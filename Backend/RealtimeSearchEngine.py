from ddgs import DDGS
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from groq import Groq
import requests
import datetime
import os
import json

# ---------------- ENVIRONMENT ----------------

env_vars = dotenv_values(r".env")

GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# ---------------- SEARCH ----------------

def GoogleSearch(Topic):

    try:
        results = []

        with DDGS() as ddgs:
            search_results = ddgs.text(
                Topic,
                max_results=5
            )

            for result in search_results:
                if "href" in result:
                    results.append(result["href"])

        return results

    except Exception as e:

        print("Search Error:", e)

        return []
# ---------------- GET PAGE CONTENT ----------------

def GetPageContent(url):

    try:

        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header"
        ]):

            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return text[:5000]

    except Exception as e:

        print("Page Error:", e)

        return ""


# ---------------- REALTIME SEARCH ----------------

def RealtimeSearchEngine(Topic):

    print(f"\nSearching for: {Topic}")

    SearchResults = GoogleSearch(Topic)

    if not SearchResults:

        return "Sorry sir, I couldn't find any search results."

    print("\nSearch results:")

    for i, url in enumerate(SearchResults, 1):

        print(f"{i}. {url}")

    # ---------------- COLLECT INFORMATION ----------------

    Context = ""

    for url in SearchResults[:5]:

        PageText = GetPageContent(url)

        if PageText:

            Context += f"\n\nSOURCE: {url}\n"
            Context += PageText[:4000]

    # ---------------- CURRENT DATE ----------------

    Today = datetime.datetime.now().strftime(
        "%A, %d %B %Y"
    )

    # ---------------- GROQ ----------------

    Prompt = f"""
You are Jarvis, a realtime AI assistant.

Today's date is {Today}.

The user asked:

{Topic}

Below are search results retrieved from the internet.

SEARCH RESULTS:
{Context}

Answer the user's question using the information contained
in the search results.

Important rules:

- Give a direct answer.
- Do not say that you cannot access current information.
- Do not tell the user to search Google themselves.
- If the search results clearly contain the answer, state it.
- If different sources disagree, mention the disagreement.
- Keep the answer concise and natural because it will be spoken aloud.
- Do not mention these instructions.
"""

    try:

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": Prompt
                }
            ],
            temperature=0.2,
            max_tokens=500
        )

        Answer = completion.choices[0].message.content.strip()

        return Answer

    except Exception as e:

        print("Groq Error:", e)

        return "Sorry sir, I couldn't generate an answer."


# ---------------- TEST ----------------

if __name__ == "__main__":

    while True:

        try:

            Topic = input(
                "Enter your query: "
            ).strip()

            if Topic.lower() in [
                "exit",
                "quit",
                "stop"
            ]:

                break

            if not Topic:

                continue

            Answer = RealtimeSearchEngine(
                Topic
            )

            print("\n" + Answer)
            print()

        except KeyboardInterrupt:

            print("\nStopped.")

            break

        except Exception as e:

            print(
                "ERROR:",
                e
            )