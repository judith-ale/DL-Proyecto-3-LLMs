import os
import discord
from discord.ext import commands
from langchain.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

CHROMA_PATH = os.environ.get("CHROMA_PATH")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---
Answer the question nicely based only on the above context: {question}
"""


def main():
    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    model = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo-0125")

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.command()
    async def question(ctx, *, question):
        try:
            # Search the DB.
            results = db.similarity_search_with_relevance_scores(question, k=7)
            if len(results) == 0 or results[0][1] < 0.7:
                print(f"Unable to find matching results.")
                await ctx.send(f"Sorry, I was unable to find matching results.")
                return

            context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
            prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
            prompt = prompt_template.format(context=context_text, question=question)
            print(prompt)

            response_text = model.invoke(prompt).content
            sources = [doc.metadata.get("source", None) for doc, _score in results]

            formatted_response = f"RESPONSE: {response_text}\n\nSOURCES: {sources}"
            print(formatted_response)

            await ctx.send(response_text)
        except Exception as e:
            print(f"Error occurred: {e}")
            await ctx.send("Sorry, I was unable to process your question.")

    bot.run(os.environ.get("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()