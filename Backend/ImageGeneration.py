import asyncio
from random import randint
from PIL import Image
from dotenv import get_key
from huggingface_hub import InferenceClient
import os
from time import sleep


# --------------------------------------------------
# Open generated images
# --------------------------------------------------

def open_images(prompt):

    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")

    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:

        image_path = os.path.join(folder_path, jpg_file)

        try:

            img = Image.open(image_path)

            print(f"Opening image: {image_path}")

            img.show()

            sleep(1)

        except IOError:

            print(f"Unable to open {image_path}")


# --------------------------------------------------
# Hugging Face API
# --------------------------------------------------

HuggingFaceAPIKey = get_key(".env", "HuggingFaceAPIKey")

if not HuggingFaceAPIKey:

    print("ERROR: HuggingFaceAPIKey not found in .env")

    raise SystemExit


client = InferenceClient(
    api_key=HuggingFaceAPIKey
)


# --------------------------------------------------
# Generate one image
# --------------------------------------------------

async def query(prompt, seed):

    try:

        image = await asyncio.to_thread(
            client.text_to_image,
            prompt=prompt,
            model="stabilityai/stable-diffusion-3-medium-diffusers",
            seed=seed
        )

        return image

    except Exception as e:

        print(f"Image generation error: {e}")

        return None


# --------------------------------------------------
# Generate 4 images simultaneously
# --------------------------------------------------

async def generate_images(prompt: str):

    tasks = []

    for _ in range(4):

        seed = randint(0, 1000000)

        task = asyncio.create_task(
            query(
                prompt,
                seed
            )
        )

        tasks.append(task)

    Images = await asyncio.gather(*tasks)

    SafePrompt = prompt.replace(" ", "_")

    Generated = 0

    for i, image in enumerate(Images):

        if image is None:

            print(f"Image {i + 1} failed.")

            continue

        try:

            image_path = fr"Data\{SafePrompt}{i + 1}.jpg"

            image.save(
                image_path,
                format="JPEG"
            )

            print(
                f"Image {i + 1} saved: {image_path}"
            )

            Generated += 1

        except Exception as e:

            print(
                f"Error saving image {i + 1}: {e}"
            )

    return Generated


# --------------------------------------------------
# Main image-generation function
# --------------------------------------------------

def GenerateImages(prompt: str):

    try:

        Generated = asyncio.run(
            generate_images(prompt)
        )

        if Generated == 0:

            print("No images were generated.")

            return False

        print(
            f"{Generated}/4 images generated successfully."
        )

        open_images(prompt)

        return True

    except Exception as e:

        print(
            f"GenerateImages ERROR: {e}"
        )

        return False


# --------------------------------------------------
# Main loop
# --------------------------------------------------

while True:

    try:

        with open(
            r"Frontend\Files\ImageGeneration.data",
            "r"
        ) as f:

            Data = f.read().strip()


        if not Data:

            sleep(1)

            continue


        Prompt, Status = Data.split(",", 1)

        Prompt = Prompt.strip()
        Status = Status.strip()


        if Status == "True":

            print(
                f"Generating Images for: {Prompt}"
            )


            ImageStatus = GenerateImages(
                prompt=Prompt
            )


            # Reset status AFTER the attempt
            with open(
                r"Frontend\Files\ImageGeneration.data",
                "w"
            ) as f:

                f.write("False,False")


            if ImageStatus:

                print(
                    "Image generation completed."
                )

            else:

                print(
                    "Image generation failed."
                )


            # Wait for the next request
            sleep(1)


        else:

            sleep(1)


    except ValueError:

        print(
            "ERROR: ImageGeneration.data must contain:"
        )

        print(
            "prompt,True"
        )

        sleep(1)


    except KeyboardInterrupt:

        print(
            "\nImage Generation stopped."
        )

        break


    except Exception as e:

        print(
            f"MAIN LOOP ERROR: {e}"
        )

        sleep(2)