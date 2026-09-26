import cohere
from rich import print
from dotenv import dotenv_values

# ---------------- LOAD ENVIRONMENT ----------------

env_vars = dotenv_values(".env")

CohereAPIKey = env_vars.get("CohereAPIKey")

co = cohere.Client(api_key=CohereAPIKey)

# ---------------- COMMANDS ----------------

funcs = [
    "exit",
    "general",
    "realtime",
    "open",
    "screen",
    "close",
    "play",
    "generate image",
    "system",
    "content",
    "google search",
    "youtube search",
    "reminder"
]

# ---------------- CHAT HISTORY ----------------

ChatHistory = [
    {
        "role": "User",
        "message": "how are you?"
    },
    {
        "role": "Chatbot",
        "message": "general how are you?"
    },

    {
        "role": "User",
        "message": "who is the prime minister of india?"
    },
    {
        "role": "Chatbot",
        "message": "realtime who is the prime minister of india?"
    },

    {
        "role": "User",
        "message": "what is today's weather?"
    },
    {
        "role": "Chatbot",
        "message": "realtime what is today's weather?"
    },

    {
        "role": "User",
        "message": "who won yesterday's cricket match?"
    },
    {
        "role": "Chatbot",
        "message": "realtime who won yesterday's cricket match?"
    },

    {
        "role": "User",
        "message": "what is the current bitcoin price?"
    },
    {
        "role": "Chatbot",
        "message": "realtime what is the current bitcoin price?"
    },

    {
        "role": "User",
        "message": "who is the current president of the united states?"
    },
    {
        "role": "Chatbot",
        "message": "realtime who is the current president of the united states?"
    },

    {
        "role": "User",
        "message": "google search best laptops for programming"
    },
    {
        "role": "Chatbot",
        "message": "google search best laptops for programming"
    },

    {
        "role": "User",
        "message": "search google for python tutorials"
    },
    {
        "role": "Chatbot",
        "message": "google search python tutorials"
    },

    {
        "role": "User",
        "message": "open chrome"
    },
    {
        "role": "Chatbot",
        "message": "open chrome"
    },

    {
        "role": "User",
        "message": "play interstellar on youtube"
    },
    {
        "role": "Chatbot",
        "message": "play interstellar on youtube"
    },

    {
        "role": "User",
        "message": "generate an image of a futuristic robot"
    },
    {
        "role": "Chatbot",
        "message": "generate image futuristic robot"
    }
]

# ---------------- SYSTEM PROMPT ----------------

VISION_SYSTEM_PROMPT = """
SCREEN CLASSIFICATION HAS PRIORITY:

If the user asks what Jarvis sees, what is visible, what the user is looking at, what is happening on the computer, or asks about an object/code/error/page currently displayed on the computer, classify it as screen.

Examples:
"What do you see now?" -> screen What do you see now?
"What do you see?" -> screen What do you see?
"What am I looking at?" -> screen What am I looking at?
"Can you see this?" -> screen Can you see this?
"What is this?" -> screen What is this?
"What's wrong here?" -> screen What's wrong here?
"Explain this." -> screen Explain this.
"Look at this." -> screen Look at this.

Do NOT use general for these requests.
You are the command classification system for Jarvis, a voice-controlled AI assistant.

Your job is to classify the user's request into one or more of these categories:

- general
- realtime
- open
- close
- play
- generate image
- system
- content
- google search
- youtube search
- reminder
- screen
- exit

IMPORTANT SCREEN RULE:

Use "screen" whenever the user is asking Jarvis to look at, understand, read, explain, or analyze something that is currently visible on the user's computer screen.

Classify based on the USER'S INTENT, NOT exact keywords.

Examples:

"What is on my screen?"
= screen What is on my screen?

"What do you see on my screen?"
= screen What do you see on my screen?

"What do you see now?"
= screen What do you see now?

"What can you see?"
= screen What can you see?

"What am I looking at?"
= screen What am I looking at?

"Look at my screen"
= screen Look at my screen

"Read this"
= screen Read this

"Explain this"
= screen Explain this

"What's happening here?"
= screen What's happening here?

"What's wrong with this code?"
= screen What's wrong with this code?

"Why am I getting this error?"
= screen Why am I getting this error?

"Can you see the problem?"
= screen Can you see the problem?

"Analyze what I'm looking at"
= screen Analyze what I'm looking at

"Explain the code I'm looking at"
= screen Explain the code I'm looking at

If the request requires seeing something currently displayed on the computer, use "screen".

Do NOT classify a request as "general" if answering it requires looking at the user's current screen.

GENERAL:

Use "general" for normal conversation, explanations, opinions, greetings, or questions that do not require seeing the user's screen.

REALTIME:

Use "realtime" for information that requires current or up-to-date information from the internet.

OPEN:

Use "open" for opening applications, websites, or files.

CLOSE:

Use "close" for closing applications or windows.

PLAY:

Use "play" for playing music, videos, or media.

GENERATE IMAGE:

Use "generate image" when the user asks Jarvis to create an image.

SYSTEM:

Use "system" for system controls such as volume, brightness, shutdown, restart, etc.

GOOGLE SEARCH:

Use "google search" when the user explicitly asks to search Google.

YOUTUBE SEARCH:

Use "youtube search" when the user explicitly asks to search YouTube.

EXIT:

Use "exit" when the user wants to stop or shut down Jarvis.

Return ONLY the classification commands.

Do not explain your answer.

Examples:

User: Hello Jarvis
Output: general Hello Jarvis

User: Who are you?
Output: general Who are you?

User: What is the current weather?
Output: realtime What is the current weather?

User: What is on my screen?
Output: screen What is on my screen?

User: What do you see now?
Output: screen What do you see now?

User: What am I looking at?
Output: screen What am I looking at?

User: Explain this code
Output: screen Explain this code

User: Why is this error happening?
Output: screen Why is this error happening?

User: Open Chrome
Output: open Chrome

User: Play Interstellar
Output: play Interstellar

User: Generate an image of a futuristic city
Output: generate image futuristic city

User: Increase volume
Output: system Increase volume

User: Search Google for Python tutorials
Output: google search Python tutorials
"""
# ---------------- MODEL FUNCTION ----------------

messages = []


def FirstLayerDMM(prompt="test"):

    messages.append({
        "role": "User",
        "message": prompt
    })

    stream = co.chat_stream(
        model="command-a-03-2025",
        message=prompt,
        temperature=0,
        chat_history=ChatHistory,
        prompt_truncation="OFF",
        connectors=[],
        preamble=VISION_SYSTEM_PROMPT
    )

    Answer = ""

    for response in stream:

        if response.event_type == "text-generation":
            Answer += response.text

    Answer = Answer.strip()

    # Clean response
    Answer = Answer.replace("[", "")
    Answer = Answer.replace("]", "")
    Answer = Answer.replace('"', "")
    Answer = Answer.replace("'", "")

    Decision = [
        command.strip()
        for command in Answer.split(",")
        if command.strip()
    ]

    return Decision

# ---------------- TEST ----------------

if __name__ == "__main__":

    while True:

        Query = input(">>> ")

        if Query.lower() in ["exit", "quit"]:
            break

        print(FirstLayerDMM(Query))