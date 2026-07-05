import os
import json
import requests
import yadisk

FOLDER_NAME = "PYAPI-152" #Folder name

def get_image_with_text(text):
    url = "https://cataas.com/cat/says"
    params = {'text': text}

    try:
        print(f"Requesting image with text: '{text}'...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        print(f"Image successfully requested.")
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error occured: {e}")
        return None

