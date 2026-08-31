from trubot.conversation import ConversationMessage, safety_identifier


def test_message_serializes_to_responses_input() -> None:
    message = ConversationMessage(role="user", content="Tim: hello")
    assert message.as_input() == {"role": "user", "content": "Tim: hello"}


def test_safety_identifier_is_stable_scoped_and_non_identifying() -> None:
    first = safety_identifier(100, 200)
    assert first == safety_identifier(100, 200)
    assert first != safety_identifier(101, 200)
    assert first != safety_identifier(None, 200)
    assert len(first) == 64
    assert first != "discord:100:200"
