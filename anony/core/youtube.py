# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of ROSE MUSIC


import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path
from urllib.parse import urlparse

from py_yt import Playlist, VideosSearch

from anony import logger
from anony.helpers import Track, utils


class DummyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.iregex = re.compile(
            r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)"
            r"(?!/(watch\?v=[A-Za-z0-9_-]{11}|shorts/[A-Za-z0-9_-]{11}"
            r"|playlist\?list=PL[A-Za-z0-9_-]+|[A-Za-z0-9_-]{11}))\S*"
        )

    def get_cookies(self):
        if not self.checked:
            for file in os.listdir(self.cookie_dir):
                if file.endswith(".txt"):
                    self.cookies.append(f"{self.cookie_dir}/{file}")
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        Path(self.cookie_dir).mkdir(parents=True, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            for index, url in enumerate(urls, start=1):
                name = Path(urlparse(url).path).name or f"cookies-{index}.txt"
                if not name.endswith(".txt"):
                    name += ".txt"
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    body = await resp.read()
                with open(f"{self.cookie_dir}/{name}", "wb") as fw:
                    fw.write(body)
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url)) or self.is_soundcloud(url)

    def invalid(self, url: str) -> bool:
        return bool(re.match(self.iregex, url))

    @staticmethod
    def is_soundcloud(url: str) -> bool:
        return bool(re.match(r"https?://(?:www\.)?soundcloud\.com/[^\s]+", url or ""))

    def _ydl_options(self, video: bool = False) -> dict:
        options = {
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "logger": DummyLogger(),
            "nocheckcertificate": True,
            "cookiefile": self.get_cookies(),
            "remote_components": ["ejs:github"],
            "js_runtimes": {"deno": {}},
        }
        if video:
            options["format"] = (
                "best[height<=720][vcodec!=none]/best[height<=720]/best"
            )
        else:
            options["format"] = "hls_aac_160k/hls_aac_96k/bestaudio/best"
        return options

    @staticmethod
    def _pick_entry(info: dict) -> dict | None:
        entries = info.get("entries") if isinstance(info, dict) else None
        if entries:
            return next((entry for entry in entries if entry), None)
        return info if isinstance(info, dict) else None

    def _extract_stream_sync(self, url: str, video: bool = False) -> tuple[dict | None, str | None]:
        try:
            with yt_dlp.YoutubeDL(self._ydl_options(video)) as ydl:
                info = self._pick_entry(ydl.extract_info(url, download=False))
                if not info:
                    return None, None
                stream = info.get("url")
                if video and info.get("vcodec") == "none":
                    return info, None
                if not stream:
                    formats = info.get("formats") or []
                    candidates = [
                        item for item in formats
                        if item.get("url") and (not video or item.get("vcodec") != "none")
                    ]
                    if candidates:
                        stream = candidates[-1]["url"]
                return info, stream
        except Exception as ex:
            logger.warning("Direct stream extraction failed for %s: %s", url, ex)
            return None, None

    @staticmethod
    def _track_from_info(info: dict, message_id: int, video: bool = False) -> Track:
        duration = int(info.get("duration") or 0)
        title = info.get("title") or "SoundCloud track"
        thumbnail = info.get("thumbnail") or info.get("artwork_url")
        return Track(
            id=str(info.get("id") or "public-track"),
            channel_name=info.get("uploader") or info.get("channel") or "",
            duration=utils.to_seconds(str(duration)) if duration else "00:00",
            duration_sec=duration,
            message_id=message_id,
            title=title[:50],
            thumbnail=thumbnail,
            url=info.get("webpage_url") or info.get("original_url"),
            view_count="",
            video=video,
        )

    async def soundcloud_search(self, query: str, message_id: int) -> Track | None:
        def search_sync():
            try:
                with yt_dlp.YoutubeDL(self._ydl_options(False)) as ydl:
                    info = ydl.extract_info(f"scsearch1:{query}", download=False)
                    entry = self._pick_entry(info)
                    if not entry:
                        return None
                    url = entry.get("webpage_url") or entry.get("original_url")
                    if not url:
                        return None
                    track_info = self._pick_entry(ydl.extract_info(url, download=False))
                    return self._track_from_info(track_info or entry, message_id, False)
            except Exception as ex:
                logger.warning("SoundCloud search failed for %r: %s", query, ex)
                return None

        return await asyncio.to_thread(search_sync)

    async def cache_public_stream(self, track: Track) -> str | None:
        """Cache a public SoundCloud AAC stream in a stable local file for PyTgCalls."""
        if not self.is_soundcloud(track.url):
            return None

        def cache_sync():
            try:
                Path("downloads").mkdir(parents=True, exist_ok=True)
                opts = self._ydl_options(False)
                opts.update(
                    {
                        "outtmpl": "downloads/public-%(id)s.%(ext)s",
                        "overwrites": False,
                        "continuedl": True,
                    }
                )
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(track.url, download=False)
                    video_id = str(info.get("id") or track.id)
                    existing = list(Path("downloads").glob(f"public-{video_id}.*"))
                    if existing:
                        return str(existing[0])
                    ydl.download([track.url])
                    files = list(Path("downloads").glob(f"public-{video_id}.*"))
                    files = [p for p in files if p.suffix not in {".part", ".ytdl"}]
                    return str(files[0]) if files else None
            except Exception as ex:
                logger.warning("Public stream cache failed for %s: %s", track.url, ex)
                return None

        return await asyncio.to_thread(cache_sync)

    async def resolve(self, track: Track, *, force: bool = False) -> str | None:
        """Resolve a track to a direct stream URL; use public SoundCloud as fallback."""
        if force:
            track.file_path = None

        if self.is_soundcloud(track.url):
            cached = await self.cache_public_stream(track)
            if cached:
                track.file_path = cached
                return cached

        _, stream = await asyncio.to_thread(
            self._extract_stream_sync, track.url, track.video
        )
        if stream:
            track.file_path = stream
            return stream

        fallback = await self.soundcloud_search(track.title or track.url, track.message_id)
        if not fallback:
            return None
        _, stream = await asyncio.to_thread(
            self._extract_stream_sync, fallback.url, False
        )
        fallback.user = track.user
        track.__dict__.update(fallback.__dict__)
        cached = await self.cache_public_stream(track)
        if cached:
            track.file_path = cached
            return cached
        if stream:
            track.file_path = stream
            return stream
        return None

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        if self.is_soundcloud(query):
            info, _ = await asyncio.to_thread(self._extract_stream_sync, query, False)
            return self._track_from_info(info, m_id, False) if info else None
        try:
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
        except Exception as ex:
            logger.warning("YouTube search failed for %r: %s", query, ex)
            return None
        if results and results["result"]:
            data = results["result"][0]
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        return await self.soundcloud_search(query, m_id)

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception as ex:
            logger.warning("YouTube playlist failed for %s: %s", url, ex)
            pass
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        url = self.base + video_id
        expected_ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{expected_ext}"

        existing = list(Path("downloads").glob(f"{video_id}.*"))
        existing = [p for p in existing if p.suffix not in {".part", ".ytdl"}]
        if existing:
            return str(existing[0])

        cookie = self.get_cookies()
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "logger": DummyLogger(),
            "nocheckcertificate": True,
            "cookiefile": cookie,
            "remote_components": ["ejs:github"],
            "js_runtimes": {"deno": {}},
        }

        if video:
            ydl_opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio)",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[acodec=opus]/bestaudio",
            }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError) as ex:
                    logger.warning(
                        "YouTube download failed for %s: %s. "
                        "If YouTube asks for sign-in, configure COOKIES_URL.",
                        video_id,
                        ex,
                    )
                    return None
                except Exception as ex:
                    logger.warning("Download failed: %s", ex)
                    return None
            downloaded = list(Path("downloads").glob(f"{video_id}.*"))
            downloaded = [
                p for p in downloaded if p.suffix not in {".part", ".ytdl"}
            ]
            return str(downloaded[0]) if downloaded else None

        return await asyncio.to_thread(_download)
