import os

import feedparser
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from termcolor import colored

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

RSS_URL = "https://zenn.dev/topics/chatgpt/feed"


def ask_to_chatgpt(prompt: str, sys_setting: str = "") -> tuple[str, int]:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_setting},
                {"role": "user", "content": prompt},
            ],
        )
        message = response["choices"][0]["message"]["content"]
        token = int(response["usage"]["total_tokens"])
        return (message, token)
    except Exception as e:
        raise Exception(e)


def summarize_feed(num_of_articles: int):
    fee: float = 0.0
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries[0:num_of_articles]:
        try:
            response = requests.get(entry.link)
        except Exception as e:
            print(f"Open article Error: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        text_p: list[str] = [s.get_text() for s in soup.find_all("p")]
        content: str = " ".join(text_p)

        prompt: str = f"このテキストの内容を200文字程度の日本語で要約する:\n{content} "
        try:
            answer, token = ask_to_chatgpt(prompt)
            fee += token * 0.000002
        except Exception as e:
            print(f"ChatGPT API Error: {e}")
            continue

        print(colored(f"Title: {entry.title}", "blue", attrs=["bold"]))
        print(f"Summary: {answer}")
        print(f"URL: {entry.link}")
        print(f"Date: {entry.published}")
        print("")

    print(f"\n\nAPI usage fee: {fee:.4f}$")


if __name__ == "__main__":
    summarize_feed(5)
