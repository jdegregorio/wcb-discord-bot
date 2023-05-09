import random
from dotenv import load_dotenv
from loguru import logger

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from prompt import PROMPT_INSULT

# Load environment variables
load_dotenv()


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
        # Create LLM Chain
        chain = LLMChain(
            llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=temperature, max_tokens=1000),
            prompt=PROMPT_INSULT
        )
        insult = chain({"dummy": "", "type": type})['text']
    except Exception as e:
        logger.error(f"Error generating insult: {e}")
        insult = "An error occurred while generating the insult."

    return {"output": insult, "type": type, "temperature": temperature}


if __name__ == "__main__":
    # Configure logging
    logger.add("insult_generator.log", level="INFO")

    # Testing
    for temp in [0.7, 0.8, 0.9, 1.0]:
        print(f"\nTemperature: {temp}\n")
        for type in ["joke", "insult", "insulting pun", "sarcastic remark", "backhanded compliment", "witty one-liner insult", "insulting trolling comment"]:
            print(f"Type: {type}")
            result = insult_jim(type=type, temperature=temp)
            print(f"Insult: {result['output']}\n")
