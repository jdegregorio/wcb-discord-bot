from typing import List
import langchain.chat_models as chat_models
import langchain.output_parsers as output_parsers
from pydantic import BaseModel, Field
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
import logging as logger

# Setup Logging
logger.basicConfig(level=logger.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define a Pydantic data model for the desired output structure
class HumorScore(BaseModel):
    score: int = Field(
        description='The "Humor Intensity Likert Scale" measures the degree of humor perceived in a statement, joke, story, or any humorous content. It is a 5-point scale, with 1 being "Not at all humorous", indicating no humor was detected or appreciated. 2 represents "Slightly humorous", suggesting a mild amusement. 3 stands for "Moderately humorous", indicating a moderate level of amusement or a chuckle. 4 is "Very humorous", implying a significant amount of laughter or amusement. Finally, 5 denotes "Extremely humorous", indicating an intense level of amusement that may result in uncontrollable laughter or the highest degree of enjoyment.'
    )

# Create an instance of PydanticOutputParser using the defined data model
parser = output_parsers.PydanticOutputParser(pydantic_object=HumorScore)

system_template = """
You are an AI Software Program. You follow commands that are provided in an exact, precise and accurate manner.
"""

# Create a PromptTemplate
prompt_template = """
Return the requested output for the provided data.

For the provided conversation, generate the humor intensity likert scale score (per the output instructions) that describes the humor level of the last response (by andrew.truax) in the provided conversation.
---
OUTPUT INSTRUCTIONS: {format_instructions}
---
CONVERSATION:
'''
Friend: Attention Jim and Will (who I believe had him every year he was active and injured): 
Former Pro Bowl TE Jordan Reed is retiring, sources say. A 2013 3rd-round pick by the Washington Football Team, Reed emerged as one of the games best receiving TEs before battling injuries. His improbable comeback with #49ers last season allowed him to walk away with no regrets.
Friend: Sad day for the league
Friend: I'm gonna need a minute here.
andrew.truax: There will NEVER be a day as sad as when Thomas Jones retired.
'''
SCORE: 5

CONVERSATION:
'''
Friend: Happy NFL Draft Eve, everyone!

I hope you all have a bowl of candy out and the Goodell-f on the shelf is seeing good behavior. Just a reminder if you don't watch the 2014 masterpiece Draft Day the night before the draft, you can't win the Will Carter Bowl next year.

Just ask this past year's champion if he watched Draft Day last year... 
@Jim Ayello
andrew.truax: When is draft day for us?
Friend: Saturday, May 15
andrew.truax: Gotcha so right after the Friday, May 14 
'''
SCORE: 1

CONVERSATION:
'''
Friend: Here's to Jordan Love szn?
Friend: hope he sucks terribly
:joy:
1


that franchise is due
Friend: I'm not ready.
andrew.truax: I hope love is as good as trubisky

Sorry will
Friend: Poll: Are you ok with the Packers trading Aaron Rodgers and not having a hall of fame caliber QB for at least a couple years?
React :sunglasses: for yes
React :hankey: for no
:sunglasses:
2
:eggplant:
1
:hankey:
1
andrew.truax: I think this is the divergent chicks fault
'''
SCORE: 4

CONVERSATION:
{conversation}
OUTPUT: """

prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(prompt_template)
    ],
    input_variables=["conversation"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Define ChatOpenAI model
chat_model = chat_models.ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo")


def generate_humor_scores(conversation: str) -> HumorScore:

    logger.info("Starting LLM for this input:\n {}", conversation)

    try:
        # Format the prompt
        _input = prompt.format_prompt(conversation=conversation)

        # Call the model
        response = chat_model(_input.to_messages())

        # Parse the response
        output = parser.parse(response.content)
        logger.info("Successfully called LLM")

        return output.score

    except Exception as e:
        logger.error("Failed to generate with LLM. Error: {}", e)
        raise e


if __name__ == "__main__":

    test = 'Friend: :+1::skin-tone-2: thanks for coordinating Tim. Best league manager we have ever had.\n:+1:\n2\nFriend: So I know a few of you guys may be having to jump in and out during the draft and will have to keep up with it somewhere, so I am going to try out having the draft on the FleaFlicker app. I’m hoping this can help all of us managing the draft. It is a little goofy in that they only allow for a max of 15 minutes per pick I believe. I scheduled it in FF for  so we can all discuss a couple league items before the picks start. If it starts becoming a hassle, we’ll just go back to a Google doc, but I was hoping that the app may be easier for @everyone\n\nAlso, make sure you cut your rosters down so you can fit your draft picks. Players need to be off your roster and available as rookies and free agents can both be drafted with our picks, so the free agent pool needs to be available for everyone for every pick.\nFriend: Just need to make cuts before the draft, or is there an earlier deadline?\nFriend: Let’s call it Friday by 5 PM. Everyone gets 24 hours to see the full free agent pool then.\nFriend: Sounds pretty great\nandrew.truax: :popcorn:'
    out = generate_humor_scores(test)