import base64
import io
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from trubot.vision import (
    MAX_BYTES,
    ImageCollector,
    decode_image,
    download_image,
    image_urls,
    trusted_image_url,
)


def pixels(format="PNG", **kwargs):
    output = io.BytesIO()
    Image.new("RGB", (100, 70), "red").save(output, format=format, **kwargs)
    return output.getvalue()


def message(urls=(), embeds=(), size=100):
    return SimpleNamespace(
        attachments=[SimpleNamespace(url=u, size=size, content_type="image/png") for u in urls],
        embeds=embeds,
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://cdn.discordapp.com/a",
        "https://cdn.discordapp.com.evil.test/a",
        "https://user@cdn.discordapp.com/a",
        "https://localhost/a",
        "https://cdn.discordapp.com:999/a",
    ],
)
def test_non_cdn_images_are_rejected(url):
    assert not trusted_image_url(url)


def test_pixels_are_decoded_bounded_and_private():
    decoded = decode_image(pixels())
    assert decoded.data_url.startswith("data:image/jpeg;base64,")
    assert "data:image" not in repr(decoded)
    raw = base64.b64decode(decoded.data_url.split(",", 1)[1])
    with Image.open(io.BytesIO(raw)) as im:
        assert im.size == (100, 70)
    gif = pixels("GIF", save_all=True, append_images=[Image.new("RGB", (100, 70), "blue")])
    assert "First frame" in decode_image(gif).description
    for raw in (b"", b"invalid", b"x" * (MAX_BYTES + 1)):
        with pytest.raises((ValueError, OSError)):
            decode_image(raw)
    with patch("trubot.vision.MAX_PIXELS", 10), pytest.raises(ValueError):
        decode_image(pixels())


@pytest.mark.asyncio
async def test_collector_deduplicates_and_explains_limits_failures_and_oversize():
    fetch = AsyncMock(return_value=pixels())
    collector = ImageCollector(fetch)
    url = "https://cdn.discordapp.com/a.png"
    images, notice = await collector.collect(message([url, url]))
    assert len(images) == 1 and notice == ""
    assert await collector.collect(message([url])) == ((), "")
    images, notice = await collector.collect(
        message(["https://cdn.discordapp.com/b.png", "https://cdn.discordapp.com/c.png"])
    )
    assert len(images) == 1 and "unavailable" in notice
    assert fetch.await_count == 2
    images, notice = await ImageCollector(fetch).collect(message([url], size=MAX_BYTES + 1))
    assert not images and "unavailable" in notice
    fetch.side_effect = TimeoutError
    images, notice = await ImageCollector(fetch).collect(message([url]))
    assert not images and "unavailable" in notice


def test_embed_proxy_is_used_instead_of_third_party_origin():
    embed = SimpleNamespace(
        image=SimpleNamespace(
            url="https://external.test/a", proxy_url="https://images-ext-1.discordapp.net/a"
        ),
        thumbnail=None,
    )
    assert image_urls(message(embeds=[embed])) == ["https://images-ext-1.discordapp.net/a"]


class Content:
    def __init__(self, chunks):
        self.chunks = chunks

    async def iter_chunked(self, size):
        for chunk in self.chunks:
            yield chunk


@pytest.mark.asyncio
async def test_download_is_stream_bounded_and_does_not_redirect_or_send_credentials():
    response = SimpleNamespace(status=200, content_length=None, content=Content([b"hello"]))
    response_context = AsyncMock()
    response_context.__aenter__.return_value = response
    session = MagicMock()
    session.get.return_value = response_context
    session_context = AsyncMock()
    session_context.__aenter__.return_value = session
    with patch("trubot.vision.aiohttp.ClientSession", return_value=session_context) as create:
        assert await download_image("https://cdn.discordapp.com/a") == b"hello"
        create.assert_called_once()
        assert create.call_args.kwargs["trust_env"] is False
        session.get.assert_called_with("https://cdn.discordapp.com/a", allow_redirects=False)
        for status, length, chunks in [
            (404, 0, []),
            (200, MAX_BYTES + 1, []),
            (200, None, [b"x" * (MAX_BYTES + 1)]),
        ]:
            response.status, response.content_length, response.content = (
                status,
                length,
                Content(chunks),
            )
            with pytest.raises(ValueError):
                await download_image("https://cdn.discordapp.com/a")
    with pytest.raises(ValueError):
        await download_image("https://external.test/a")
