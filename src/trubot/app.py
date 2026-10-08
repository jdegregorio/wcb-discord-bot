"""Composition root for the Trubot process."""

from __future__ import annotations

import logging
from datetime import timedelta

import discord
from dotenv import load_dotenv
from openai import AsyncOpenAI

from trubot.attention import AttentionTracker
from trubot.budget import BudgetError, UsageLedger
from trubot.config import ConfigurationError, Settings
from trubot.discord_client import TruBotClient
from trubot.distillation import GraphDistiller
from trubot.health import ReadinessFile
from trubot.ingestion import MessageIngestor
from trubot.learning import LearningStore, LearningUnavailable
from trubot.openai_responder import OpenAITruaxResponder
from trubot.participation import ParticipationPolicy, ParticipationTracker

logger = logging.getLogger(__name__)


def build_client(settings: Settings, *, spending_purpose: str = "runtime") -> TruBotClient:
    intents = discord.Intents.none()
    intents.guilds = True
    intents.guild_messages = True
    intents.guild_reactions = True
    intents.message_content = True

    budget = UsageLedger(settings.usage_ledger_path)
    budget.check()
    openai_client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        max_retries=0,
        base_url="https://api.openai.com/v1",
    )
    responder = OpenAITruaxResponder(
        openai_client,
        model=settings.openai_model,
        max_output_tokens=settings.openai_max_output_tokens,
        budget=budget,
        max_retries=settings.openai_max_retries,
        purpose=spending_purpose,
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
    learning = None
    try:
        learning = MessageIngestor(
            LearningStore(
                settings.learning_store_path, retention_days=settings.learning_retention_days
            ),
            settings.allowed_channel_ids,
            batch_size=settings.learning_batch_size,
        )
    except LearningUnavailable:
        logger.warning("Learning paused: verified private state unavailable")
    return TruBotClient(
        settings=settings,
        responder=responder,
        participation=participation,
        attention=attention,
        readiness=readiness,
        intents=intents,
        learning=learning,
        distiller=GraphDistiller(learning, responder, clock=learning.clock) if learning else None,
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
    try:
        client = build_client(settings)
    except BudgetError as error:
        logger.error("Cannot start with unsafe usage ledger: %s", type(error).__name__)
        raise SystemExit(2) from None
    client.run(settings.discord_token, log_handler=None)
