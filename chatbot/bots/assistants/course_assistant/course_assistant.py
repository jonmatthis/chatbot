import asyncio

from dotenv import load_dotenv

from chatbot.bots.assistants.course_assistant.course_assistant_prompt import COURSE_ASSISTANT_SYSTEM_TEMPLATE

load_dotenv()
from langchain import LLMChain, OpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)



class CourseAssistant:
    def __init__(self,
                 temperature=0.8,
                 model_name="gpt-4",
                 ):


        self._chat_llm = ChatOpenAI(
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
            temperature=temperature,
            model_name=model_name,
        )


        self._chat_prompt = self._create_chat_prompt()
        self._chat_memory = self._configure_chat_memory()

        self._chain = self._create_llm_chain()

    @property
    def conversation_summary(self):
        return self._chat_memory.moving_summary_buffer

    def _configure_chat_memory(self):

        return ConversationSummaryBufferMemory(memory_key="chat_history",
                                               llm=OpenAI(),
                                               max_token_limit=500)

    def _create_llm_chain(self):
        return LLMChain(llm=self._chat_llm,
                        prompt=self._chat_prompt,
                        memory=self._chat_memory,
                        verbose=True,
                        )

    def _create_chat_prompt(self):
        self._system_message_prompt = SystemMessagePromptTemplate.from_template(
            COURSE_ASSISTANT_SYSTEM_TEMPLATE
        )
        human_template = "{human_input}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            human_template
        )

        chat_prompt = ChatPromptTemplate.from_messages(
            [self._system_message_prompt, human_message_prompt]
        )

        return chat_prompt

    async def async_process_input(self, input_text):
        print(f"Input: {input_text}")
        print("Streaming response...\n")
        ai_response = await self._chain.arun(human_input=input_text)
        return ai_response

    async def demo(self):
        print("Welcome to the Neural Control Assistant demo!")
        print("You can ask questions or provide input related to the course.")
        print("Type 'exit' to end the demo.\n")

        while True:
            input_text = input("Enter your input: ")

            if input_text.strip().lower() == "exit":
                print("Ending the demo. Goodbye!")
                break

            response = await self.async_process_input(input_text)

            print("\n")


if __name__ == "__main__":
    assistant = CourseAssistant()
    asyncio.run(assistant.demo())
