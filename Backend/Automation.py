from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
from ddgs import DDGS

import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import urllib.parse


# ==================================================
# ENVIRONMENT
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

env_vars = dotenv_values(
    os.path.join(BASE_DIR, ".env")
)

GroqAPIKey = env_vars.get("GroqAPIKey")


# ==================================================
# GROQ
# ==================================================

client = Groq(
    api_key=GroqAPIKey
)


# ==================================================
# OPEN WINDOWS APP
# ==================================================

def OpenWindowsApp(app):

    app = app.strip()
    app_lower = app.lower()

    # Windows URI protocols
    app_protocols = {

        "whatsapp": "whatsapp:",

        "spotify": "spotify:",

        "calculator": "calculator:",
        "calc": "calculator:",

        "settings": "ms-settings:",

        "mail": "outlookmail:",

        "outlook": "outlook:",

    }


    if app_lower not in app_protocols:

        return False


    try:

        os.startfile(
            app_protocols[app_lower]
        )

        print(
            f"Opened app: {app}"
        )

        return True


    except Exception as e:

        print(
            f"Windows app error: {e}"
        )

        return False


# ==================================================
# FIND WEBSITE
# ==================================================

def FindWebsite(query):

    try:

        print(
            f"Finding website for: {query}"
        )


        search_query = (
            f"{query} official website"
        )


        with DDGS() as ddgs:

            results = ddgs.text(
                search_query,
                max_results=5
            )


            for result in results:

                url = result.get(
                    "href",
                    ""
                )


                if not url:
                    continue


                # Ignore search/social junk where possible
                blocked_domains = [
                    "youtube.com",
                    "facebook.com",
                    "instagram.com",
                    "reddit.com",
                    "wikipedia.org"
                ]


                domain = urllib.parse.urlparse(
                    url
                ).netloc.lower()


                if any(
                    blocked in domain
                    for blocked in blocked_domains
                ):

                    continue


                print(
                    f"Website found: {url}"
                )

                return url


    except Exception as e:

        print(
            f"Website search error: {e}"
        )


    return None


# ==================================================
# OPEN APP / WEBSITE
# ==================================================

def OpenApp(app):

    app = app.strip()


    if not app:

        return False


    # ==================================================
    # 1. TRY WINDOWS APP
    # ==================================================

    if OpenWindowsApp(app):

        return True


    # ==================================================
    # 2. DIRECT URL
    # ==================================================

    if (
        app.lower().startswith("http://")
        or
        app.lower().startswith("https://")
    ):

        try:

            webbrowser.open(
                app
            )

            return True

        except Exception as e:

            print(
                f"URL error: {e}"
            )

            return False


    # ==================================================
    # 3. DOMAIN ALREADY GIVEN
    # ==================================================

    if (
        "." in app
        and " " not in app
    ):

        try:

            url = (
                "https://"
                + app
            )

            webbrowser.open(
                url
            )

            print(
                f"Opening website: {url}"
            )

            return True

        except Exception as e:

            print(
                f"Domain error: {e}"
            )


    # ==================================================
    # 4. FIND WEBSITE DYNAMICALLY
    # ==================================================

    Website = FindWebsite(
        app
    )


    if Website:

        try:

            webbrowser.open(
                Website
            )

            return True

        except Exception as e:

            print(
                f"Website opening error: {e}"
            )


    # ==================================================
    # 5. FALLBACK TO WINDOWS APPLICATION
    # ==================================================

    try:

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "",
                app
            ],
            shell=True
        )

        print(
            f"Trying Windows application: {app}"
        )

        return True


    except Exception as e:

        print(
            f"Application error: {e}"
        )

        return False


# ==================================================
# PLAY YOUTUBE
# ==================================================

def PlayYoutube(query):

    try:

        query = query.strip()

        if not query:
            return False

        playonyt(
            query
        )

        return True

    except Exception as e:

        print(
            f"YouTube error: {e}"
        )

        return False


# ==================================================
# GOOGLE SEARCH
# ==================================================

