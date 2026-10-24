const form = document.querySelector("#download-form");
const input = document.querySelector("#video-url");
const downloadType = document.querySelector("#download-type");
const chromeCookies = document.querySelector("#use-chrome-cookies");
const languageSelect = document.querySelector("#language-select");
const button = document.querySelector("#download-button");
const panel = document.querySelector("#job-panel");
const title = document.querySelector("#job-title");
const description = document.querySelector("#job-description");
const status = document.querySelector("#job-status");
const output = document.querySelector("#job-output");
const progressTrack = document.querySelector("#progress-track");
const progressBar = document.querySelector("#progress-bar");
const progressStage = document.querySelector("#progress-stage");
const progressPercent = document.querySelector("#progress-percent");
const progressTransferred = document.querySelector("#progress-transferred");
const progressSpeed = document.querySelector("#progress-speed");
const progressEta = document.querySelector("#progress-eta");
const progressFile = document.querySelector("#progress-file");
const ffmpegStatus = document.querySelector("#ffmpeg-status");

const messages = {
  en: {
    languageLabel: "Language",
    brandHome: "SDown home",
    heroTitle: "Quality videos.<br><span>Quality software.</span>",
    heroCopy: "Developed by 0akh.",
    downloadForm: "Video download form",
    videoUrlLabel: "VIDEO URL",
    urlPlaceholder: "https://www.tiktok.com/...",
    startDownload: "Start download",
    downloadType: "DOWNLOAD TYPE",
    videoMp4: "Video · MP4",
    audioMp3: "Audio · MP3",
    chromeCookies: "Use Chrome session for YouTube",
    chromeHint: "Chrome session is used only when checked. Keep Chrome closed during the download.",
    ffmpegChecking: "Checking FFmpeg...",
    preparingDownload: "Preparing download",
    processingLink: "Processing link, please wait.",
    starting: "STARTING",
    readingVideoInfo: "Getting video information...",
    waiting: "Waiting",
    downloadProgress: "Download progress",
    waitingForSize: "0 B / waiting for size",
    calculatingTime: "Calculating time remaining",
    processDetails: "Process details",
    qualityNote: "The best available quality is downloaded as MP4.",
    platformGuide: "PLATFORM GUIDE",
    platformTitle: "Media you may be able to download",
    platformDisclaimer: "Availability depends on yt-dlp support, access permissions, and platform changes.",
    socialPlatforms: "Social Media Platforms",
    instagramDesc: "Reels, IGTV, post videos, and stories.",
    tiktokDesc: "Short-form videos, audio, and user profiles.",
    xDesc: "Videos and GIFs posted on X.",
    facebookDesc: "Page and group videos, Facebook Watch, and Reels.",
    redditDesc: "Videos embedded in posts, v.redd.it links, and merged audio/video.",
    linkedinDesc: "Professional and personal videos shared in posts.",
    pinterestDesc: "Animated videos and idea pins.",
    snapchatDesc: "Spotlight videos and public stories.",
    videoPlatforms: "Video and Streaming Platforms",
    youtubeDesc: "Videos, Shorts, playlists, channels, live-stream recordings, and YouTube Music.",
    twitchDesc: "Live streams, past broadcasts (VODs), and clips.",
    kickDesc: "Live streams and recordings of past streams.",
    vimeoDesc: "Public videos, albums, and unprotected portfolio content.",
    dailymotionDesc: "Channels, playlists, and videos.",
    audioPlatforms: "Music and Audio Platforms",
    soundcloudDesc: "Tracks, albums, playlists, and artist profiles.",
    bandcampDesc: "Albums, individual tracks, and discographies.",
    mixcloudDesc: "Radio shows, DJ mixes, and podcasts.",
    spotifyDesc: "Public podcast episodes; music tracks are not directly downloaded because of copyright protection.",
    filmPlatforms: "Film, Series, and Anime Platforms (Non-DRM Content)",
    crunchyrollDesc: "Anime episodes and series (may require membership or be region-restricted).",
    bilibiliDesc: "Anime, gaming, and community videos from China.",
    "9gagDesc": "Videos and GIFs posted on the platform.",
    newsEducation: "News and Education",
    newsDesc: "International news videos and live streams.",
    tedDesc: "Talks, presentations, and conference recordings.",
    udemyDesc: "Course videos you have purchased or that are free (account access/cookies may be required).",
    footerTagline: "Local video downloader",
    footerLocation: "Files are saved in the <code>Ultra_HD_videolar</code> folder beside the app.",
    runningVideoTitle: "Downloading video",
    runningAudioTitle: "Downloading audio as MP3",
    runningDescription: "Keep this page open until the download is complete.",
    completedTitle: "Download complete",
    completedVideoDescription: "Your file was saved to the Ultra_HD_videolar folder.",
    completedAudioDescription: "Your MP3 was saved to the Ultra_HD_videolar folder.",
    failedTitle: "Download failed",
    failedDescription: "Check the process output for details.",
    runningStatus: "IN PROGRESS",
    completedStatus: "COMPLETED",
    failedStatus: "ERROR",
    preparingPython: "Starting the Python process...",
    downloadPreparing: "Preparing download",
    ffmpegNotReady: "FFmpeg is not ready",
    ffmpegRequired: "The FFmpeg check must succeed before downloading.",
    startError: "Could not start the download.",
    startingButton: "Starting...",
    newDownload: "New download",
    retry: "Try again",
    serverDisconnected: "Connection to the server was lost. Check that the app is running.",
    serverUnavailable: "Could not connect to the application server.",
    downloadStarted: "Download started",
    downloadFinished: "Download complete.",
    downloadFailed: "The operation could not be completed.",
    videoInfo: "Getting video information...",
    lookingForMp4: "Looking for MP4 streams for a long/large video...",
    downloadingVideo: "Downloading video...",
    downloadingAudio: "Downloading audio...",
    mergingFiles: "Download complete; merging files...",
    convertingVideo: "Converting video to MP4; this may take as long as the video...",
    creatingMp3: "Creating MP3 audio file...",
    mergingAudioVideo: "Merging audio and video...",
    transferred: "{size} downloaded",
    waitingForTotal: "Waiting for total size",
    remaining: "Remaining: {duration}",
    calculating: "Calculating time remaining",
    durationHours: "{hours} hr {minutes} min",
    durationMinutes: "{minutes} min {seconds} sec",
    durationSeconds: "{seconds} sec",
    ffmpegSystemReady: "FFmpeg was found and is working on your system.",
    ffmpegBundledReady: "System FFmpeg not found; bundled FFmpeg is ready.",
    ffmpegMissing: "Bundled FFmpeg executable was not found.",
    invalidUrl: "Enter a valid http or https URL.",
    downloadAlreadyRunning: "A download is already in progress.",
    ffmpegServerNotReady: "FFmpeg is not ready.",
    compatibleMp4: "Compatible MP4 stream found; skipping re-encoding.",
    savedVideo: "Video saved to the '{folder}' folder.",
    savedAudio: "MP3 audio saved to the '{folder}' folder.",
  },
  tr: {
    languageLabel: "Dil",
    brandHome: "SDown ana sayfa",
    heroTitle: "Kaliteli Videoları.<br><span>Kaliteli yazılımlar yükler.</span>",
    heroCopy: "0akh tarafından geliştirilmiştir.",
    downloadForm: "Video indirme formu",
    videoUrlLabel: "VİDEO BAĞLANTISI",
    urlPlaceholder: "https://www.tiktok.com/...",
    startDownload: "İndirmeyi başlat",
    downloadType: "İNDİRME TÜRÜ",
    videoMp4: "Video · MP4",
    audioMp3: "Ses · MP3",
    chromeCookies: "YouTube için Chrome oturumunu kullan",
    chromeHint: "Chrome oturumu yalnızca işaretlendiğinde kullanılır. İndirme sırasında Chrome'u kapalı tutun.",
    ffmpegChecking: "FFmpeg kontrol ediliyor...",
    preparingDownload: "İndirme hazırlanıyor",
    processingLink: "Bağlantı işleniyor, lütfen bekle.",
    starting: "BAŞLATILIYOR",
    readingVideoInfo: "Video bilgileri alınıyor...",
    waiting: "Bekleniyor",
    downloadProgress: "İndirme ilerlemesi",
    waitingForSize: "0 B / Boyut bekleniyor",
    calculatingTime: "Kalan süre hesaplanıyor",
    processDetails: "İşlem ayrıntıları",
    qualityNote: "En iyi kullanılabilir kalite MP4 olarak indirilir.",
    platformGuide: "PLATFORM REHBERİ",
    platformTitle: "Bu yazılımdan indirebileceğiniz videolar",
    platformDisclaimer: "Gerçek kullanılabilirlik yt-dlp desteğine, erişim durumuna ve platform değişikliklerine bağlıdır.",
    socialPlatforms: "Sosyal Medya Platformları",
    instagramDesc: "Reels videoları, IGTV, gönderi videoları ve hikayeler (story).",
    tiktokDesc: "Kısa videolar, sesler ve kullanıcı profilleri.",
    xDesc: "X gönderilerine yüklenen videolar ve GIF'ler.",
    facebookDesc: "Sayfa ve grup videoları, Facebook Watch ve Reels.",
    redditDesc: "Gönderilere gömülü videolar, v.redd.it bağlantıları ve ses-görüntü birleştirmeleri.",
    linkedinDesc: "Gönderilerde paylaşılan kurumsal ve kişisel videolar.",
    pinterestDesc: "Pin olarak yüklenmiş hareketli videolar ve fikir pinleri.",
    snapchatDesc: "Spotlight videoları ve herkese açık hikayeler.",
    videoPlatforms: "Video Paylaşım ve Yayın Platformları",
    youtubeDesc: "Standart videolar, Shorts, oynatma listeleri, kanallar, canlı yayın kayıtları ve YouTube Music.",
    twitchDesc: "Canlı yayınlar, geçmiş yayın kayıtları (VOD) ve klipler.",
    kickDesc: "Canlı yayınlar ve geçmiş yayın kayıtları.",
    vimeoDesc: "Herkese açık videolar, albümler ve korumasız portfolyo içerikleri.",
    dailymotionDesc: "Kanallar, çalma listeleri ve videolar.",
    audioPlatforms: "Müzik ve Ses Platformları",
    soundcloudDesc: "Şarkılar, albümler, çalma listeleri ve sanatçı profilleri.",
    bandcampDesc: "Albümler, tekli şarkılar ve diskografiler.",
    mixcloudDesc: "Radyo programları, DJ miksleri ve podcast'ler.",
    spotifyDesc: "Herkese açık podcast bölümleri; telif koruması nedeniyle müzik parçaları doğrudan indirilmez.",
    filmPlatforms: "Film, Dizi ve Anime Platformları (DRM'siz İçerikler)",
    crunchyrollDesc: "Anime bölümleri ve serileri (bölge kısıtlaması veya üyelik gerektirebilir).",
    bilibiliDesc: "Çin menşeili anime, oyun ve topluluk videoları.",
    "9gagDesc": "Platforma yüklenen videolar ve GIF'ler.",
    newsEducation: "Haber ve Eğitim Kanalları",
    newsDesc: "Uluslararası haber videoları ve canlı yayın akışları.",
    tedDesc: "Konuşmalar, sunumlar ve konferans kayıtları.",
    udemyDesc: "Satın aldığınız veya ücretsiz kurs videoları (hesap erişimi/çerez kullanımı gerekebilir).",
    footerTagline: "Yerel video indirici",
    footerLocation: "Dosyalar uygulamanın yanındaki <code>Ultra_HD_videolar</code> klasörüne kaydedilir.",
    runningVideoTitle: "Video indiriliyor",
    runningAudioTitle: "Ses MP3 olarak indiriliyor",
    runningDescription: "İndirme tamamlanana kadar bu sayfayı açık tut.",
    completedTitle: "İndirme tamamlandı",
    completedVideoDescription: "Dosyan Ultra_HD_videolar klasörüne kaydedildi.",
    completedAudioDescription: "MP3 ses dosyan Ultra_HD_videolar klasörüne kaydedildi.",
    failedTitle: "İndirme tamamlanamadı",
    failedDescription: "Ayrıntılar için işlem çıktısını kontrol et.",
    runningStatus: "İŞLENİYOR",
    completedStatus: "TAMAMLANDI",
    failedStatus: "HATA",
    preparingPython: "Python işlemi başlatılıyor...",
    downloadPreparing: "İndirme hazırlanıyor",
    ffmpegNotReady: "FFmpeg hazır değil",
    ffmpegRequired: "İndirme için FFmpeg kontrolünün başarılı olması gerekir.",
    startError: "İndirme başlatılamadı.",
    startingButton: "Başlatılıyor...",
    newDownload: "Yeni indirme",
    retry: "Tekrar dene",
    serverDisconnected: "Sunucuyla bağlantı kesildi. Uygulamanın çalıştığını kontrol et.",
    serverUnavailable: "Uygulama sunucusuna bağlanılamadı.",
    downloadStarted: "İndirme başlatıldı",
    downloadFinished: "İndirme tamamlandı.",
    downloadFailed: "İşlem tamamlanamadı.",
    videoInfo: "Video bilgileri alınıyor...",
    lookingForMp4: "Uzun/büyük video için MP4 akışı aranıyor...",
    downloadingVideo: "Video indiriliyor...",
    downloadingAudio: "Ses indiriliyor...",
    mergingFiles: "İndirme tamamlandı; dosyalar birleştiriliyor...",
    convertingVideo: "Video MP4'e dönüştürülüyor; bu aşama videonun uzunluğuna bağlı...",
    creatingMp3: "MP3 ses dosyası oluşturuluyor...",
    mergingAudioVideo: "Ses ve görüntü birleştiriliyor...",
    transferred: "{size} indirildi",
    waitingForTotal: "Toplam boyut bekleniyor",
    remaining: "Kalan: {duration}",
    calculating: "Kalan süre hesaplanıyor",
    durationHours: "{hours} sa {minutes} dk",
    durationMinutes: "{minutes} dk {seconds} sn",
    durationSeconds: "{seconds} sn",
    ffmpegSystemReady: "FFmpeg sistemde bulundu ve çalışıyor.",
    ffmpegBundledReady: "Sistemde FFmpeg yok; uygulamayla gelen FFmpeg hazır.",
    ffmpegMissing: "Uygulamayla gelen FFmpeg dosyası bulunamadı.",
    invalidUrl: "Geçerli bir http veya https bağlantısı girin.",
    downloadAlreadyRunning: "Devam eden bir indirme zaten var.",
    ffmpegServerNotReady: "FFmpeg hazır değil.",
    compatibleMp4: "Uyumlu MP4 akışı bulundu; yeniden kodlama atlanıyor.",
    savedVideo: "Video '{folder}' klasörüne kaydedildi.",
    savedAudio: "MP3 ses dosyası '{folder}' klasörüne kaydedildi.",
  },
  ru: {
    languageLabel: "Язык",
    brandHome: "Главная страница SDown",
    heroTitle: "Качественные видео.<br><span>Качественное ПО.</span>",
    heroCopy: "Разработано 0akh.",
    downloadForm: "Форма загрузки видео",
    videoUrlLabel: "ССЫЛКА НА ВИДЕО",
    urlPlaceholder: "https://www.tiktok.com/...",
    startDownload: "Начать загрузку",
    downloadType: "ТИП ЗАГРУЗКИ",
    videoMp4: "Видео · MP4",
    audioMp3: "Аудио · MP3",
    chromeCookies: "Использовать сеанс Chrome для YouTube",
    chromeHint: "Сеанс Chrome используется только при включённом флажке. Во время загрузки Chrome должен быть закрыт.",
    ffmpegChecking: "Проверка FFmpeg...",
    preparingDownload: "Подготовка загрузки",
    processingLink: "Обработка ссылки, подождите.",
    starting: "ЗАПУСК",
    readingVideoInfo: "Получение сведений о видео...",
    waiting: "Ожидание",
    downloadProgress: "Ход загрузки",
    waitingForSize: "0 Б / ожидание размера",
    calculatingTime: "Расчёт оставшегося времени",
    processDetails: "Подробности процесса",
    qualityNote: "Видео загружается в наилучшем доступном качестве MP4.",
    platformGuide: "ПОДДЕРЖИВАЕМЫЕ ПЛАТФОРМЫ",
    platformTitle: "Материалы, которые могут быть доступны для загрузки",
    platformDisclaimer: "Доступность зависит от поддержки yt-dlp, прав доступа и изменений платформ.",
    socialPlatforms: "Социальные сети",
    instagramDesc: "Reels, IGTV, видео в публикациях и истории.",
    tiktokDesc: "Короткие видео, аудио и профили пользователей.",
    xDesc: "Видео и GIF, опубликованные в X.",
    facebookDesc: "Видео страниц и групп, Facebook Watch и Reels.",
    redditDesc: "Видео в публикациях, ссылки v.redd.it и объединённые аудио/видео.",
    linkedinDesc: "Профессиональные и личные видео в публикациях.",
    pinterestDesc: "Анимированные видео и idea pins.",
    snapchatDesc: "Видео Spotlight и общедоступные истории.",
    videoPlatforms: "Видеоплатформы и стриминг",
    youtubeDesc: "Видео, Shorts, плейлисты, каналы, записи трансляций и YouTube Music.",
    twitchDesc: "Прямые трансляции, записи эфиров (VOD) и клипы.",
    kickDesc: "Прямые трансляции и записи прошедших эфиров.",
    vimeoDesc: "Общедоступные видео, альбомы и незащищённые портфолио.",
    dailymotionDesc: "Каналы, плейлисты и видео.",
    audioPlatforms: "Музыкальные и аудиоплатформы",
    soundcloudDesc: "Треки, альбомы, плейлисты и профили исполнителей.",
    bandcampDesc: "Альбомы, отдельные треки и дискографии.",
    mixcloudDesc: "Радиопередачи, DJ-миксы и подкасты.",
    spotifyDesc: "Общедоступные выпуски подкастов; музыкальные треки не загружаются напрямую из-за защиты авторских прав.",
    filmPlatforms: "Фильмы, сериалы и аниме (без DRM)",
    crunchyrollDesc: "Эпизоды и сериалы аниме (могут требоваться подписка или доступ из определённого региона).",
    bilibiliDesc: "Аниме, игры и пользовательские видео из Китая.",
    "9gagDesc": "Видео и GIF, опубликованные на платформе.",
    newsEducation: "Новости и образовательные материалы",
    newsDesc: "Международные новостные видео и прямые эфиры.",
    tedDesc: "Выступления, презентации и записи конференций.",
    udemyDesc: "Купленные или бесплатные учебные видео (может потребоваться аккаунт/cookies).",
    footerTagline: "Локальный загрузчик видео",
    footerLocation: "Файлы сохраняются в папку <code>Ultra_HD_videolar</code> рядом с приложением.",
    runningVideoTitle: "Загрузка видео",
    runningAudioTitle: "Загрузка аудио в MP3",
    runningDescription: "Не закрывайте эту страницу до завершения загрузки.",
    completedTitle: "Загрузка завершена",
    completedVideoDescription: "Файл сохранён в папку Ultra_HD_videolar.",
    completedAudioDescription: "MP3-файл сохранён в папку Ultra_HD_videolar.",
    failedTitle: "Не удалось загрузить",
    failedDescription: "Подробности смотрите в выводе процесса.",
    runningStatus: "ВЫПОЛНЯЕТСЯ",
    completedStatus: "ГОТОВО",
    failedStatus: "ОШИБКА",
    preparingPython: "Запуск процесса Python...",
    downloadPreparing: "Подготовка загрузки",
    ffmpegNotReady: "FFmpeg не готов",
    ffmpegRequired: "Для загрузки необходимо успешно проверить FFmpeg.",
    startError: "Не удалось начать загрузку.",
    startingButton: "Запуск...",
    newDownload: "Новая загрузка",
    retry: "Повторить",
    serverDisconnected: "Соединение с сервером потеряно. Проверьте, что приложение запущено.",
    serverUnavailable: "Не удалось подключиться к серверу приложения.",
    downloadStarted: "Загрузка начата",
    downloadFinished: "Загрузка завершена.",
    downloadFailed: "Не удалось завершить операцию.",
    videoInfo: "Получение сведений о видео...",
    lookingForMp4: "Поиск потоков MP4 для длинного/большого видео...",
    downloadingVideo: "Загрузка видео...",
    downloadingAudio: "Загрузка аудио...",
    mergingFiles: "Загрузка завершена; объединение файлов...",
    convertingVideo: "Преобразование видео в MP4; длительность зависит от видео...",
    creatingMp3: "Создание аудиофайла MP3...",
    mergingAudioVideo: "Объединение аудио и видео...",
    transferred: "Загружено: {size}",
    waitingForTotal: "Ожидание общего размера",
    remaining: "Осталось: {duration}",
    calculating: "Расчёт оставшегося времени",
    durationHours: "{hours} ч {minutes} мин",
    durationMinutes: "{minutes} мин {seconds} с",
    durationSeconds: "{seconds} с",
    ffmpegSystemReady: "FFmpeg найден в системе и работает.",
    ffmpegBundledReady: "Системный FFmpeg не найден; встроенный FFmpeg готов.",
    ffmpegMissing: "Не найден встроенный исполняемый файл FFmpeg.",
    invalidUrl: "Укажите правильную ссылку http или https.",
    downloadAlreadyRunning: "Загрузка уже выполняется.",
    ffmpegServerNotReady: "FFmpeg не готов.",
    compatibleMp4: "Найден совместимый поток MP4; повторное кодирование пропущено.",
    savedVideo: "Видео сохранено в папку «{folder}».",
    savedAudio: "Аудиофайл MP3 сохранён в папку «{folder}».",
  },
};

