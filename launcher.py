import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import imageio_ffmpeg
import yt_dlp
from yt_dlp.postprocessor.ffmpeg import FFmpegVideoConvertorPP, FFmpegVideoRemuxerPP

HOST = "127.0.0.1"
DEFAULT_PORT = int(os.environ.get("PORT", "3000"))
MAX_BODY_SIZE = 8192
MAX_OUTPUT_SIZE = 40000
DOWNLOAD_TYPES = {"video", "mp3"}
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}

_job_lock = threading.Lock()
_active_job = None
_ffmpeg_info = {
    "status": "checking",
    "message": "FFmpeg kontrol ediliyor...",
    "path": None,
}

VIDEO_DURATION_THRESHOLD = 10 * 60
VIDEO_SIZE_THRESHOLD = 1024 * 1024 * 1024


def application_directory():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def public_directory():
    bundle_directory = getattr(sys, "_MEIPASS", None)
    if bundle_directory:
        return Path(bundle_directory) / "public"
    return Path(__file__).resolve().parent / "public"


def verify_ffmpeg(executable):
    result = subprocess.run(
        [str(executable), "-version"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(details or "FFmpeg sürüm kontrolü başarısız oldu.")


def find_ffmpeg():
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        try:
            verify_ffmpeg(system_ffmpeg)
            return system_ffmpeg, "FFmpeg sistemde bulundu ve çalışıyor."
        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
            logging.warning("Sistemde bulunan FFmpeg kullanılamadı: %s", error)

    bundled_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    if not os.path.isfile(bundled_ffmpeg):
        raise FileNotFoundError("Uygulamayla gelen FFmpeg dosyası bulunamadı.")
    verify_ffmpeg(bundled_ffmpeg)
    return bundled_ffmpeg, "Sistemde FFmpeg yok; uygulamayla gelen FFmpeg hazır."


def append_output(job, text):
    with _job_lock:
        job["output"] = (job["output"] + str(text))[-MAX_OUTPUT_SIZE:]


def is_large_video(info):
    duration = info.get("duration")
    if isinstance(duration, (int, float)) and duration >= VIDEO_DURATION_THRESHOLD:
        return True

    sizes = []
    for key in ("filesize", "filesize_approx"):
        size = info.get(key)
        if isinstance(size, (int, float)):
            sizes.append(size)
    for video_format in info.get("formats", []):
        for key in ("filesize", "filesize_approx"):
            size = video_format.get(key)
            if isinstance(size, (int, float)):
                sizes.append(size)
    return any(size >= VIDEO_SIZE_THRESHOLD for size in sizes)


def create_video_format_selector(downloader, job):
    default_selector = downloader.build_format_selector("bestvideo+bestaudio/best")
    mp4_selector = downloader.build_format_selector(
        "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
    )

    def select_format(context):
        if not job["large_video"]:
            job["direct_mp4"] = False
            return default_selector(context)
        try:
            selected_formats = list(mp4_selector(context))
        except yt_dlp.utils.ExtractorError:
            selected_formats = []
        if selected_formats:
            job["direct_mp4"] = True
            return selected_formats
        job["direct_mp4"] = False
        return default_selector(context)

    return select_format


class ConditionalVideoRemuxerPP(FFmpegVideoRemuxerPP):
    def __init__(self, downloader, job):
        super().__init__(downloader, preferedformat="mkv")
        self.job = job

    def run(self, info):
        if self.job["direct_mp4"]:
            append_output(self.job, "Uyumlu MP4 akışı bulundu; yeniden kodlama atlanıyor.\n")
            return [], info
        return super().run(info)


class ConditionalVideoConvertorPP(FFmpegVideoConvertorPP):
    def __init__(self, downloader, job):
        super().__init__(downloader, preferedformat="mp4")
        self.job = job

    def run(self, info):
        if self.job["direct_mp4"]:
            return [], info
        return super().run(info)


def is_youtube_url(url):
    hostname = (urlparse(url).hostname or "").lower().rstrip(".")
    return hostname == "youtube.com" or hostname.endswith(".youtube.com") or hostname == "youtu.be"


class DownloadLogger:
    def __init__(self, job):
        self.job = job

    def debug(self, message):
        if not message.startswith("[debug] "):
            append_output(self.job, f"{message}\n")

    def info(self, message):
        append_output(self.job, f"{message}\n")

    def warning(self, message):
        append_output(self.job, f"Uyarı: {message}\n")

    def error(self, message):
        append_output(self.job, f"Hata: {message}\n")


def download_video(url, job):
    output_directory = application_directory() / "Ultra_HD_videolar"

    def update_progress(data):
        status = data.get("status")
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        downloaded = data.get("downloaded_bytes", 0)
        percent = round(downloaded * 100 / total, 1) if total and status != "finished" else None
        if status == "finished":
            stage = "İndirme tamamlandı; dosyalar birleştiriliyor..."
        else:
            stage = "Video indiriliyor..." if job["download_type"] == "video" else "Ses indiriliyor..."
        with _job_lock:
            job["progress"] = {
                "stage": stage,
                "percent": percent,
                "downloaded_bytes": downloaded,
                "total_bytes": total,
                "speed": data.get("speed"),
                "eta": data.get("eta"),
                "filename": os.path.basename(data.get("filename") or ""),
                "indeterminate": not total or status == "finished",
            }

    def update_postprocessor_progress(data):
        postprocessor = data.get("postprocessor", "")
        if data.get("status") not in ("started", "processing"):
            return
        if "VideoConvertor" in postprocessor:
            stage = "Video MP4'e dönüştürülüyor; bu aşama videonun uzunluğuna bağlı..."
        elif "ExtractAudio" in postprocessor:
            stage = "MP3 ses dosyası oluşturuluyor..."
        else:
            stage = "Ses ve görüntü birleştiriliyor..."
        with _job_lock:
            progress = dict(job["progress"])
            progress.update({"stage": stage, "percent": None, "indeterminate": True})
            job["progress"] = progress

    def classify_video(info, *, incomplete=False):
        del incomplete
        is_large = is_large_video(info)
        with _job_lock:
            job["large_video"] = is_large
            job["direct_mp4"] = False
            if is_large:
                job["progress"] = {
                    "stage": "Uzun/büyük video için MP4 akışı aranıyor...",
                    "percent": None,
                    "downloaded_bytes": 0,
                    "total_bytes": None,
                    "speed": None,
                    "eta": None,
                    "filename": "",
                    "indeterminate": True,
                }
        return None

    try:
        output_directory.mkdir(parents=True, exist_ok=True)
        options = {
            "ffmpeg_location": _ffmpeg_info["path"],
            "quiet": True,
            "logger": DownloadLogger(job),
            "progress_hooks": [update_progress],
            "postprocessor_hooks": [update_postprocessor_progress],
        }
        node_path = shutil.which("node")
        if node_path:
            options["js_runtimes"] = {"node": {"path": node_path}}
        if job["use_chrome_cookies"]:
            options["cookiesfrombrowser"] = ("chrome",)
        if job["download_type"] == "mp3":
            options.update(
                {
                    "format": "bestaudio/best",
                    "outtmpl": str(output_directory / "%(title)s.%(ext)s"),
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "0",
                        }
                    ],
                }
            )
        else:
            options.update(
                {
                    "format": "bestvideo+bestaudio/best",
                    "match_filter": classify_video,
                    "merge_output_format": "mp4",
                    "outtmpl": str(output_directory / "%(title)s_UltraHD.%(ext)s"),
                    "postprocessor_args": {
                        "VideoConvertor+ffmpeg": [
                            "-c:v", "libx264",
                            "-preset", "medium",
                            "-crf", "18",
                            "-pix_fmt", "yuv420p",
                            "-c:a", "aac",
                            "-b:a", "320k",
                        ],
                    },
                }
            )
        with yt_dlp.YoutubeDL(options) as downloader:
            if job["download_type"] == "video":
                selector = create_video_format_selector(downloader, job)
                downloader.params["format"] = selector
                downloader.format_selector = selector
                downloader.add_post_processor(ConditionalVideoRemuxerPP(downloader, job), when="post_process")
                downloader.add_post_processor(ConditionalVideoConvertorPP(downloader, job), when="post_process")
            result = downloader.download([url])
        if result:
            raise RuntimeError(f"yt-dlp işlemi {result} koduyla tamamlandı.")
        file_type = "MP3 ses dosyası" if job["download_type"] == "mp3" else "Video"
        append_output(job, f"\n{file_type} '{output_directory.name}' klasörüne kaydedildi.\n")
        with _job_lock:
            job["status"] = "completed"
    except Exception as error:
        append_output(job, f"\nİndirme sırasında bir hata oluştu: {error}\n")
        with _job_lock:
            job["status"] = "failed"


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "SDown"

    def log_message(self, _format, *_args):
        return

    def send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/status":
            with _job_lock:
                job = dict(_active_job) if _active_job else None
            self.send_json(200, {"job": job, "ffmpeg": dict(_ffmpeg_info)})
            return

        static_file = STATIC_FILES.get(parsed_path.path)
        if static_file is None:
            self.send_json(404, {"error": "Sayfa bulunamadı."})
            return

        file_name, content_type = static_file
        try:
            content = (public_directory() / file_name).read_bytes()
        except OSError:
            logging.exception("Arayüz dosyası okunamadı: %s", file_name)
            self.send_json(500, {"error": "Arayüz dosyası okunamadı."})
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        global _active_job

        if urlparse(self.path).path != "/api/download":
            self.send_json(404, {"error": "Sayfa bulunamadı."})
            return

        if _ffmpeg_info["status"] != "ready":
            self.send_json(503, {"error": "FFmpeg hazır değil."})
            return

        try:
            body_size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_json(400, {"error": "Geçerli bir bağlantı girin."})
            return
        if body_size < 1 or body_size > MAX_BODY_SIZE:
            self.send_json(413, {"error": "İstek gövdesi geçersiz veya çok büyük."})
            return

        try:
            request_data = json.loads(self.rfile.read(body_size))
            url = request_data.get("url")
            download_type = request_data.get("download_type", "video")
            use_chrome_cookies = request_data.get("use_chrome_cookies", False)
        except (json.JSONDecodeError, AttributeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Geçerli bir bağlantı girin."})
            return

        if not isinstance(url, str):
            self.send_json(400, {"error": "Geçerli bir bağlantı girin."})
            return
        if not isinstance(download_type, str) or download_type not in DOWNLOAD_TYPES:
            self.send_json(400, {"error": "İndirme türü video veya mp3 olmalıdır."})
            return
        if not isinstance(use_chrome_cookies, bool):
            self.send_json(400, {"error": "Chrome çerez seçimi geçersiz."})
            return

        parsed_url = urlparse(url.strip())
        if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
            self.send_json(400, {"error": "Geçerli bir http veya https bağlantısı girin."})
            return
        use_chrome_cookies = use_chrome_cookies and is_youtube_url(parsed_url.geturl())

        with _job_lock:
            if _active_job and _active_job["status"] == "running":
                self.send_json(409, {"error": "Devam eden bir indirme zaten var."})
                return
            job = {
                "id": str(threading.get_ident()) + "-" + str(threading.get_native_id()),
                "status": "running",
                "download_type": download_type,
                "use_chrome_cookies": use_chrome_cookies,
                "output": "",
                "large_video": False,
                "direct_mp4": False,
                "progress": {
                    "stage": "Video bilgileri alınıyor...",
                    "percent": None,
                    "downloaded_bytes": 0,
                    "total_bytes": None,
                    "speed": None,
                    "eta": None,
                    "filename": "",
                    "indeterminate": True,
                },
            }
            _active_job = job

        thread = threading.Thread(
            target=download_video,
            args=(parsed_url.geturl(), job),
            daemon=True,
        )
        thread.start()
        self.send_json(202, job)


def main():
    global _ffmpeg_info

    logging.basicConfig(level=logging.WARNING)
    try:
        executable, message = find_ffmpeg()
        _ffmpeg_info = {"status": "ready", "message": message, "path": executable}
    except (OSError, subprocess.SubprocessError, RuntimeError) as error:
        logging.exception("FFmpeg doğrulanamadı.")
        _ffmpeg_info = {"status": "error", "message": str(error), "path": None}

    try:
        server = ThreadingHTTPServer((HOST, DEFAULT_PORT), RequestHandler)
    except OSError:
        logging.exception("Varsayılan yerel port %s kullanılamıyor; boş port deneniyor.", DEFAULT_PORT)
        server = ThreadingHTTPServer((HOST, 0), RequestHandler)
    server.daemon_threads = True
    address = f"http://{HOST}:{server.server_address[1]}"
    print(f"SDown arayüzü hazır: {address}")
    if os.environ.get("SDOWN_NO_BROWSER") != "1":
        webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