def GoogleSearch(query):

    try:

        query = query.strip()

        if not query:
            return False

        search(
            query
        )

        return True

    except Exception as e:

        print(
            f"Google search error: {e}"
        )

        return False


# ==================================================
# SYSTEM COMMANDS
# ==================================================

def SystemCommand(command):

    command = command.lower().strip()


    # ------------------------------
    # Volume Up
    # ------------------------------

    if command == "volume up":

        for _ in range(5):

            keyboard.press_and_release(
                "volume up"
            )

        return True


    # ------------------------------
    # Volume Down
    # ------------------------------

    if command == "volume down":

        for _ in range(5):

            keyboard.press_and_release(
                "volume down"
            )

        return True


    # ------------------------------
    # Mute
    # ------------------------------

    if command == "mute":

        keyboard.press_and_release(
            "volume mute"
        )

        return True


    # ------------------------------
    # Unmute
    # ------------------------------

    if command == "unmute":

        keyboard.press_and_release(
            "volume mute"
        )

        return True


    # ------------------------------
    # Pause
    # ------------------------------

    if command == "pause":

        keyboard.press_and_release(
            "play/pause media"
        )

        return True


    # ------------------------------
    # Next
    # ------------------------------

    if command == "next":

        keyboard.press_and_release(
            "next track"
        )

        return True


    # ------------------------------
    # Previous
    # ------------------------------

    if command == "previous":

        keyboard.press_and_release(
            "previous track"
        )

        return True


    # ------------------------------
    # Shutdown
    # ------------------------------

    if command == "shutdown":

        os.system(
            "shutdown /s /t 0"
        )

        return True


    # ------------------------------
    # Restart
    # ------------------------------

    if command == "restart":

        os.system(
            "shutdown /r /t 0"
        )

        return True


    return False


# ==================================================
# MAIN AUTOMATION FUNCTION
# ==================================================

def Automation(Query):

    try:

        Query = Query.strip()


        if not Query:

            return False


        QueryLower = Query.lower()


        print(
            f"\nAutomation command: {Query}"
        )


        # ==================================================
        # OPEN
        # ==================================================

        if QueryLower.startswith(
            "open "
        ):

            App = Query[
                len("open "):
            ].strip()


            return OpenApp(
                App
            )


        # ==================================================
        # CLOSE
        # ==================================================

        if QueryLower.startswith(
            "close "
        ):

            App = Query[
                len("close "):
            ].strip()


            try:

                os.system(
                    f'taskkill /IM "{App}.exe" /F'
                )

                return True

            except Exception as e:

                print(
                    f"Close error: {e}"
                )

                return False


        # ==================================================
        # PLAY
        # ==================================================

        if QueryLower.startswith(
            "play "
        ):

            Song = Query[
                len("play "):
            ].strip()


            return PlayYoutube(
                Song
            )


        # ==================================================
        # GOOGLE SEARCH
        # ==================================================

        if QueryLower.startswith(
            "google search "
        ):

            SearchQuery = Query[
                len("google search "):
            ].strip()


            return GoogleSearch(
                SearchQuery
            )


        # ==================================================
        # YOUTUBE SEARCH
        # ==================================================

        if QueryLower.startswith(
            "youtube search "
        ):

            SearchQuery = Query[
                len("youtube search "):
            ].strip()


            try:

                url = (
                    "https://www.youtube.com/results?search_query="
                    +
                    urllib.parse.quote(
                        SearchQuery
                    )
                )

                webbrowser.open(
                    url
                )

                return True

            except Exception as e:

                print(
                    f"YouTube search error: {e}"
                )

                return False


        # ==================================================
        # SYSTEM
        # ==================================================

        if SystemCommand(
            QueryLower
        ):

            return True


        # ==================================================
        # DEFAULT
        # ==================================================

        return False


    except Exception as e:

        print(
            f"Automation error: {e}"
        )

        return False


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    while True:

        Query = input(
            "\n>>> "
        ).strip()


        if Query.lower() in [
            "exit",
            "quit"
        ]:

            break


        Result = Automation(
            Query
        )


        print(
            f"Result: {Result}"
        )