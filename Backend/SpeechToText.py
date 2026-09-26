from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from mtranslate import translate
from dotenv import dotenv_values

from time import sleep

import os


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

InputLanguage = env_vars.get(
    "InputLanguage",
    "en"
)


# ==================================================
# HTML SPEECH RECOGNITION
# ==================================================

HtmlCode = '''
<!DOCTYPE html>

<html lang="en">

<head>

<title>Speech Recognition</title>

</head>

<body>

<button id="start" onclick="startRecognition()">
Start Recognition
</button>

<button id="end" onclick="stopRecognition()">
Stop Recognition
</button>

<p id="output"></p>

<script>

const output = document.getElementById('output');

let recognition = null;

let recognizing = false;


function startRecognition() {

    recognition =
        new webkitSpeechRecognition() ||
        new SpeechRecognition();

    recognition.lang = '';

    recognition.continuous = true;

    recognition.interimResults = false;


    recognition.onresult = function(event) {

        const transcript =
            event.results[
                event.results.length - 1
            ][0].transcript;

        output.textContent += transcript;

    };


    recognition.onend = function() {

        if (recognizing) {

            try {

                recognition.start();

            } catch(e) {

            }

        }

    };


    recognizing = true;

    recognition.start();

}


function stopRecognition() {

    recognizing = false;

    if (recognition) {

        try {

            recognition.stop();

        } catch(e) {

        }

    }

    output.innerHTML = "";

}

</script>

</body>

</html>
'''


HtmlCode = HtmlCode.replace(
    "recognition.lang = '';",
    f"recognition.lang = '{InputLanguage}';"
)


# ==================================================
# CREATE HTML FILE
# ==================================================

VoiceFilePath = os.path.join(
    BASE_DIR,
    "Data",
    "Voice.html"
)


with open(
    VoiceFilePath,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        HtmlCode
    )


# ==================================================
# CHROME
# ==================================================

chrome_options = Options()

chrome_options.add_argument(
    "--log-level=3"
)

chrome_options.add_argument(
    "--use-fake-ui-for-media-stream"
)

chrome_options.add_argument(
    "--use-fake-device-for-media-stream"
)

chrome_options.add_argument(
    "--headless=new"
)


service = Service(
    ChromeDriverManager().install()
)


driver = webdriver.Chrome(
    service=service,
    options=chrome_options
)


driver.get(
    "file:///"
    +
    VoiceFilePath.replace(
        "\\",
        "/"
    )
)


# ==================================================
# QUERY MODIFIER
# ==================================================

def QueryModifier(Query):

    new_query = Query.lower().strip()

    if not new_query:

        return ""


    query_words = new_query.split()


    question_words = [

        "how",
        "what",
        "who",
        "where",
        "when",
        "why",
        "which",
        "whose",
        "whom",
        "can you",
        "what's",
        "where's",
        "how's"

    ]


    if any(
        word + " " in new_query
        for word in question_words
    ):

        if query_words[-1][-1] in [
            ".",
            "?",
            "!"
        ]:

            new_query = (
                new_query[:-1]
                + "?"
            )

        else:

            new_query += "?"

    else:

        if query_words[-1][-1] in [
            ".",
            "?",
            "!"
        ]:

            new_query = (
                new_query[:-1]
                + "."
            )

        else:

            new_query += "."


    return new_query.capitalize()


# ==================================================
# GET MICROPHONE STATUS
# ==================================================

def GetMicrophoneStatus():

    try:

        MicFile = os.path.join(
            BASE_DIR,
            "Frontend",
            "Files",
            "Mic.data"
        )


        with open(
            MicFile,
            "r",
            encoding="utf-8"
        ) as file:

            Status = file.read().strip()


        return Status.lower()


    except Exception:

        # Default = microphone ON
        return "false"


# ==================================================
# SPEECH RECOGNITION
# ==================================================

def SpeechRecognition():

    try:

        # ------------------------------------------
        # CHECK MIC BEFORE STARTING
        # ------------------------------------------

        while GetMicrophoneStatus() == "true":

            print(
                "Microphone is OFF..."
            )

            sleep(0.2)


        # ------------------------------------------
        # START RECOGNITION
        # ------------------------------------------

        driver.find_element(
            by=By.ID,
            value="start"
        ).click()


        print(
            "Listening..."
        )


        while True:

            # ======================================
            # CHECK MICROPHONE BUTTON
            # ======================================

            if GetMicrophoneStatus() == "true":

                print(
                    "Microphone turned OFF."
                )


                try:

                    driver.find_element(
                        by=By.ID,
                        value="end"
                    ).click()

                except Exception:

                    pass


                return ""


            # ======================================
            # READ SPEECH
            # ======================================

            try:

                Text = driver.find_element(
                    by=By.ID,
                    value="output"
                ).text


                if Text:

                    driver.find_element(
                        by=By.ID,
                        value="end"
                    ).click()


                    return QueryModifier(
                        Text
                    )


                sleep(
                    0.1
                )


            except Exception:

                sleep(
                    0.1
                )


    except Exception as e:

        print(
            f"Speech Recognition Error: {e}"
        )

        return ""


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    while True:

        Query = SpeechRecognition()


        if Query:

            print(
                f"You Said: {Query}"
            )


        if Query.lower() in [
            "exit.",
            "quit."
        ]:

            break