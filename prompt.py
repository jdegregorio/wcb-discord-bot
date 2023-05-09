from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

template_insult_system = "You are a professional comedian and comedy writer who specializing in celebrity roasts."
prompt_insult_system = SystemMessagePromptTemplate.from_template(template_insult_system)

template_insult_human = """
BACKGROUND: Jim Ayello is a manager in a long running fantasy football league,
called Will Carter League of Champions. He is a sports journalist, and even
writes fantasy sports column. Everyone loves Jim, but they also want to make
sure he never gets too big of a head given that he plays fantasy football for a
living, so someone  must occasionally put him in his place by insulting him or
providing fantasy smack talk about his team.

--- OBJECTIVE & STYLE: Use the similar comedy style as what is used in "The
League". Specifically, create insults in the way that Pete and Ruxin would make
fun of the others in the league. Compose an intellectually risqué insult that
blends sophisticated wit with a touch of raunchiness, reflecting a clever
balance between high brow humor and below-the-waist playfulness. Keep in mind
that the goal is to create a laugh-inducing, thought-provoking, and edgy insult
without crossing the line into blatant offensiveness. Jim's team is actually
good, so the joke should not be about how bad his team is. {dummy}

--- INSULT:
"""
prompt_insult_human = HumanMessagePromptTemplate.from_template(template_insult_human)

PROMPT_INSULT = ChatPromptTemplate.from_messages([prompt_insult_system, prompt_insult_human])

