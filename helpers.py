import re
import os
import json
import requests


def clean_json_string(json_str):
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')

    # Handle "NULL" values (making sure they are correctly replaced without extra quotes)
    # json_str = re.sub(r'""NULL""', '"NULL"', json_str)
    json_str = re.sub(r"(\bNULL\b)", '"NULL"', json_str)
    json_str = re.sub(r'""NULL""', '"NULL"', json_str)

    # Remove any trailing commas in objects and arrays
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*\]", "]", json_str)

    return json_str


def ask_claude(system_settings, ask):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "content-type": "application/json",
        "x-api-key": os.getenv("CLAUDE_KEY"),
        "anthropic-version": "2023-06-01",
    }
    data = {
        "model": "claude-3-sonnet-20240229",
        "system": system_settings,
        "messages": [{"role": "user", "content": ask}],
        "max_tokens": 1024,
        "temperature": 0.0,
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        response_data = response.json()

        if "content" in response_data:
            content = response_data["content"][0]["text"]
            try:
                content = clean_json_string(content)
                return json.loads(content)
            except json.JSONDecodeError:
                print("Content is not a valid JSON string. Returning as is.")
                return content
        else:
            print("Unexpected response structure:", response_data)
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
        print(f"Raw response: {response.text}")
    except Exception as err:
        print(f"An error occurred: {err}")
        print(f"Raw response: {response.text}")


def generate_prompts(email_content_to_extract):
    response_structure = {
        "__sig__": {
            "first_name": "Jane",
            "second_name": "Doe",
            "company": "ABC Company",
            "position": "Sales & Marketing Director",
            "phone": "(800) 555-1133",
            "email": "jane.doe@example.com",
            "website": "www.example.com",
        }
    }

    prompt = f"""
    You are an expert agent in data analysis and natural language processing. Your task is to process a set of email texts and extract the email signature information. Please adhere strictly to the following instructions and return the information in the specified format only:

    TASK: Extract the email signature from the following email and structure it into a JSON format.

    Instructions:
    1. Identify the signature block within the email text.
    2. Extract the following fields from the signature: first_name, second_name, company, position, phone, email, and website.
    3. If a field is missing, return 'NULL' in the JSON structure for that field only. If other fields exist, extract them. If some data could fit into two different fields, infer the best place to have it and extract it. Do not leave it.
    4. Ensure that the extracted information is accurate and consistent.
    5. Adhere strictly to the format provided below and only return the information as requested.
    6. Do not include any additional text or information beyond the required JSON structure.
    7. Do not extract emojis, extra characters, or non-relevant information. Only extract the required fields.
    8. Sometimes, we come across data that is protected and might get us in trouble if we extract it. Follow legal and copyright warnings strictly. If any information is flagged as not to be extracted, return 'NULL' for that field. Do not extract data that might get us in trouble.
    9. Verify and validate each extracted field to ensure completeness and accuracy.
    10. In case of multiple details in an email, extract data from the most relevant signature block for that specific email. e.g if we have both home and work details, you would rather get the work details.
    11. Ensure you extract all information possible (if it legally allows it) and do not leave out details.

    Email text to process:
    -----------------------------------------
    {email_content_to_extract}
    -----------------------------------------
    """

    return_format = f"""
    Your response must be in valid JSON format.
    Wrap the entire response in a JSON object with a single key '__sig__' containing the extracted signature fields.
    Example structure provided below. Do not return any other text information apart from the response JSON requested:

    -----------------------------------------

    {response_structure}
    """

    return prompt, return_format
