import os
import json

import requests
import yadisk
import io
from urllib.parse import quote

FOLDER_NAME = "PYAPI-152" #Folder name

def get_image_with_text(text):
    #Encoding other symbols while not touching alphabet
    encoded_text = quote(text)

    url = f"https://cataas.com/cat/says/{encoded_text}"

    try:
        print(f"Requesting image with text: '{text}'...")
        response = requests.get(url)
        response.raise_for_status()
        print(f"Image successfully requested.")
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error occured: {e}")
        return None

def upload_to_yandex_disk(token, folder_name, file_name, file_data):
    client = yadisk.Client(token=token)
    upload_path = f"{folder_name}/{file_name}.jpg"

    try:
        print(f"Connecting Yandex Disk...")
        with client:
            #Verify token
            if not client.check_token():
                print(f"Error : Wrong token")
                return None

            #Check if folder is there
            print(f"Creating folder '{folder_name}'...")
            try:
                client.mkdir(f"/{folder_name}")
            except yadisk.exceptions.PathExistsError:
                print(f"Error : Folder '{folder_name}' already exists")
            except Exception as e:
                print(f"Error while creating folder : {e}")
                return None

            #Uploading file
            print(f"Uploading image to Yandex Disk: {file_name}.jpg...")
            client.upload(io.BytesIO(file_data),upload_path,overwrite=True)

            print(f"File uploaded successfully")

            #Get info about uploaded file
            meta = client.get_meta(upload_path)
            return {
                "name": f"{file_name}.jpg",
                "size_bytes": meta.size,
                "size_mb": round(meta.size / (1024 * 1024), 2),
            }

    except Exception as e:
        print(f"Error while uploading image to Yandex Disk: {e}")
        return None

def save_report(report_data, file_path="report.json"):
    #Saving info about uploaded files

    try:
        #If exists, download it and add new data
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding='utf-8') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []

        existing_data.append(report_data)

        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        print(f"Report saved successfully in '{file_path}'")
    except Exception as e:
        print(f"Error while saving report: {e}")

print("---Program of reserve copying cats---")
user_text = input("Please enter your text for the image: ").strip()
if not user_text or user_text == "":
    print("Text for the image cannot be empty")
    exit()

user_token = input("Please enter your OAuth-token for Yandex Disk: ").strip()
if not user_token or user_token == "":
    print("Text for the image cannot be empty")
    exit()

#Getting image
image_data = get_image_with_text(user_text)
if not image_data:
    print("Program exit due to no image")
    exit()

#Uploading image
upload_info = upload_to_yandex_disk(user_token, FOLDER_NAME, user_text, image_data)
if not upload_info:
    print("Program exit due to the error while uploading image to Yandex Disk")
    exit()

#Saving report
save_report(upload_info)
print("---Program of reserve copying cats successfully executed!---")
print(f"--- File '{user_text}.jpg' has been successfully uploaded in folder '{FOLDER_NAME}'---")
print(f"File size: {upload_info['size_mb']} MB")