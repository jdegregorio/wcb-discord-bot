from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from prompt import PROMPT_INSULT
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

def insult_jim(type=None, temperature=None):
    
    # Randomly select temperature
    if temperature is None:
        temperature = round(random.uniform(0.7, 1.1), 3)

    if type is None:
        type = random.choice(["joke", "insult", "insulting pun", "witty one-liner insult", "insulting trolling comment"])

    # Create LLM Chain
    chain = LLMChain(
        llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=temperature, max_tokens=1000),
        prompt=PROMPT_INSULT
    )
    insult = chain({"dummy": "", "type": type})['text']
    return insult


if __name__ == "__main__":

    # Testing
    for temp in [0.7, 0.8, 0.9, 1.0]:
        print(f"\Temperature: {temp}\n")
        for type in ["joke", "insult", "insulting pun", "sarcastic remark", "backhanded compliment", "witty one-liner insult", "insulting trolling comment"]:
            print(f"Type: {type}")
            print(insult_jim(type=type, temperature=temp))
            print("\n")



# 0.9: "Jim, you're like the Cleveland Browns of fantasy football managers - lots of hype, but in the end, always disappointing."

# 0.6: "Hey Jim, I heard your fantasy football team is like a toddler trying to walk for the first time - all wobbly and constantly falling down. But don't worry, we still love you, even if your team is the equivalent of a baby giraffe on ice skates."

# 0.7: "Hey Jim, I heard that your fantasy team is about as successful as your attempts at growing a full beard. Maybe you should stick to managing your eyebrows instead. #Burn #WillCarterLOL"