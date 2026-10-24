import os
import yt_dlp

VIDEO_POSTPROCESSORS = [
    {"key": "FFmpegVideoRemuxer", "preferedformat": "mkv"},
    {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
]
VIDEO_POSTPROCESSOR_ARGS = {
    "VideoConvertor+ffmpeg": [
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
    ],
}


def ultra_hd_indir(tiktok_url):
    kayit_klasoru = "Ultra_HD_videolar"
    if not os.path.exists(kayit_klasoru):
        os.makedirs(kayit_klasoru)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(kayit_klasoru, '%(title)s_UltraHD.%(ext)s'),
        'postprocessors': VIDEO_POSTPROCESSORS,
        'postprocessor_args': VIDEO_POSTPROCESSOR_ARGS,
        'quiet': False
    }

    try:
        print("indiriliyor...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tiktok_url])
        print(f"\nvideo '{kayit_klasoru}' klasörüne kaydedildi")
    except Exception as e:
        print(f"İndirme sırasında bir hata oluştu: {e}")

if __name__ == "__main__":
    url = input("link gir tt ig farketmez:  ")
    ultra_hd_indir(url)
