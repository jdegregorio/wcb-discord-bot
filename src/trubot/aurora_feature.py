"""First scheduled visual skill: bounded public evidence, image generation and durable claims."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Protocol

from trubot.aurora import EASTERN, AuroraStore, Opportunity, collect_opportunity, morning_window
from trubot.aurora_image import AuroraImage


class ImageGenerator(Protocol):
    async def generate(
        self, opportunity: Opportunity, *, purpose: str = "runtime"
    ) -> AuroraImage: ...


class AuroraFeature:
    def __init__(
        self,
        store: AuroraStore,
        images: ImageGenerator,
        *,
        collect: Callable[..., Awaitable[Opportunity | None]] = collect_opportunity,
    ) -> None:
        self.store = store
        self.images = images
        self.collect = collect

    async def prepare(
        self, *, now: datetime, before_generation: Callable[[], Awaitable[bool]] | None = None
    ) -> tuple[Opportunity, AuroraImage] | None:
        if morning_window(now) is None:
            return None
        morning = now.astimezone(EASTERN).date().isoformat()
        if await asyncio.to_thread(self.store.seen, morning):
            return None
        opportunity = await self.collect(now=now)
        if opportunity is None or not await asyncio.to_thread(self.store.claim, opportunity):
            return None
        try:
            if before_generation is not None and not await before_generation():
                await asyncio.to_thread(self.store.finish, morning, "deferred")
                return None
            image = await self.images.generate(opportunity)
        except BaseException:
            await asyncio.to_thread(self.store.finish, morning, "failed")
            raise
        return opportunity, image
