import os
import json
import requests
from urllib.parse import quote

FOLDER_NAME = "PYAPI-152" #Folder name

YANDEX_API_BASE = "https://cloud-api.yandex.net/v1/disk"

def get_image_with_text(text):
    """Encoding other symbols while not touching alphabet"""
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

def create_folder_on_cloud(token, folder_path):
    """Creating folder..."""
    url = f"{YANDEX_API_BASE}/resources"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": folder_path}

    try:
        print(f"Creating folder '{folder_path}'...")
        response = requests.put(url, headers=headers, params=params)
        if response.status_code == 409: #folder already there
            print(f"Folder '{folder_path}' already exists.")
            return True
        elif response.status_code == 201:
            print(f"Folder '{folder_path}' created successfully.")
            return True
        else:
            response.raise_for_status()
            return True
    except requests.exceptions.RequestException as e:
        print(f"Error occured while creating folder: {e}")
        if hasattr(e, "response") and e.response:
            print(f"Response: {e.response}")
        return False

def get_upload_url(token, file_path):
    """Gets URL for uploading file"""
    url = f"{YANDEX_API_BASE}/resources/upload"
    headers = {"Authorization": f"OAuth {token}"}
    params = {
        "path": file_path,
        "overwrite": True #rewrite if exists
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("href")

    except requests.exceptions.RequestException as e:
        print(f"Error getting upload URL: {e}")
        if hasattr(e, "response") and e.response:
            print(f"Response: {e.response.text}")
        return None

def get_file_meta(token, file_path):
    """Gets file metadata"""
    url = f"{YANDEX_API_BASE}/resources"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": file_path}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "name": data.get("name"),
            "size_bytes": data.get("size"),
            "size_mb": round(data.get("size", 0) / (1024 * 1024), 2),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error getting file metadata: {e}")
        return None

def upload_file(token, folder_name, file_name, file_data):
    """Uploading file to Yandex Disk through API"""
    file_path = f"{folder_name}/{file_name}.jpg"

    #create folder
    if not create_folder_on_cloud(token, f"/{folder_name}"):
        return None

    #get URL
    upload_url = get_upload_url(token, file_path)
    if not upload_url:
        return None

    #upload file to URL
    try:
        print(f"Uploading file '{file_name}.jpg' to '{upload_url}'...")

        response = requests.put(upload_url, data=file_data)
        response.raise_for_status()
        print(f"File '{file_name}.jpg' successfully uploaded.")

        #getting metadata
        return get_file_meta(token, file_path)

    except requests.exceptions.RequestException as e:
        print(f"Error occured while uploading file: {e}")
        if hasattr(e, "response") and e.response:
            print(f"Response: {e.response.text}")
        return None

def save_report(report_data, file_path = "report.json"):
    """Saves report data to JSON file"""

    try:
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding='utf-8') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []

        existing_data.append(report_data)

        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        print(f"Report data successfully saved to '{file_path}'")
    except Exception as e:
        print(f"Error occured while saving report data: {e}")

def main():
    """Main function"""
    print("---Program of reserve copying cats---")

    user_text = input("Please enter your text for the image: ").strip()
    if not user_text or user_text == "":
        print("Text for the image cannot be empty")
        exit()

    user_token = input("Please enter your OAuth-token for Yandex Disk: ").strip()
    if not user_token or user_token == "":
        print("Text for the token cannot be empty")
        exit()

    # Getting image
    image_data = get_image_with_text(user_text)
    if not image_data:
        print("Program exit due to no image")
        exit()

    # Uploading image
    upload_info = upload_file(user_token, FOLDER_NAME, user_text, image_data)
    if not upload_info:
        print("Program exit due to error while uploading to Yandex Disk")
        return

    # Saving report
    save_report(upload_info)
    print("---Program of reserve copying cats successfully executed!---")
    print(f"--- File '{user_text}.jpg' has been successfully uploaded in folder '{FOLDER_NAME}'---")
    print(f"File size: {upload_info['size_mb']} MB")

if __name__ == "__main__":
    main()

