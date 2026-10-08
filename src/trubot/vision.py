"""Ephemeral, bounded Discord pixels for responses, never a durable learning write."""

from __future__ import annotations

import asyncio
import base64
import io
from collections.abc import Awaitable, Callable
from urllib.parse import urlsplit

import aiohttp
import discord
from PIL import Image, ImageOps

from trubot.conversation import ConversationImage

MAX_IMAGES = 2
MAX_BYTES = 4 * 1024 * 1024
MAX_PIXELS = 20_000_000
# Deliberately loose: exceeds the documented 30,000-patch rejection ceiling
# times the highest published vision multiplier (2.46), including rounding.
# The ledger still halts if authoritative usage ever exceeds a reservation.
IMAGE_TOKEN_BOUND = 80_000
_CDN_HOSTS = frozenset(
    {
        "cdn.discordapp.com",
        "media.discordapp.net",
        "images-ext-1.discordapp.net",
        "images-ext-2.discordapp.net",
    }
)


def trusted_image_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        return (
            parsed.scheme == "https"
            and parsed.hostname in _CDN_HOSTS
            and parsed.port in (None, 443)
            and parsed.username is None
            and parsed.password is None
        )
    except ValueError:
        return False


def image_urls(message: discord.Message) -> list[str]:
    urls: list[str] = []
    for attachment in getattr(message, "attachments", ()):
        if attachment.size <= MAX_BYTES and (attachment.content_type or "").startswith("image/"):
            urls.append(attachment.url)
    for embed in getattr(message, "embeds", ()):
        for item in (embed.image, embed.thumbnail):
            if item and item.url:
                urls.append(item.proxy_url or item.url)
    return list(dict.fromkeys(url for url in urls if trusted_image_url(url)))


async def download_image(url: str) -> bytes:
    if not trusted_image_url(url):
        raise ValueError("Image source is not a Discord CDN")
    timeout = aiohttp.ClientTimeout(total=6)
    # Never follow a CDN redirect to an arbitrary host or send Discord credentials.
    async with (
        aiohttp.ClientSession(timeout=timeout, trust_env=False) as session,
        session.get(url, allow_redirects=False) as response,
    ):
        if response.status != 200:
            raise ValueError("Image unavailable")
        if response.content_length and response.content_length > MAX_BYTES:
            raise ValueError("Image too large")
        raw = bytearray()
        async for chunk in response.content.iter_chunked(64 * 1024):
            raw.extend(chunk)
            if len(raw) > MAX_BYTES:
                raise ValueError("Image too large")
        return bytes(raw)


def decode_image(raw: bytes) -> ConversationImage:
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("Image outside byte limit")
    with Image.open(io.BytesIO(raw), formats=("PNG", "JPEG", "WEBP", "GIF")) as image:
        if image.width * image.height > MAX_PIXELS:
            raise ValueError("Image outside pixel limit")
        # Animation is represented honestly by its first frame. Do not decode an
        # unbounded number of frames or pretend to have watched the entire clip.
        animated = getattr(image, "is_animated", False)
        frame = ImageOps.exif_transpose(image).convert("RGB")
        frame.thumbnail((1600, 1600))
        output = io.BytesIO()
        frame.save(output, format="JPEG", quality=90)
        return ConversationImage(
            "data:image/jpeg;base64," + base64.b64encode(output.getvalue()).decode("ascii"),
            "First frame only of an animation" if animated else "Attached image pixels",
        )


class ImageCollector:
    """One response shares a two-image/two-download budget across all messages."""

    def __init__(self, fetch: Callable[[str], Awaitable[bytes]] = download_image) -> None:
        self.fetch = fetch
        self.attempts = 0
        self.seen: set[str] = set()

    async def collect(self, message: discord.Message) -> tuple[tuple[ConversationImage, ...], str]:
        images = []
        missing = False
        urls = image_urls(message)
        # Unsupported/oversized attachments must remain visible as missing context.
        advertised = any(
            (a.content_type or "").startswith("image/") for a in getattr(message, "attachments", ())
        ) or any(e.image or e.thumbnail for e in getattr(message, "embeds", ()))
        for url in urls:
            if url in self.seen:
                continue
            self.seen.add(url)
            if self.attempts >= MAX_IMAGES:
                missing = True
                continue
            self.attempts += 1
            try:
                raw = await self.fetch(url)
                images.append(await asyncio.to_thread(decode_image, raw))
            except (
                aiohttp.ClientError,
                TimeoutError,
                OSError,
                ValueError,
                Image.DecompressionBombError,
            ):
                missing = True
        if advertised and not urls:
            missing = True
        notice = " [Some image pixels unavailable or omitted by limits.]" if missing else ""
        return tuple(images), notice