const progressStages = {
  "Video bilgileri alınıyor...": "videoInfo",
  "Uzun/büyük video için MP4 akışı aranıyor...": "lookingForMp4",
  "Video indiriliyor...": "downloadingVideo",
  "Ses indiriliyor...": "downloadingAudio",
  "İndirme tamamlandı; dosyalar birleştiriliyor...": "mergingFiles",
  "Video MP4'e dönüştürülüyor; bu aşama videonun uzunluğuna bağlı...": "convertingVideo",
  "MP3 ses dosyası oluşturuluyor...": "creatingMp3",
  "Ses ve görüntü birleştiriliyor...": "mergingAudioVideo",
};

const languageLocales = { en: "en-US", tr: "tr-TR", ru: "ru-RU" };
const savedLanguage = localStorage.getItem("sdown-language");
let language = Object.hasOwn(messages, savedLanguage) ? savedLanguage : "tr";
let activeJobId = null;
let currentJob = null;
let pollingTimer = null;
let ffmpegReady = false;
let ffmpegMessage = "";
let viewError = null;

function t(key, values = {}) {
  let message = messages[language][key] || messages.en[key] || key;
  for (const [name, value] of Object.entries(values)) {
    message = message.replaceAll(`{${name}}`, value);
  }
  return message;
}

