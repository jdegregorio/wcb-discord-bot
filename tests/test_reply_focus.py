from trubot.conversation import ConversationMessage as M
from trubot.reply_focus import MAX_FOCUS_CHARS, preceding_human_turn


def switched_topic():
    return [
        M("user", "Friend: Pick an animal coach."),
        M("assistant", "An owl."),
        M("user", "Friend: What dessert would you choose?"),
        M("assistant", "I don't know."),
    ]


def test_current_human_subject_wins_over_old_bot_choice():
    assert preceding_human_turn(switched_topic()) == "Friend: What dessert would you choose?"


def test_nonconversation_rows_cannot_supply_or_interrupt_topic():
    messages = [
        *switched_topic(),
        M("user", "Past evidence: owl", origin="memory"),
        M("user", "Old thread: animal", origin="reference"),
        M("user", "If you had to choose..", origin="focus"),
    ]
    assert preceding_human_turn(messages) == "Friend: What dessert would you choose?"


def test_repeated_message_text_cannot_erase_intervening_human():
    messages = [*switched_topic(), M("user", "If you had to choose..")]
    assert preceding_human_turn(messages) == ""


def test_source_looking_text_is_still_a_human_turn():
    messages = [
        M("user", "RETRIEVED HISTORICAL EVIDENCE is a strange name for a dessert."),
        M("assistant", "Agreed."),
    ]
    assert preceding_human_turn(messages) == messages[0].content


def test_no_human_setup_or_no_immediate_bot_reply_has_no_anchor():
    for messages in ([], [M("assistant", "Hi")], [M("user", "Hi")]):
        assert preceding_human_turn(messages) == ""


def test_focus_is_bounded_without_including_pixels_or_metadata():
    messages = [M("user", "x" * 4000), M("assistant", "Hi")]
    assert preceding_human_turn(messages) == "x" * MAX_FOCUS_CHARS


def test_memory_and_reference_assistant_rows_do_not_manufacture_an_exchange():
    for origin in ("memory", "reference", "focus"):
        assert (
            preceding_human_turn([M("user", "New topic"), M("assistant", "Old", origin=origin)])
            == ""
        )
