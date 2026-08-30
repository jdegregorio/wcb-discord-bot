import logging

from truaxbot import generate_truax_reply

logger = logging.getLogger(__name__)


def generate_truax(message) -> str:
    logger.info("Generating a direct Truax reply")
    if isinstance(message, list):
        messages = message
    else:
        messages = [{"role": "user", "content": str(message)}]
    return generate_truax_reply(messages)


if __name__ == "__main__":
    print(generate_truax("I heard Thomas Jones will be the next coach of the Chicago Bears!"))
