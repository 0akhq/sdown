import json
import ipaddress
import logging
import os
import re
import shutil
import subprocess
import sys
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, urlsplit

import imageio_ffmpeg

try:
    import yt_dlp
    from yt_dlp.postprocessor import ffmpeg as yt_dlp_ffmpeg
    from yt_dlp.postprocessor.ffmpeg import FFmpegVideoConvertorPP, FFmpegVideoRemuxerPP
except ImportError as error:
    yt_dlp = None
    yt_dlp_ffmpeg = None
    FFmpegVideoConvertorPP = object
    FFmpegVideoRemuxerPP = object
    _yt_dlp_import_error = error
else:
    _yt_dlp_import_error = None

HOST = "127.0.0.1"
FALLBACK_PORT = 3000
DEFAULT_PORT = FALLBACK_PORT
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
_active_runtime = None
_active_download_thread = None
_ffmpeg_info = {
    "status": "checking",
    "message": "FFmpeg kontrol ediliyor...",
    "path": None,
}

VIDEO_DURATION_THRESHOLD = 10 * 60
VIDEO_SIZE_THRESHOLD = 1024 * 1024 * 1024


def parse_port(value):
    if value is None:
        return FALLBACK_PORT, None

    raw_port = value.strip()
    if not re.fullmatch(r"[+-]?[0-9]+", raw_port):
        return FALLBACK_PORT, "PORT sayısal değil; varsayılan 3000 portu kullanılacak."
    if len(raw_port.lstrip("+-").lstrip("0") or "0") > 5:
        return FALLBACK_PORT, "PORT 0 ile 65535 arasında olmalıdır; varsayılan 3000 portu kullanılacak."
    port = int(raw_port)
    if not 0 <= port <= 65535:
        return FALLBACK_PORT, "PORT 0 ile 65535 arasında olmalıdır; varsayılan 3000 portu kullanılacak."
    return port, None


DEFAULT_PORT, PORT_CONFIGURATION_WARNING = parse_port(os.environ.get("PORT"))


def validate_download_url(value):
    if not isinstance(value, str):
        raise ValueError("URL metin olmalıdır.")
    url = value.strip()
    if not url or any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in url):
        raise ValueError("URL boşluk veya kontrol karakteri içeremez.")

    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise ValueError("URL biçimi veya portu geçersiz.") from error

    if parsed.scheme not in ("http", "https") or not parsed.netloc or not hostname:
        raise ValueError("Yalnızca geçerli bir http veya https URL'si kabul edilir.")
    if "@" in parsed.netloc or "\\" in parsed.netloc:
        raise ValueError("URL kullanıcı adı veya parola bilgisi içeremez.")

    authority = parsed.netloc
    if authority.startswith("["):
        closing_bracket = authority.find("]")
        if closing_bracket < 0:
            raise ValueError("URL host bilgisi geçersiz.")
        suffix = authority[closing_bracket + 1:]
        if suffix and (
            not suffix.startswith(":")
            or not re.fullmatch(r"[0-9]+", suffix[1:])
        ):
            raise ValueError("URL portu geçersiz.")
        try:
            ipaddress.IPv6Address(hostname)
        except ipaddress.AddressValueError as error:
            raise ValueError("URL IPv6 host bilgisi geçersiz.") from error
    else:
        if authority.count(":") > 1:
            raise ValueError("IPv6 host adresleri köşeli parantez içinde olmalıdır.")
        if ":" in authority and not re.fullmatch(r"[0-9]+", authority.rsplit(":", 1)[1]):
            raise ValueError("URL portu geçersiz.")
        if ":" in hostname:
            raise ValueError("URL host bilgisi geçersiz.")
        try:
            ascii_hostname = hostname.rstrip(".").encode("idna").decode("ascii")
        except UnicodeError as error:
            raise ValueError("URL host bilgisi geçersiz.") from error
        labels = ascii_hostname.split(".")
        if (
            not ascii_hostname
            or len(ascii_hostname) > 253
            or any(
                not label
                or len(label) > 63
                or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
                for label in labels
            )
        ):
            raise ValueError("URL host bilgisi geçersiz.")
        if len(labels) == 4 and all(label.isdigit() for label in labels):
            try:
                ipaddress.IPv4Address(ascii_hostname)
            except ipaddress.AddressValueError as error:
                raise ValueError("URL IPv4 host bilgisi geçersiz.") from error

    if port is not None and not 1 <= port <= 65535:
        raise ValueError("URL portu 1 ile 65535 arasında olmalıdır.")
    return parsed.geturl()


_URL_CREDENTIALS_PATTERN = re.compile(r"(?i)(https?://)[^/\s?#@]+@")
_SENSITIVE_QUERY_PATTERN = re.compile(
    r"(?i)([?&#](?:access_token|auth_token|refresh_token|token|auth|authorization|password|passwd|secret|api[_-]?key|key|signature|sig|cookie|session(?:id)?|sid)=)[^&#\s]+"
)
_SENSITIVE_HEADER_PATTERN = re.compile(
    r"(?i)(\b(?:cookie|set-cookie|authorization|proxy-authorization)\s*:\s*)[^\r\n]*"
)
_SENSITIVE_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)(\b(?:access_token|auth_token|refresh_token|token|password|passwd|secret|api[_-]?key|authorization|cookie|session(?:id)?|sid)\b\s*[:=]\s*)[^,&\s;]+"
)


