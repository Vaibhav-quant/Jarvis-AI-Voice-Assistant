import pygame
import random
import asyncio
import edge_tts
import os
import re
from dotenv import dotenv_values


# ==================================================
# ENVIRONMENT
# ==================================================

env_vars = dotenv_values(".env")

AssistantVoice = env_vars.get("AssistantVoice")


# ==================================================
# STOP CONTROL
# ==================================================

StopSpeech = False


def StopTalking():
    global StopSpeech

    StopSpeech = True

    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass


def ResetSpeech():
    global StopSpeech

    StopSpeech = False


# ==================================================
# TEXT TO AUDIO FILE
# ==================================================

async def TextToAudioFile(text) -> None:

    file_path = r"Data\speech.mp3"

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    communicate = edge_tts.Communicate(
        text,
        AssistantVoice,
        pitch="-8Hz",
        rate="-5%"
    )

    await communicate.save(file_path)


# ==================================================
# TEXT TO SPEECH
# ==================================================

def TTS(Text, func=lambda r=None: True):

    global StopSpeech

    ResetSpeech()

    while True:

        try:

            # Generate speech
            asyncio.run(
                TextToAudioFile(Text)
            )

            # If stopped while generating
            if StopSpeech:
                return False

            # Initialize pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Load generated speech
            pygame.mixer.music.load(
                r"Data\speech.mp3"
            )

            # Play speech
            pygame.mixer.music.play()

            clock = pygame.time.Clock()

            # Keep checking while audio is playing
            while pygame.mixer.music.get_busy():

                # User requested stop
                if StopSpeech:
                    pygame.mixer.music.stop()
                    return False

                # Existing callback
                try:
                    if not func():
                        pygame.mixer.music.stop()
                        return False
                except Exception:
                    pass

                clock.tick(10)

            return True

        except Exception as e:

            print(
                f"Error in TTS: {e}"
            )

            return False

        finally:

            try:

                if pygame.mixer.get_init():

                    pygame.mixer.music.stop()

                    pygame.mixer.quit()

            except Exception as e:

                print(
                    f"Error in finally block: {e}"
                )


# ==================================================
# HIGHER LEVEL TEXT TO SPEECH
# ==================================================
def TextToSpeech(Text, func=lambda r=None: True):

    Text = str(Text)

    # Remove Markdown formatting
    Text = re.sub(r'\*\*(.*?)\*\*', r'\1', Text)
    Text = re.sub(r'\*(.*?)\*', r'\1', Text)
    Text = re.sub(r'`(.*?)`', r'\1', Text)

    # Remove remaining asterisks
    Text = Text.replace("*", "")

    # Remove markdown headings
    Text = re.sub(r'^#+\s*', '', Text, flags=re.MULTILINE)

    # Remove markdown bullet markers
    Text = re.sub(r'^\s*[-•]\s+', '', Text, flags=re.MULTILINE)

    # Clean excessive whitespace
    Text = re.sub(r'\s+', ' ', Text).strip()

    TTS(
        Text,
        func
    )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    while True:

        Text = input(
            "Enter the text: "
        )

        if Text.lower() == "exit":
            break

        TextToSpeech(Text)