"""Fixed public-scene image generation on Trubot's existing spending ledger."""

from __future__ import annotations

import asyncio
import base64
import binascii
import io
from dataclasses import dataclass

from openai import AsyncOpenAI
from PIL import Image

from trubot.aurora import Opportunity
from trubot.budget import IMAGE_MODEL, BudgetUnavailable, UsageLedger


@dataclass(frozen=True, slots=True)
class AuroraImage:
    data: bytes
    caption: str
    description: str


def image_prompt(opportunity: Opportunity) -> str:
    # Only closed public region names enter the prompt. No human corpus or source photos.
    return (
        "Create an original photorealistic landscape illustration of northern lights over "
        f"Michigan's Upper Peninsula near {opportunity.region}, looking north over Lake Superior. "
        "A quiet rocky shoreline, dark conifers at the edge, realistic modest green aurora "
        "curtains near the northern horizon, clear stars and cold lake water. Natural long "
        "exposure appearance, restrained saturation, plausible geography and scale. No people, "
        "buildings, animals, text, watermark, camera interface, snow assumption or tropical "
        "mountains. This is an imagined scene, not documentation of an actual sighting."
    )


class AuroraImageGenerator:
    def __init__(self, client: AsyncOpenAI, ledger: UsageLedger) -> None:
        self.client = client.with_options(max_retries=0, timeout=120.0)
        self.ledger = ledger

    async def generate(self, opportunity: Opportunity, *, purpose: str = "runtime") -> AuroraImage:
        prompt = image_prompt(opportunity)
        reservation = await asyncio.to_thread(
            self.ledger.reserve_image, prompt_bytes=len(prompt.encode()), purpose=purpose
        )
        try:
            response = await self.client.images.generate(
                model=IMAGE_MODEL,
                prompt=prompt,
                n=1,
                size="1536x1024",
                quality="medium",
                output_format="png",
                background="opaque",
            )
            usage = response.usage
            if (
                usage is None
                or usage.input_tokens_details.image_tokens != 0
                or usage.input_tokens_details.text_tokens != usage.input_tokens
                or usage.total_tokens != usage.input_tokens + usage.output_tokens
            ):
                raise BudgetUnavailable("Image usage metadata unavailable or unsupported")
            await asyncio.to_thread(
                self.ledger.settle_image,
                reservation,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
            )
        except BaseException:
            # Includes cancellation. Never retry an ambiguous paid image attempt.
            await asyncio.to_thread(self.ledger.uncertain, reservation)
            raise
        if not response.data or len(response.data) != 1 or not response.data[0].b64_json:
            raise ValueError("Single generated image required")
        encoded = response.data[0].b64_json
        if len(encoded) > 11_000_000:
            raise ValueError("Generated image exceeds Discord attachment bound")
        try:
            data = base64.b64decode(encoded, validate=True)
        except binascii.Error as error:
            raise ValueError("Invalid generated image encoding") from error
        if len(data) > 8_000_000:
            raise ValueError("Generated image exceeds Discord attachment bound")
        with Image.open(io.BytesIO(data)) as image:
            if image.format != "PNG" or image.size != (1536, 1024):
                raise ValueError("Unexpected generated image format")
            image.verify()
        return AuroraImage(
            data,
            "Pretty good excuse to look north.\n"
            "-# AI-generated U.P. scene inspired by favorable conditions near "
            f"{opportunity.region} "
            "last night. A viewing opportunity, not a confirmed sighting.",
            "AI-generated illustration: green northern lights above Lake Superior, a rocky "
            "Upper Peninsula shoreline and dark conifers. Not a photograph of last night.",
        )
