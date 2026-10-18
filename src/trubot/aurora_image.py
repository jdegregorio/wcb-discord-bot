"""Fixed public-scene image generation on Trubot's existing spending ledger."""

from __future__ import annotations

import asyncio
import base64
import binascii
import io
from dataclasses import dataclass

from openai import AsyncOpenAI
from PIL import Image

from trubot.aurora import REGIONS, Opportunity
from trubot.budget import IMAGE_MODEL, BudgetUnavailable, UsageLedger


@dataclass(frozen=True, slots=True)
class AuroraImage:
    data: bytes
    caption: str
    description: str


def image_prompt(opportunity: Opportunity) -> str:
    return scene_prompt(opportunity.region)


def scene_prompt(region: str) -> str:
    if region not in {item.name for item in REGIONS}:
        raise ValueError("Unapproved public scene region")
    # Only closed public region names enter the prompt. No human corpus or source photos.
    return (
        "Create an original photorealistic landscape illustration of northern lights over "
        f"Michigan's Upper Peninsula near {region}, looking north over Lake Superior. "
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
        image = await self._generate(image_prompt(opportunity), purpose=purpose)
        return AuroraImage(
            image,
            "Pretty good excuse to look north.\n"
            "-# AI-generated U.P. scene inspired by favorable conditions near "
            f"{opportunity.region} "
            "last night. A viewing opportunity, not a confirmed sighting.",
            "AI-generated illustration: green northern lights above Lake Superior, a rocky "
            "Upper Peninsula shoreline and dark conifers. Not a photograph of last night.",
        )

    async def generate_requested(self, region: str, *, purpose: str = "runtime") -> AuroraImage:
        if region in {"trail_camera", "woodpile", "lake_freeze", "lake_thaw"}:
            return await self.generate_life(region, purpose=purpose)
        image = await self._generate(scene_prompt(region), purpose=purpose)
        return AuroraImage(
            image,
            {
                "Marquette": "Lake Superior showing off.",
                "Munising": "Would sit here for a while.",
                "the Keweenaw": "Pretty good excuse to look north.",
            }[region]
            + f"\n-# AI-generated scene near {region}.",
            f"AI-generated illustration of imagined northern lights over Lake Superior near "
            f"{region}, with a rocky shoreline and dark conifers. Not a real photograph.",
        )

    async def generate_life(self, scene: str, *, purpose: str = "runtime") -> AuroraImage:
        subjects = {
            "trail_camera": (
                "A candid trail-camera style view of a white-tailed deer at the edge of a "
                "mixed conifer and birch forest, uneven ground, quiet natural daylight. "
                "No artificial antler exaggeration or camera timestamp.",
                "Management finally showed up.",
            ),
            "woodpile": (
                "A modest neatly stacked split hardwood pile beside a simple woodshed, "
                "work gloves resting on a chopping block, autumn leaves and mixed conifers. "
                "No people, running tools, dangerous action or luxury cabin.",
                "Winter can take its time.",
            ),
            "lake_freeze": (
                "A SMALL inland lake with thin new ice along a sheltered shoreline, dark "
                "open water farther out, frosty reeds and conifers. Not Lake Superior "
                "frozen solid. No people on ice or implication it is safe to walk on.",
                "Lake's starting to get ideas.",
            ),
            "lake_thaw": (
                "Spring breakup on a SMALL inland lake: broken shore ice, open water, "
                "wet stones and conifers. Restrained early spring colors, no summer "
                "flowers, people on ice or implausible icebergs.",
                "About time.",
            ),
        }
        if scene not in subjects:
            raise ValueError("Unapproved outdoor scene")
        subject, caption = subjects[scene]
        prompt = (
            "Create an original photorealistic illustration of an imagined everyday scene "
            "in Michigan's Upper Peninsula. " + subject + " Ordinary imperfect composition, "
            "plausible scale and ecology, natural restrained colors. No text, watermark, "
            "real person's likeness or claim of documenting an actual event."
        )
        data = await self._generate(prompt, purpose=purpose)
        return AuroraImage(
            data,
            caption + "\n-# AI-generated U.P. scene.",
            f"AI-generated imagined U.P. {scene.replace('_', ' ')} scene. Not a real photo "
            "or evidence of Andrew's activities, wildlife sightings or current lake conditions.",
        )

    async def _generate(self, prompt: str, *, purpose: str) -> bytes:
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
        return data
