"""Composition root for the Trubot process."""

from __future__ import annotations

import logging
from datetime import timedelta

import discord
from dotenv import load_dotenv
from openai import AsyncOpenAI

from trubot.attention import AttentionTracker
from trubot.config import ConfigurationError, Settings
from trubot.discord_client import TruBotClient
from trubot.health import ReadinessFile
from trubot.openai_responder import OpenAITruaxResponder
from trubot.participation import ParticipationPolicy, ParticipationTracker

logger = logging.getLogger(__name__)


def build_client(settings: Settings) -> TruBotClient:
    intents = discord.Intents.none()
    intents.guilds = True
    intents.guild_messages = True
    intents.guild_reactions = True
    intents.message_content = True

    openai_client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )
    responder = OpenAITruaxResponder(
        openai_client,
        model=settings.openai_model,
        max_output_tokens=settings.openai_max_output_tokens,
    )
    participation = ParticipationTracker(
        ParticipationPolicy(
            delay=timedelta(seconds=settings.auto_delay_seconds),
            activity_window=timedelta(seconds=settings.auto_activity_window_seconds),
            min_interval=timedelta(seconds=settings.auto_min_interval_seconds),
            daily_limit=settings.auto_daily_limit,
            min_participants=settings.auto_min_participants,
        )
    )
    attention = AttentionTracker(timedelta(seconds=settings.followup_window_seconds))
    readiness = ReadinessFile(
        settings.ready_file,
        refresh_seconds=settings.health_refresh_seconds,
    )
    return TruBotClient(
        settings=settings,
        responder=responder,
        participation=participation,
        attention=attention,
        readiness=readiness,
        intents=intents,
        allowed_mentions=discord.AllowedMentions.none(),
    )


def main() -> None:
    load_dotenv()
    try:
        settings = Settings.from_env()
    except ConfigurationError as error:
        logging.basicConfig(level=logging.ERROR, format="%(levelname)s %(name)s %(message)s")
        logger.error("Invalid configuration: %s", error)
        raise SystemExit(2) from None

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,
    )
    logger.info("Starting Trubot model=%s", settings.openai_model)
    client = build_client(settings)
    client.run(settings.discord_token, log_handler=None)
