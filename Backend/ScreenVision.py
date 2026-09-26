import os
import base64
from PIL import ImageGrab
from dotenv import dotenv_values
from groq import Groq


# ---------------- ENVIRONMENT ----------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

env_vars = dotenv_values(
    os.path.join(BASE_DIR, ".env")
)

GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)


# ---------------- SCREENSHOT ----------------

def TakeScreenshot():

    ScreenshotPath = os.path.join(
        BASE_DIR,
        "Data",
        "Screen.png"
    )

    screenshot = ImageGrab.grab()

    screenshot.save(
        ScreenshotPath,
        "PNG"
    )

    return ScreenshotPath


# ---------------- ENCODE IMAGE ----------------

def EncodeImage(ImagePath):

    with open(ImagePath, "rb") as image_file:

        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


# ---------------- SCREEN VISION ----------------

def ScreenVision(Query):

    try:

        print("\nTaking screenshot...")

        ImagePath = TakeScreenshot()

        Base64Image = EncodeImage(
            ImagePath
        )

        print("Analyzing screen...")

        Response = client.chat.completions.create(

            model="qwen/qwen3.8-27b",

            messages=[

                {
                    "role": "system",
                    "content": """
You are Jarvis, a computer vision assistant.

You are looking at the user's current computer screen.

Answer the user's question based ONLY on what you can actually
see in the screenshot.

Be concise and natural because your answer will be spoken aloud.

If the user asks about code, explain the relevant code clearly.

If the user asks about an error, identify the error and explain
what is likely causing it.

If something cannot be read or is not visible, say so honestly.
Do not invent information.
"""
                },

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text": Query
                        },

                        {
                            "type": "image_url",

                            "image_url": {

                                "url":
                                f"data:image/png;base64,{Base64Image}"

                            }

                        }

                    ]

                }

            ],

            temperature=0.2,

            max_completion_tokens=700

        )

        Answer = (
            Response
            .choices[0]
            .message
            .content
            .strip()
        )

        return Answer

    except Exception as e:

        print(
            f"Screen Vision Error: {e}"
        )

        return (
            "Sorry sir, I couldn't analyze "
            "the screen."
        )


# ---------------- TEST ----------------

if __name__ == "__main__":

    while True:

        Query = input(
            "\nAsk about your screen: "
        ).strip()

        if Query.lower() in [
            "exit",
            "quit",
            "stop"
        ]:

            break

        Answer = ScreenVision(Query)

        print(
            "\nJarvis:",
            Answer
        )