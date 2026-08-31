import hashlib

import pytest

from trubot.conversation import ReplyMode
from trubot.personality import STYLE_EXAMPLES, instructions_for


@pytest.mark.parametrize("mode", list(ReplyMode))
def test_each_reply_mode_keeps_the_authentic_voice(mode: ReplyMode) -> None:
    instructions = instructions_for(mode)

    assert "Thomas Jones" in instructions
    assert "Return only the message" in instructions
    assert "Why is it called trash talk" in instructions
    assert "speaker label" in instructions
    assert len(STYLE_EXAMPLES) == 20


def test_modes_have_distinct_situational_guidance() -> None:
    direct = instructions_for(ReplyMode.DIRECT)
    ambient = instructions_for(ReplyMode.AMBIENT)
    reaction = instructions_for(ReplyMode.REACTION)

    assert "addressed Trubot directly" in direct
    assert "naturally joining" in ambient
    assert "reaction target" in reaction
    assert len({direct, ambient, reaction}) == 3


def test_complete_legacy_personality_corpus_is_preserved() -> None:
    corpus = "\n\n".join(
        f"Friend: {example.friend}\nTrubot: {example.trubot}" for example in STYLE_EXAMPLES
    )

    assert len(STYLE_EXAMPLES) == 20
    assert corpus.count("Hey Tim I need you to check Fleaflicker") == 2
    assert "is chicago a metaphor for death then?" in corpus
    assert "Yes I believe that may take out wills outsides as well" in corpus
    assert "Why it it called trash talk?" in corpus
    assert "fix them on and then I got called out on a fire call" in corpus
    assert hashlib.sha256(corpus.encode()).hexdigest() == (
        "3d0ca84f01ff5796c16e5c3776046ed1f5a8ace7845a4b3e82185c68e761d7fe"
    )


def test_prompt_prevents_an_off_topic_reply_from_becoming_a_loop() -> None:
    instructions = instructions_for(ReplyMode.DIRECT)

    assert "Earlier Trubot replies are fallible" in instructions
    assert "Never claim someone said, misspelled, or repeated something" in instructions
    assert "reset and address their current point" in instructions
