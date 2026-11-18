<div align="center">

<img src="assets/rose-logo.png" alt="ROSE MUSIC logo" width="128" />

# ROSE MUSIC

### Premium Telegram music experience

Music · Video · Queue · Autoplay · Controls

[![Python](https://img.shields.io/badge/Python-3.11%2B-111827?style=for-the-badge&logo=python&logoColor=ff4f81)](https://www.python.org/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-Kurigram-111827?style=for-the-badge&logo=telegram&logoColor=ff4f81)](https://docs.pyrogram.org/)
[![License](https://img.shields.io/badge/License-MIT-111827?style=for-the-badge&logo=opensourceinitiative&logoColor=ff4f81)](LICENSE)

<a href="https://t.me/aresxcores">Official channel</a> · <a href="https://t.me/zorolegacy">Support group</a>

<img src="assets/rose-banner.png" alt="ROSE MUSIC dark rose and audio banner" width="100%" />

</div>

## About ROSE MUSIC

ROSE MUSIC is a Telegram group voice-chat music bot built for clean playback control and straightforward deployment. It uses Pyrogram-compatible Kurigram clients, Py-TgCalls/ntgcalls, yt-dlp, and MongoDB-backed settings to stream audio or video into Telegram supergroups.

The internal Python package is intentionally kept as `anony` to preserve the existing architecture and avoid breaking imports. The user-facing identity, documentation, runtime copy, metadata, and assets are branded as **ROSE MUSIC**.

## Verified capabilities

- Audio playback in Telegram group video chats with `/play`.
- Video playback with `/vplay` and force-play variants.
- YouTube search/URL handling, playlist queueing, and yt-dlp downloads.
- Queue inspection, skip, pause, resume, stop, replay, seek, and loop controls.
- Inline playback controls and per-chat settings.
- Admin-only playback mode, authorized users, blacklist controls, and language selection.
- Optional assistant sessions, automatic leave/end behavior, generated thumbnails, and cookie URLs.
- MongoDB persistence for chats, users, queues, settings, sudoers, and blacklist data.
- Statistics, logging, restart, broadcast, and owner/sudo administration tools.

<img src="assets/rose-feature-art.png" alt="ROSE MUSIC feature artwork" width="100%" />

## Command reference

### Playback and chat controls

| Command | Purpose |
| --- | --- |
| `/play <query>` | Play audio from a search query, URL, or replied media. |
| `/playforce <query>` | Force-play audio. |
| `/vplay <query>` | Play video in the group video chat. |
| `/vplayforce <query>` | Force-play video. |
| `/pause` | Pause the current stream. |
| `/resume` | Resume a paused stream. |
| `/skip` or `/next` | Skip to the next queued item. |
| `/end` or `/stop` | Stop playback and clear the call. |
| `/seek <seconds>` | Seek forward in the current stream. |
| `/seekback <seconds>` | Seek backward in the current stream. |
| `/loop <count\|off>` | Set or disable looping. |
| `/queue` or `/playing` | Show the current track and queue. |
| `/playmode` or `/settings` | Open per-chat playback settings. |
| `/lang` or `/language` | Change the chat language. |
| `/ping` or `/alive` | Show latency and resource status. |
| `/stats` | Show bot and chat statistics. |
| `/help` | Open the interactive help menu in private chat. |
| `/start` | Start the bot or open the start panel. |

### Owner and sudo tools

`/ac`, `/activevc`, `/broadcast`, `/eval`, `/exec`, `/logs`, `/logger`, `/restart`, `/addsudo`, `/delsudo`, `/rmsudo`, `/listsudo`, `/sudolist`, `/blacklist`, `/unblacklist`, `/whitelist`, `/auth`, `/unauth`, `/authlist`, `/admincache`, and `/reload` are restricted administrative commands. Use them only with the appropriate owner, sudo, or group permissions.

## Requirements

- Python 3.11 or newer.
- Telegram API credentials from [my.telegram.org](https://my.telegram.org/apps).
- A bot token from [@BotFather](https://t.me/BotFather).
- A MongoDB connection string from [MongoDB Atlas](https://www.mongodb.com/atlas).
- A Telegram string session for the assistant account, generated with a trusted Pyrogram session workflow.
- FFmpeg and Deno for local/VPS installations. Docker installs these in the image.

## Configuration

Copy `.env.example` to `.env` for local use, or define the same variables in Railway. The application validates the required values at startup.

| Variable | Required | Purpose |
| --- | :---: | --- |
| `API_ID` | Yes | Telegram application ID from my.telegram.org. |
| `API_HASH` | Yes | Telegram application hash from my.telegram.org. |
| `BOT_TOKEN` | Yes | Bot token from @BotFather. |
| `MONGO_URL` | Yes | MongoDB connection URI. |
| `LOGGER_ID` | Yes | Telegram group/channel ID where logs are sent; the bot must be able to access it. |
| `OWNER_ID` | Yes | Numeric Telegram user ID of the bot owner. |
| `SESSION` | Yes | Primary assistant string session. |
| `SESSION2` / `SESSION3` | No | Additional assistant sessions. |
| `SUPPORT_CHAT` | No | Support button and support link. Default: `https://t.me/aresxcores`. |
| `SUPPORT_CHANNEL` | No | Channel button link. Default: `https://t.me/zorolegacy`. |
| `UPDATE_CHANNEL` | No | Update button link. Default: `https://t.me/updatesxhub`. |
| `OWNER_URL` | No | Optional owner button URL. If empty, the button targets `OWNER_ID` with a Telegram user deep link. |
| `DURATION_LIMIT` | No | Maximum track length in minutes; default `60`. |
| `QUEUE_LIMIT` | No | Maximum queued tracks per chat; default `20`. |
| `PLAYLIST_LIMIT` | No | Maximum playlist tracks accepted; default `20`. |
| `AUTO_LEAVE` | No | Leave inactive calls when enabled; default `False`. |
| `AUTO_END` | No | End behavior toggle used by the call manager; default `False`. |
| `THUMB_GEN` | No | Generate thumbnails; default `True`. |
| `VIDEO_PLAY` | No | Enable video playback; default `True`. |
| `LANG_CODE` | No | Default locale code; default `en`. |
| `COOKIES_URL` | Recommended for YouTube | Space-separated `batbin.me` cookie URLs. YouTube may require exported browser cookies when it returns “Sign in to confirm you’re not a bot”; this is especially common on Railway/cloud IPs. |
| `DEFAULT_THUMB` | No | Fallback thumbnail URL. |
| `PING_IMG` | No | Image URL used by ping/status responses. |
| `START_IMG` | No | Image URL used by the premium `/start` panel. Defaults to the ROSE MUSIC welcome artwork. |

Never commit `.env`, bot tokens, API keys, session strings, passwords, or cookie files. `.gitignore` already excludes the local secret and session patterns.

## Local or VPS deployment

```bash
git clone https://github.com/heartcyber25-boop/Anonymousxmusic.git
cd Anonymousxmusic

curl -Ls https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

cp .env.example .env
# Edit .env with your real values.
uv sync --frozen
bash start
```

Add ROSE MUSIC to a Telegram supergroup, promote it with the permissions required for voice-chat operation, and start a video chat before using playback commands. The `/start` welcome panel uses the same premium artwork and button layout in private chats and groups: Help, Owner, Update, Support, and Channel.

## Railway deployment

This repository is prepared as a single Railway worker service. Railway can build it from the included `Dockerfile`; the container installs FFmpeg, Deno, and the locked Python environment, then runs `bash start`. Alternatively, Railway can use the `Procfile` worker command.

1. Create a Railway project and deploy this GitHub repository.
2. Add every required variable from the table above under **Variables**.
3. Confirm the logger chat, assistant account, bot, and MongoDB instance are reachable.
4. Deploy and inspect the service logs for `Bot started` and `Loaded ... modules`.

Playback cannot be fully verified without valid Telegram credentials, a reachable MongoDB instance, an assistant session, and an active group video chat.

## Project layout

```text
anony/              Application package and Telegram plugins
assets/              ROSE MUSIC logo, banner, and feature artwork
config.py            Environment parsing and startup validation
Dockerfile           Railway/container image definition
Procfile             Worker process definition
start                Local/container startup command
.env.example         Safe configuration template
```

## Troubleshooting

- **Missing environment variables:** compare `.env` with `.env.example`; values must be non-empty and numeric IDs must be valid integers.
- **Logger access failure:** add the bot to the logger chat and grant the required permissions.
- **Assistant cannot join:** ensure the string session is valid and the assistant account can join group video chats.
- **No playback:** install/verify FFmpeg and Deno for local deployments, then check yt-dlp/network access.
- **YouTube sign-in or bot-check error:** export a Netscape-format YouTube cookies file, upload it to a private/controlled `batbin.me` raw URL, and set `COOKIES_URL` in Railway. The bot logs the exact yt-dlp failure and returns a clean message instead of crashing.
- **MongoDB errors:** verify the URI, Atlas network access, and database user permissions.
- **Old commands or links in a deployment:** pull the latest commit and restart the worker so the updated locales and configuration defaults load.

## Credits and license

ROSE MUSIC preserves the original open-source architecture and MIT licensing terms. See [LICENSE](LICENSE) for the complete license text. Contributions are welcome through focused pull requests.

<div align="center">

**ROSE MUSIC** · built for late-night queues and clean group calls

<a href="https://t.me/aresxcores">Official channel</a> · <a href="https://t.me/zorolegacy">Support group</a>

</div>
