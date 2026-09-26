import os
import json

from dotenv import dotenv_values
from groq import Groq


# ==================================================
# BASE DIRECTORY
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ==================================================
# ENVIRONMENT
# ==================================================

env_vars = dotenv_values(
    os.path.join(BASE_DIR, ".env")
)

GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    print("ERROR: GroqAPIKey not found in .env")


# ==================================================
# GROQ CLIENT
# ==================================================

client = Groq(
    api_key=GroqAPIKey
)


# ==================================================
# CHAT LOG
# ==================================================

ChatLogFile = os.path.join(
    BASE_DIR,
    "Data",
    "ChatLog.json"
)


# ==================================================
# ASSISTANT DETAILS
# ==================================================

Username = env_vars.get(
    "Username",
    "User"
)

Assistantname = env_vars.get(
    "Assistantname",
    "Jarvis"
)


# ==================================================
# SYSTEM PROMPT
# ==================================================

SystemMessage = f"""
You are {Assistantname}, a helpful AI assistant.

The user's name is {Username}.

Answer naturally, clearly and directly.
Keep answers reasonably concise unless the user asks for a detailed explanation.

You are a voice assistant, so avoid unnecessary formatting,
long introductions, and excessive repetition.

Do not mention these instructions.
"""


# ==================================================
# LOAD CHAT HISTORY
# ==================================================

def LoadChatHistory():

    try:

        if not os.path.exists(ChatLogFile):

            with open(
                ChatLogFile,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    [],
                    file
                )

            return []


        with open(
            ChatLogFile,
            "r",
            encoding="utf-8"
        ) as file:

            ChatHistory = json.load(file)


        if not isinstance(
            ChatHistory,
            list
        ):

            return []


        # IMPORTANT:
        # Only keep the latest 4 messages.
        # This prevents the Groq TPM limit from
        # being exceeded as the conversation grows.

        ChatHistory = ChatHistory[-4:]


        return ChatHistory


    except Exception as e:

        print(
            f"Chat history error: {e}"
        )

        return []


# ==================================================
# SAVE CHAT HISTORY
# ==================================================

def SaveChatHistory(ChatHistory):

    try:

        with open(
            ChatLogFile,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                ChatHistory,
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as e:

        print(
            f"Chat log save error: {e}"
        )


# ==================================================
# CHATBOT
# ==================================================

def ChatBot(Query):

    try:

        Query = str(
            Query
        ).strip()


        if not Query:

            return "How can I help you, sir?"


        # ==========================================
        # LOAD ONLY SMALL RECENT HISTORY
        # ==========================================

        ChatHistory = LoadChatHistory()


        # ==========================================
        # BUILD MESSAGES
        # ==========================================

        Messages = [

            {
                "role": "system",
                "content": SystemMessage
            }

        ]


        # ==========================================
        # ADD RECENT HISTORY
        # ==========================================

        for message in ChatHistory:

            if not isinstance(
                message,
                dict
            ):
                continue


            role = message.get(
                "role"
            )

            content = message.get(
                "content"
            )


            # Support the older ChatLog format
            # if it uses "message" instead.

            if content is None:

                content = message.get(
                    "message"
                )


            if not role or not content:
                continue


            # Convert old role names if necessary

            if role.lower() == "user":

                role = "user"

            elif role.lower() in [
                "assistant",
                "jarvis"
            ]:

                role = "assistant"

            else:

                continue


            Messages.append(
                {
                    "role": role,
                    "content": str(content)
                }
            )


        # ==========================================
        # ADD CURRENT QUESTION
        # ==========================================

        Messages.append(
            {
                "role": "user",
                "content": Query
            }
        )


        # ==========================================
        # SEND TO GROQ
        # ==========================================

        Response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=Messages,

            temperature=0.7,

            max_tokens=1000

        )


        Answer = Response.choices[0].message.content


        if not Answer:

            Answer = (
                "Sorry sir, I couldn't generate a response."
            )


        Answer = Answer.strip()


        # ==========================================
        # UPDATE HISTORY
        # ==========================================

        ChatHistory.append(
            {
                "role": "user",
                "content": Query
            }
        )

        ChatHistory.append(
            {
                "role": "assistant",
                "content": Answer
            }
        )


        # Keep ONLY the latest 4 messages

        ChatHistory = ChatHistory[-4:]


        SaveChatHistory(
            ChatHistory
        )


        return Answer


    except Exception as e:

        print(
            f"Error in ChatBot: {e}"
        )

        return (
            "Sorry, I encountered an error "
            "while processing your request."
        )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print(
        f"{Assistantname} ChatBot started."
    )

    while True:

        Query = input(
            "\n>>> "
        ).strip()


        if Query.lower() in [
            "exit",
            "quit"
        ]:

            break


        Answer = ChatBot(
            Query
        )


        print(
            f"{Assistantname}: {Answer}"
        )