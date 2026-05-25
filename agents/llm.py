from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os

load_dotenv()


def get_llm():

    groq_llm = ChatGroq(
        model="qwen/qwen3-32b",
        api_key=os.getenv(
            "GROQ_API_KEY"
        ),
         max_tokens=1000,
         temperature=0,
         streaming=True
    )

  

    llm=groq_llm

    return llm