def sanitize_sensitive_text(value):
    text = str(value)
    text = _URL_CREDENTIALS_PATTERN.sub(r"\1[REDACTED]@", text)
    text = _SENSITIVE_QUERY_PATTERN.sub(r"\1[REDACTED]", text)
    text = _SENSITIVE_HEADER_PATTERN.sub(r"\1[REDACTED]", text)
    return _SENSITIVE_ASSIGNMENT_PATTERN.sub(r"\1[REDACTED]", text)


def friendly_download_error(error):
    message = sanitize_sensitive_text(error)
    lowered = message.lower()
    postprocessing_error = getattr(getattr(yt_dlp, "utils", None), "PostProcessingError", ())

    if (
        isinstance(error, postprocessing_error)
        or "ffmpeg" in lowered
        or "postprocessing" in lowered
        or "post-processing" in lowered
    ):
        return "FFmpeg işlemi başarısız oldu. Disk alanını ve FFmpeg hata ayrıntılarını kontrol edin."
    if any(term in lowered for term in ("sign in", "login", "authentication", "http error 401", "http error 403", "private video", "members-only", "cookies")):
        return "Kaynak erişim veya oturum gerektiriyor ya da isteği reddetti. Erişim yetkinizi ve gerekli oturum ayarlarını kontrol edin."
    if any(term in lowered for term in ("unsupported url", "no suitable extractor", "unsupported site", "not a valid url", "requested format is not available", "no video formats found")):
        return "Bu bağlantı veya medya biçimi desteklenmiyor. Bağlantının herkese açık ve doğru olduğunu kontrol edin."
    if any(term in lowered for term in ("timed out", "timeout", "connection", "name resolution", "network is unreachable", "unable to download webpage", "http error 429", "http error 5")):
        return "Ağ bağlantısı veya kaynak sunucu nedeniyle indirme tamamlanamadı. İnternet bağlantınızı kontrol edip tekrar deneyin."
    return "İndirme tamamlanamadı. Bağlantıyı ve işlem ayrıntılarını kontrol edip tekrar deneyin."


class DownloadRuntime:
    def __init__(self):
        self.cancel_event = threading.Event()
        self.cancel_lock = threading.Lock()
        self.process_lock = threading.Lock()
        self.processes = set()


def cancel_download_processes(runtime):
    with runtime.cancel_lock:
        runtime.cancel_event.set()
        with runtime.process_lock:
            processes = tuple(runtime.processes)

        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                    process.wait(timeout=3)
                except (OSError, subprocess.SubprocessError):
                    logging.exception("İndirme alt süreci zorla sonlandırılamadı.")
            except OSError:
                if process.poll() is None:
                    logging.exception("İndirme alt süreci sonlandırılamadı.")


_download_context = threading.local()


if yt_dlp is not None:
    class CancellablePopen(yt_dlp.utils.Popen):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            runtime = getattr(_download_context, "runtime", None)
            self._download_runtime = runtime
            if runtime is None:
                return
            with runtime.process_lock:
                runtime.processes.add(self)
                cancelled = runtime.cancel_event.is_set()
            if cancelled:
                try:
                    self.kill()
                except OSError:
                    if self.poll() is None:
                        raise

        def communicate_or_kill(self, *args, **kwargs):
            try:
                return super().communicate_or_kill(*args, **kwargs)
            finally:
                runtime = self._download_runtime
                if runtime is not None:
                    with runtime.process_lock:
                        runtime.processes.discard(self)


    yt_dlp_ffmpeg.Popen = CancellablePopen


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


def show_startup_error(message):
    if sys.stderr is not None:
        print(message, file=sys.stderr)
    if os.name == "nt" and Path(sys.executable).name.lower() == "pythonw.exe":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(None, message, "SDown", 0x10)
        except (AttributeError, OSError):
            logging.exception("Başlangıç hata penceresi gösterilemedi.")


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


def is_trusted_local_request(headers, server_address, *, require_origin=False):
    expected_host = f"{HOST}:{server_address[1]}"
    if headers.get("Host") != expected_host:
        return False
    if require_origin and headers.get("Origin") != f"http://{expected_host}":
        return False
    return True


class DownloadLogger:
    def __init__(self, job):
        self.job = job

    def debug(self, message):
        safe_message = sanitize_sensitive_text(message)
        if not safe_message.startswith("[debug] "):
            append_output(self.job, f"{safe_message}\n")

    def info(self, message):
        append_output(self.job, f"{sanitize_sensitive_text(message)}\n")

    def warning(self, message):
        append_output(self.job, f"Uyarı: {sanitize_sensitive_text(message)}\n")

    def error(self, message):
        append_output(self.job, f"Hata: {sanitize_sensitive_text(message)}\n")