function isYoutubeUrl(value) {
  try {
    const hostname = new URL(value).hostname.toLowerCase().replace(/\.$/, "");
    return hostname === "youtube.com" || hostname.endsWith(".youtube.com") || hostname === "youtu.be";
  } catch {
    return false;
  }
}

function localizeBackendText(text) {
  if (!text) return "";
  const replacements = [
    ["FFmpeg kontrol ediliyor...", t("ffmpegChecking")],
    ["Uygulama sunucusuna bağlanılamadı.", t("serverUnavailable")],
    ["FFmpeg sistemde bulundu ve çalışıyor.", t("ffmpegSystemReady")],
    ["Sistemde FFmpeg yok; uygulamayla gelen FFmpeg hazır.", t("ffmpegBundledReady")],
    ["Uygulamayla gelen FFmpeg dosyası bulunamadı.", t("ffmpegMissing")],
    ["Uyumlu MP4 akışı bulundu; yeniden kodlama atlanıyor.", t("compatibleMp4")],
    ["Geçerli bir http veya https bağlantısı girin.", t("invalidUrl")],
    ["Devam eden bir indirme zaten var.", t("downloadAlreadyRunning")],
    ["FFmpeg hazır değil.", t("ffmpegServerNotReady")],
  ];
  let localized = text;
  for (const [source, replacement] of replacements) {
    localized = localized.replaceAll(source, replacement);
  }
  localized = localized.replace(
    /Video '([^']+)' klasörüne kaydedildi\./g,
    (_match, folder) => t("savedVideo", { folder }),
  );
  localized = localized.replace(
    /MP3 ses dosyası '([^']+)' klasörüne kaydedildi\./g,
    (_match, folder) => t("savedAudio", { folder }),
  );
  return localized;
}

