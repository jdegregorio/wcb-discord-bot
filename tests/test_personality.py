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
    assert len(STYLE_EXAMPLES) >= 15


def test_modes_have_distinct_situational_guidance() -> None:
    direct = instructions_for(ReplyMode.DIRECT)
    ambient = instructions_for(ReplyMode.AMBIENT)
    reaction = instructions_for(ReplyMode.REACTION)

    assert "addressed Trubot directly" in direct
    assert "naturally joining" in ambient
    assert "reaction target" in reaction
    assert len({direct, ambient, reaction}) == 3
