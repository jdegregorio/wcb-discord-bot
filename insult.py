import logging
import os
import random

from openai import OpenAI
from prompt import INSULT_INSTRUCTIONS, INSULT_PROMPT

logger = logging.getLogger(__name__)

def insult_jim(type=None, temperature=None):
    """
    Generates an insult using the LLMChain.

    :param type: The type of insult, e.g. "joke", "insult", "insulting pun", etc.
    :param temperature: The temperature for the ChatOpenAI model.
    :return: A dictionary containing the generated insult, its type, and temperature.
    """
    # Log function call
    logger.info(f"insult_jim called with type={type}, temperature={temperature}")

    # Randomly select temperature
    if temperature is None:
        temperature = round(random.uniform(0.7, 1.1), 3)

    if type is None:
        type = random.choice(["joke", "insult", "insulting pun", "witty one-liner insult", "insulting trolling comment"])

    try:
        response = OpenAI(timeout=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60"))).responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=INSULT_INSTRUCTIONS.format(type=type),
            input=INSULT_PROMPT.format(type=type),
            temperature=temperature,
            max_output_tokens=300,
        )
        insult = response.output_text.strip()
    except Exception:
        logger.exception("Error generating insult")
        insult = "An error occurred while generating the insult."

    return {"output": insult, "type": type, "temperature": temperature}


if __name__ == "__main__":
    # Testing
    for temp in [0.7, 0.8, 0.9, 1.0]:
        print(f"\nTemperature: {temp}\n")
        for type in ["joke", "insult", "insulting pun", "sarcastic remark", "backhanded compliment", "witty one-liner insult", "insulting trolling comment"]:
            print(f"Type: {type}")
            result = insult_jim(type=type, temperature=temp)
            print(f"Insult: {result['output']}\n")
