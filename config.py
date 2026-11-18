from os import getenv
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def _valid_url(value: str | None, fallback: str) -> str:
    value = (value or "").strip()
    if value.startswith("@"):
        value = f"https://t.me/{value[1:]}"
    elif value.startswith("t.me/"):
        value = f"https://{value}"
    elif value and "://" not in value and " " not in value:
        value = f"https://t.me/{value.lstrip('/')}"

    parsed = urlparse(value)
    if (
        parsed.scheme in {"http", "https"}
        and parsed.netloc
        and " " not in value
        and "\n" not in value
        and "\r" not in value
    ):
        return value
    return fallback

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", 0))
        self.API_HASH = getenv("API_HASH")

        self.BOT_TOKEN = getenv("BOT_TOKEN")
        self.MONGO_URL = getenv("MONGO_URL")

        self.LOGGER_ID = int(getenv("LOGGER_ID", 0))
        self.OWNER_ID = int(getenv("OWNER_ID", 0))

        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", 60)) * 60
        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", 20))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", 20))

        self.SESSION1 = getenv("SESSION", None)
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.SUPPORT_CHANNEL = _valid_url(
            getenv("SUPPORT_CHANNEL"), "https://t.me/aresxcores"
        )
        self.SUPPORT_CHAT = _valid_url(
            getenv("SUPPORT_CHAT"), "https://t.me/zorolegacy"
        )

        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "False").lower() == "true"
        self.AUTO_END: bool = getenv("AUTO_END", "False").lower() == "true"
    
        self.THUMB_GEN: bool = getenv("THUMB_GEN", "True").lower() == "true"
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "True").lower() == "true"

        self.LANG_CODE = getenv("LANG_CODE", "en")

        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "").split(" ")
            if url and "batbin.me" in url
        ]
        asset_root = "https://raw.githubusercontent.com/heartcyber25-boop/Anonymousxmusic/master/assets"
        self.DEFAULT_THUMB = _valid_url(
            getenv("DEFAULT_THUMB"), f"{asset_root}/rose-feature-art.png"
        )
        self.PING_IMG = _valid_url(
            getenv("PING_IMG"), f"{asset_root}/rose-logo.png"
        )
        self.START_IMG = _valid_url(
            getenv("START_IMG"), f"{asset_root}/rose-banner.png"
        )

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