def download_video(url, job, runtime):
    output_directory = application_directory() / "Ultra_HD_videolar"

    def update_progress(data):
        if runtime.cancel_event.is_set():
            raise yt_dlp.utils.DownloadError("İndirme iptal edildi.")
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
        _download_context.runtime = runtime
        try:
            with yt_dlp.YoutubeDL(options) as downloader:
                if job["download_type"] == "video":
                    selector = create_video_format_selector(downloader, job)
                    downloader.params["format"] = selector
                    downloader.format_selector = selector
                    downloader.add_post_processor(ConditionalVideoRemuxerPP(downloader, job), when="post_process")
                    downloader.add_post_processor(ConditionalVideoConvertorPP(downloader, job), when="post_process")
                result = downloader.download([url])
        finally:
            _download_context.runtime = None
        if runtime.cancel_event.is_set():
            with _job_lock:
                job["status"] = "cancelled"
            append_output(job, "\nİndirme iptal edildi.\n")
            return
        if result:
            raise RuntimeError(f"yt-dlp işlemi {result} koduyla tamamlandı.")
        file_type = "MP3 ses dosyası" if job["download_type"] == "mp3" else "Video"
        append_output(job, f"\n{file_type} '{output_directory.name}' klasörüne kaydedildi.\n")
        with _job_lock:
            job["status"] = "completed"
    except Exception as error:
        if runtime.cancel_event.is_set():
            append_output(job, "\nİndirme iptal edildi.\n")
            final_status = "cancelled"
        else:
            logging.error("İndirme başarısız oldu:\n%s", sanitize_sensitive_text(traceback.format_exc()))
            append_output(job, f"\n{friendly_download_error(error)}\n")
            final_status = "failed"
        with _job_lock:
            job["status"] = final_status


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
        if not is_trusted_local_request(self.headers, self.server.server_address):
            self.send_json(403, {"error": "İstek SDown yerel arayüzünden gelmelidir."})
            return

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
        global _active_download_thread
        global _active_job, _active_runtime

        if not is_trusted_local_request(
            self.headers,
            self.server.server_address,
            require_origin=True,
        ):
            self.send_json(403, {"error": "İstek SDown yerel arayüzünden gelmelidir."})
            return

        request_path = urlparse(self.path).path
        if request_path == "/api/cancel":
            with _job_lock:
                job = _active_job
                runtime = _active_runtime
                if not job or job["status"] != "running" or runtime is None:
                    self.send_json(409, {"error": "İptal edilebilecek etkin bir indirme yok."})
                    return
                job["status"] = "cancelling"
            cancel_download_processes(runtime)
            with _job_lock:
                cancelled_job = dict(job)
            self.send_json(202, {"job": cancelled_job})
            return

        if request_path == "/api/shutdown":
            with _job_lock:
                job = _active_job
                runtime = _active_runtime
                download_thread = _active_download_thread
                if job and job["status"] == "running" and runtime is not None:
                    job["status"] = "cancelling"
            if runtime is not None and download_thread is not None and download_thread.is_alive():
                cancel_download_processes(runtime)
            self.send_json(202, {"message": "SDown kapatılıyor."})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return

        if request_path != "/api/download":
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

        if not isinstance(download_type, str) or download_type not in DOWNLOAD_TYPES:
            self.send_json(400, {"error": "İndirme türü video veya mp3 olmalıdır."})
            return
        if not isinstance(use_chrome_cookies, bool):
            self.send_json(400, {"error": "Chrome çerez seçimi geçersiz."})
            return

        try:
            url = validate_download_url(url)
        except ValueError:
            self.send_json(400, {"error": "Geçerli bir http veya https bağlantısı girin."})
            return
        use_chrome_cookies = use_chrome_cookies and is_youtube_url(url)

        with _job_lock:
            if _active_job and _active_job["status"] == "running":
                self.send_json(409, {"error": "Devam eden bir indirme zaten var."})
                return
            runtime = DownloadRuntime()
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
            _active_runtime = runtime

        _active_download_thread = threading.Thread(
            target=download_video,
            args=(url, job, runtime),
            daemon=True,
        )
        _active_download_thread.start()
        self.send_json(202, job)


def main():
    global _ffmpeg_info

    logging.basicConfig(level=logging.WARNING)
    if PORT_CONFIGURATION_WARNING:
        logging.warning(PORT_CONFIGURATION_WARNING)
    if yt_dlp is None:
        message = "yt-dlp bulunamadı. Kurmak için: python -m pip install yt-dlp"
        logging.error("yt-dlp içe aktarılamadı: %s", _yt_dlp_import_error)
        show_startup_error(message)
        return 1

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
        with _job_lock:
            runtime = _active_runtime
            download_thread = _active_download_thread
            if _active_job and _active_job["status"] == "running":
                _active_job["status"] = "cancelling"
        if runtime is not None and download_thread is not None and download_thread.is_alive():
            cancel_download_processes(runtime)
            download_thread.join(timeout=8)
            if download_thread.is_alive():
                logging.error("İndirme iş parçacığı kapanış zaman aşımında hâlâ çalışıyor.")
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
