from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech, StopTalking
from Backend.ScreenVision import ScreenVision

from dotenv import dotenv_values

from time import sleep

import subprocess
import threading
import os


# ==================================================
# SCREEN MODE
# ==================================================

ScreenMode = False


# ==================================================
# ENVIRONMENT
# ==================================================

env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")


# ==================================================
# DEFAULT MESSAGE
# ==================================================

DefaultMessage = f"""
{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?
"""


# ==================================================
# SUBPROCESSES
# ==================================================

subprocesses = []


# ==================================================
# GUI
# ==================================================

def GraphicalUserInterface():

    process = subprocess.Popen(
        [
            os.path.join(
                ".venv",
                "Scripts",
                "python.exe"
            ),
            r"Frontend\GUI.py"
        ]
    )

    subprocesses.append(process)

    process.wait()


# ==================================================
# IMAGE GENERATION
# ==================================================

def ImageGeneration():

    process = subprocess.Popen(
        [
            os.path.join(
                ".venv",
                "Scripts",
                "python.exe"
            ),
            r"Backend\ImageGeneration.py"
        ]
    )

    subprocesses.append(process)

    process.wait()


# ==================================================
# SHOW DEFAULT MESSAGE
# ==================================================

def ShowDefaultMessage():

    try:

        with open(
            r"Frontend\Files\Responses.data",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(DefaultMessage)

    except Exception as e:

        print(
            f"Error writing default message: {e}"
        )


# ==================================================
# SET ASSISTANT STATUS
# ==================================================

def SetAssistantStatus(Status):

    try:

        with open(
            r"Frontend\Files\Status.data",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(Status)

    except Exception as e:

        print(
            f"Status error: {e}"
        )


# ==================================================
# SHOW RESPONSE
# ==================================================

def ShowTextToScreen(Text):

    try:

        with open(
            r"Frontend\Files\Responses.data",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(Text)

    except Exception as e:

        print(
            f"Response error: {e}"
        )


# ==================================================
# IMAGE GENERATION TRIGGER
# ==================================================

def TriggerImageGeneration(Prompt):

    try:

        with open(
            r"Frontend\Files\ImageGeneration.data",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                f"{Prompt},True"
            )

        return True

    except Exception as e:

        print(
            f"Image trigger error: {e}"
        )

        return False


# ==================================================
# COMMAND PROCESSOR
# ==================================================

def ProcessQuery(Query):

    global ScreenMode

    Query = Query.strip()

    if not Query:
        return

    QueryLower = Query.lower()


    # ==================================================
    # STOP TALKING
    # ==================================================

    if QueryLower in [
        "stop talking",
        "stop speaking",
        "be quiet",
        "shut up",
        "silence"
    ]:

        StopTalking()

        SetAssistantStatus(
            "Listening..."
        )

        return


    # ==================================================
    # STOP SCREEN MODE
    # ==================================================

    if QueryLower in [
        "stop screen mode",
        "exit screen mode",
        "stop looking at my screen",
        "stop looking at the screen"
    ]:

        ScreenMode = False

        Response = "Screen mode disabled, sir."

        ShowTextToScreen(Response)

        TextToSpeech(Response)

        return


    # ==================================================
    # SCREEN VISION
    # ==================================================

    ScreenTriggers = [

        "what do you see",

        "what can you see",

        "what am i looking at",

        "what am i seeing",

        "what is on my screen",

        "what's on my screen",

        "look at my screen",

        "look at the screen",

        "look at this",

        "read my screen",

        "read the screen",

        "read this",

        "explain this",

        "analyze this",

        "check my screen",

        "check the screen"

    ]


    # Commands that must NEVER be intercepted by screen mode

    CommandPrefixes = [

        "open ",
        "close ",
        "play ",
        "google search ",
        "youtube search ",
        "generate image ",
        "volume ",
        "mute",
        "unmute",
        "pause",
        "next",
        "previous",
        "shutdown",
        "restart"

    ]


    # ==================================================
    # DIRECT SCREEN REQUEST
    # ==================================================

    if any(
        Trigger in QueryLower
        for Trigger in ScreenTriggers
    ):

        ScreenMode = True

        SetAssistantStatus(
            "Looking at screen..."
        )

        Answer = ScreenVision(Query)

        print(
            "Jarvis:",
            Answer
        )

        ShowTextToScreen(
            Answer
        )

        SetAssistantStatus(
            "Speaking..."
        )

        TextToSpeech(
            Answer
        )

        return


    # ==================================================
    # FOLLOW-UP QUESTIONS WHILE IN SCREEN MODE
    # ==================================================

    if (
        ScreenMode
        and len(Query.split()) <= 12
        and not any(
            QueryLower.startswith(prefix)
            for prefix in CommandPrefixes
        )
    ):

        SetAssistantStatus(
            "Looking at screen..."
        )

        Answer = ScreenVision(Query)

        print(
            "Jarvis:",
            Answer
        )

        ShowTextToScreen(
            Answer
        )

        SetAssistantStatus(
            "Speaking..."
        )

        TextToSpeech(
            Answer
        )

        return


    # ==================================================
    # DMM
    # ==================================================

    Decision = FirstLayerDMM(Query)

    if isinstance(Decision, str):

        Decision = [
            Decision
        ]

    print(
        "DMM:",
        Decision
    )


    # ==================================================
    # IMAGE GENERATION
    # ==================================================

    for command in Decision:

        if command.startswith(
            "generate image"
        ):

            Prompt = command.replace(
                "generate image",
                "",
                1
            ).strip()


            if not Prompt:

                Prompt = Query.replace(
                    "generate image",
                    "",
                    1
                ).strip()


            if TriggerImageGeneration(
                Prompt
            ):

                Response = (
                    f"Generating images of {Prompt}, sir."
                )

                ShowTextToScreen(
                    Response
                )

                SetAssistantStatus(
                    "Generating images..."
                )

                TextToSpeech(
                    Response
                )

            else:

                Response = (
                    "Sorry sir, I couldn't start image generation."
                )

                ShowTextToScreen(
                    Response
                )

                TextToSpeech(
                    Response
                )

            return


    # ==================================================
    # AUTOMATION
    # ==================================================

    AutomationCommands = [

        "open",
        "close",
        "play",
        "google search",
        "youtube search",

        "system",

        "mute",
        "unmute",

        "volume up",
        "volume down",

        "pause",
        "next",
        "previous"

    ]


    for command in Decision:

        if any(
            command.startswith(x)
            for x in AutomationCommands
        ):

            SetAssistantStatus(
                "Executing..."
            )

            try:

                Result = Automation(
                    command
                )

                print(
                    "Automation:",
                    Result
                )


                if Result:

                    Response = (
                        "Done, sir."
                    )

                else:

                    Response = (
                        "I couldn't complete that command, sir."
                    )


                ShowTextToScreen(
                    Response
                )

                TextToSpeech(
                    Response
                )


            except Exception as e:

                print(
                    f"Automation error: {e}"
                )

                Response = (
                    "Sorry sir, I couldn't complete that command."
                )

                ShowTextToScreen(
                    Response
                )

                TextToSpeech(
                    Response
                )

            return


    # ==================================================
    # REALTIME SEARCH
    # ==================================================

    for command in Decision:

        if command.startswith(
            "realtime"
        ):

            SetAssistantStatus(
                "Searching..."
            )

            try:

                SearchQuery = command.replace(
                    "realtime",
                    "",
                    1
                ).strip()


                Answer = RealtimeSearchEngine(
                    SearchQuery
                )

                Answer = str(
                    Answer
                )


                print(
                    "Jarvis:",
                    Answer
                )


                ShowTextToScreen(
                    Answer
                )


                SetAssistantStatus(
                    "Speaking..."
                )


                TextToSpeech(
                    Answer
                )


            except Exception as e:

                print(
                    f"Realtime search error: {e}"
                )

                Response = (
                    "Sorry sir, I couldn't search for that information."
                )

                ShowTextToScreen(
                    Response
                )

                TextToSpeech(
                    Response
                )

            return


    # ==================================================
    # GOOGLE SEARCH
    # ==================================================

    for command in Decision:

        if command.startswith(
            "google search"
        ):

            SetAssistantStatus(
                "Searching Google..."
            )

            try:

                Result = Automation(
                    command
                )


                if Result:

                    Response = (
                        "I have opened the Google search, sir."
                    )

                else:

                    Response = (
                        "I couldn't open the Google search."
                    )


                ShowTextToScreen(
                    Response
                )

                TextToSpeech(
                    Response
                )


            except Exception as e:

                print(
                    f"Google search error: {e}"
                )

            return


    # ==================================================
    # YOUTUBE SEARCH
    # ==================================================

    for command in Decision:

        if command.startswith(
            "youtube search"
        ):

            SetAssistantStatus(
                "Searching YouTube..."
            )

            try:

                Result = Automation(
                    command
                )


                if Result:

                    Response = (
                        "I have opened YouTube, sir."
                    )

                else:

                    Response = (
                        "I couldn't open YouTube."
                    )


                ShowTextToScreen(
                    Response
                )

                TextToSpeech(
                    Response
                )


            except Exception as e:

                print(
                    f"YouTube search error: {e}"
                )

            return


    # ==================================================
    # GENERAL CHAT
    # ==================================================

    for command in Decision:

        if command.startswith(
            "general"
        ):

            SetAssistantStatus(
                "Thinking..."
            )

            try:

                ChatQuery = command.replace(
                    "general",
                    "",
                    1
                ).strip()


                Answer = ChatBot(
                    ChatQuery
                )

                Answer = str(
                    Answer
                )


                print(
                    "Jarvis:",
                    Answer
                )


                ShowTextToScreen(
                    Answer
                )


                SetAssistantStatus(
                    "Speaking..."
                )


                TextToSpeech(
                    Answer
                )


            except Exception as e:

                print(
                    f"Chatbot error: {e}"
                )

                Response = (
                    "Sorry sir, I couldn't process that."
                )

                ShowTextToScreen(
                    Response
                )

                TextToSpeech(
                    Response
                )

            return


    # ==================================================
    # FALLBACK
    # ==================================================

    SetAssistantStatus(
        "Thinking..."
    )

    try:

        Answer = ChatBot(
            Query
        )

        Answer = str(
            Answer
        )


        ShowTextToScreen(
            Answer
        )


        TextToSpeech(
            Answer
        )


    except Exception as e:

        print(
            f"Fallback error: {e}"
        )


# ==================================================
# MAIN LOOP
# ==================================================

def MainExecution():

    ShowDefaultMessage()

    SetAssistantStatus(
        "Available"
    )


    # ==================================================
    # START GUI
    # ==================================================

    gui_thread = threading.Thread(
        target=GraphicalUserInterface,
        daemon=True
    )

    gui_thread.start()


    sleep(2)


    # ==================================================
    # START IMAGE GENERATION BACKEND
    # ==================================================

    image_thread = threading.Thread(
        target=ImageGeneration,
        daemon=True
    )

    image_thread.start()


    sleep(2)


    # ==================================================
    # MAIN VOICE LOOP
    # ==================================================

    while True:

        try:

            SetAssistantStatus(
                "Listening..."
            )


            Query = SpeechRecognition()


            if not Query:
                continue


            Query = Query.strip()


            print(
                f"\nYou said: {Query}"
            )


            # ==================================================
            # EXIT
            # ==================================================

            if Query.lower() in [
                "exit",
                "quit",
                "goodbye",
                "shutdown jarvis"
            ]:

                SetAssistantStatus(
                    "Shutting down..."
                )


                Response = (
                    "Goodbye sir."
                )


                ShowTextToScreen(
                    Response
                )


                TextToSpeech(
                    Response
                )


                sleep(2)

                break


            # ==================================================
            # PROCESS COMMAND
            # ==================================================

            ProcessQuery(
                Query
            )


            SetAssistantStatus(
                "Available"
            )


        except KeyboardInterrupt:

            print(
                "\nJarvis stopped."
            )

            break


        except Exception as e:

            print(
                f"MAIN ERROR: {e}"
            )

            SetAssistantStatus(
                "Available"
            )

            sleep(1)


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    MainExecution()