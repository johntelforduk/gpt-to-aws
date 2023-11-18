import base64
import requests
from dotenv import load_dotenv
from os import getenv

# OpenAI API Key
load_dotenv(verbose=True)           # Set operating system environment variables based on contents of .env file.
api_key = getenv('OPEN_AI_KEY')

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "hla.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": """Here is a high level architecture diagram for a system.
            The system will be deployed to Amazon Web Services (AWS).
            You must generate an AWS CloudFormation template for the system. 
            I will then use your CloudFormation code to generate the infrastructure.
            Ensure that your CloudFormation template is valid.
            If in doubt about correct configurations to use for AWS services, please follow AWS Well Architected guidelines."""
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 1000
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json()["choices"][0]["message"]["content"])