function applyLanguage() {
  document.documentElement.lang = language;
  document.title = `SDown — ${language === "tr" ? "Yerel video indirici" : language === "ru" ? "Локальный загрузчик видео" : "Local video downloader"}`;
  languageSelect.value = language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    element.innerHTML = t(element.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  if (currentJob) {
    renderJob(currentJob);
  } else {
    renderFfmpeg();
    if (viewError) renderViewError();
  }
}

languageSelect.addEventListener("change", () => {
  language = languageSelect.value;
  localStorage.setItem("sdown-language", language);
  applyLanguage();
});

input.addEventListener("input", () => {
  const youtubeUrl = isYoutubeUrl(input.value.trim());
  chromeCookies.disabled = !youtubeUrl;
  if (!youtubeUrl) chromeCookies.checked = false;
});

function renderFfmpeg(ffmpeg) {
  if (ffmpeg) {
    ffmpegReady = ffmpeg.status === "ready";
    ffmpegMessage = ffmpeg.message || "";
  }
  if (!ffmpegMessage) return;
  ffmpegStatus.textContent = localizeBackendText(ffmpegMessage);
  ffmpegStatus.className = `ffmpeg-status ${ffmpegReady ? "is-ready" : "is-error"}`;
  button.disabled = !ffmpegReady;
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes < 0) return "—";
  if (bytes < 1024) return `${Math.round(bytes)} B`;
  const units = ["KB", "MB", "GB", "TB"];
  let value = bytes / 1024;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${new Intl.NumberFormat(languageLocales[language], { maximumFractionDigits: 1 }).format(value)} ${units[unit]}`;
}

function formatDuration(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) return t("calculating");
  const totalSeconds = Math.ceil(seconds);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const remainingSeconds = totalSeconds % 60;
  if (hours) return t("durationHours", { hours, minutes });
  if (minutes) return t("durationMinutes", { minutes, seconds: remainingSeconds });
  return t("durationSeconds", { seconds: remainingSeconds });
}

function renderProgress(progress, jobStatus) {
  const currentProgress = progress || {};
  const percent = jobStatus === "completed"
    ? 100
    : Number.isFinite(currentProgress.percent)
      ? Math.min(100, Math.max(0, currentProgress.percent))
      : null;
  const stageKey = progressStages[currentProgress.stage];
  progressStage.textContent = jobStatus === "completed"
    ? t("downloadFinished")
    : jobStatus === "failed"
      ? t("downloadFailed")
      : stageKey
        ? t(stageKey)
        : localizeBackendText(currentProgress.stage) || t("videoInfo");
  progressPercent.textContent = percent === null
    ? t("waiting")
    : `${language === "tr" ? "%" : ""}${Math.round(percent)}${language === "tr" ? "" : "%"}`;
  progressBar.style.width = `${percent === null ? 32 : percent}%`;
  if (percent === null) {
    progressTrack.removeAttribute("aria-valuenow");
  } else {
    progressTrack.setAttribute("aria-valuenow", String(Math.round(percent)));
  }
  progressTrack.classList.toggle(
    "is-indeterminate",
    jobStatus === "running" && (percent === null || currentProgress.indeterminate === true),
  );
  progressTransferred.textContent = currentProgress.total_bytes
    ? `${formatBytes(currentProgress.downloaded_bytes)} / ${formatBytes(currentProgress.total_bytes)}`
    : currentProgress.downloaded_bytes
      ? t("transferred", { size: formatBytes(currentProgress.downloaded_bytes) })
      : t("waitingForTotal");
  progressSpeed.textContent = Number.isFinite(currentProgress.speed)
    ? `${formatBytes(currentProgress.speed)}/${language === "ru" ? "с" : language === "en" ? "s" : "sn"}`
    : "";
  progressEta.textContent = currentProgress.eta == null
    ? t("calculating")
    : t("remaining", { duration: formatDuration(currentProgress.eta) });
  progressFile.textContent = currentProgress.filename || "";
}

function renderJob(job) {
  currentJob = job;
  viewError = null;
  const jobStatus = job.status;
  const isMp3 = job.download_type === "mp3";
  panel.hidden = false;
  panel.className = `job-panel is-${jobStatus === "running" ? "running" : jobStatus === "completed" ? "completed" : "failed"}`;
  title.textContent = jobStatus === "running"
    ? isMp3 ? t("runningAudioTitle") : t("runningVideoTitle")
    : jobStatus === "completed" ? t("completedTitle") : t("failedTitle");
  description.textContent = jobStatus === "running"
    ? t("runningDescription")
    : jobStatus === "completed"
      ? isMp3 ? t("completedAudioDescription") : t("completedVideoDescription")
      : t("failedDescription");
  status.textContent = jobStatus === "running"
    ? t("runningStatus")
    : jobStatus === "completed" ? t("completedStatus") : t("failedStatus");
  output.textContent = localizeBackendText(job.output) || t("preparingPython");
  renderProgress(job.progress, jobStatus);
  button.disabled = jobStatus === "running" || !ffmpegReady;
  button.querySelector("span").textContent = jobStatus === "running" ? t("startingButton") : t("newDownload");
  if (jobStatus !== "running") {
    if (pollingTimer) window.clearInterval(pollingTimer);
    pollingTimer = null;
  }
}

function renderViewError() {
  if (!viewError) return;
  panel.hidden = false;
  panel.className = "job-panel is-failed";
  title.textContent = t(viewError.title);
  description.textContent = viewError.message;
  status.textContent = t("failedStatus");
  output.textContent = localizeBackendText(viewError.output);
  renderProgress({ stage: viewError.stage, indeterminate: false }, "failed");
  progressStage.textContent = t(viewError.stageKey);
  button.disabled = !ffmpegReady;
  button.querySelector("span").textContent = t("retry");
}

async function refreshStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();
    renderFfmpeg(data.ffmpeg);
    if (data.job && data.job.id === activeJobId) {
      renderJob(data.job);
    }
  } catch {
    description.textContent = t("serverDisconnected");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const url = input.value.trim();
  if (!url) {
    input.focus();
    return;
  }
  if (!ffmpegReady) {
    viewError = {
      title: "ffmpegNotReady",
      message: t("ffmpegRequired"),
      output: ffmpegMessage,
      stage: "",
      stageKey: "ffmpegNotReady",
    };
    renderViewError();
    return;
  }

  currentJob = null;
  viewError = null;
  button.disabled = true;
  button.querySelector("span").textContent = t("startingButton");
  panel.hidden = false;
  panel.className = "job-panel is-running";
  title.textContent = t("downloadPreparing");
  description.textContent = t("preparingPython");
  status.textContent = t("starting");
  output.textContent = t("waiting");
  renderProgress({
    stage: "Video bilgileri alınıyor...",
    downloaded_bytes: 0,
    total_bytes: null,
    indeterminate: true,
  }, "running");

  try {
    const response = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url,
        download_type: downloadType.value,
        use_chrome_cookies: chromeCookies.checked && isYoutubeUrl(url),
      }),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(localizeBackendText(data.error) || t("startError"));
    }

    activeJobId = data.id;
    renderJob(data);
    if (data.status === "running") {
      pollingTimer = window.setInterval(refreshStatus, 1200);
    }
  } catch (error) {
    currentJob = null;
    viewError = {
      title: "startError",
      message: error.message,
      output: error.message,
      stage: "",
      stageKey: "startError",
    };
    renderViewError();
  }
});

applyLanguage();

fetch("/api/status")
  .then((response) => response.json())
  .then(({ job, ffmpeg }) => {
    renderFfmpeg(ffmpeg);
    if (!job) return;
    activeJobId = job.id;
    renderJob(job);
    if (job.status === "running") {
      pollingTimer = window.setInterval(refreshStatus, 1200);
    }
  })
  .catch(() => {
    ffmpegMessage = "Uygulama sunucusuna bağlanılamadı.";
    ffmpegStatus.textContent = ffmpegMessage;
    ffmpegStatus.className = "ffmpeg-status is-error";
  });
