from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

template_insult_system = "You are a professional comedian and comedy writer known for good {type} that are mean, but still in good faith."
prompt_insult_system = SystemMessagePromptTemplate.from_template(template_insult_system)

template_insult_human = """
BACKGROUND: Jim Ayello is a manager in a long running fantasy football league,
called Will Carter League of Champions. Everyone loves Jim, but in the spirit
of fantasy football culture, we occasionally need to make {type} to keep his
ego in check.

--- 
OBJECTIVE & STYLE: Use the similar comedy style as what is used in "The
League" (specifically how Pete and Ruxin insult others). Compose an {type} that
blends smart sophisticated wit with a touch of childhood imaturity, reflecting
a clever balance between high brow humor and petty playfulness. Keep in mind
that the goal is to create a laugh-inducing edgy {type} without crossing the
line into blatant offensiveness. {dummy}

--- 
{type}:
"""
prompt_insult_human = HumanMessagePromptTemplate.from_template(template_insult_human)
PROMPT_INSULT = ChatPromptTemplate.from_messages([prompt_insult_system, prompt_insult_human])

