from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from prompt import PROMPT_INSULT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def insult_jim(temperature=0.9):
    chain = LLMChain(
        llm=ChatOpenAI(model='gpt-3.5-turbo', temperature=temperature, max_tokens=1000),
        prompt=PROMPT_INSULT
    )
    insult = chain("")['text']
    return insult
