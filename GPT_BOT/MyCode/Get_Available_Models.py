import os
import requests
from dotenv import load_dotenv

# Load the .env file containing the API key
env_path = os.path.join(os.path.dirname(__file__), 'EnvKeys', '.env')
load_dotenv(env_path)

# Retrieve the OpenAI API key from the environment
api_key = os.getenv('OPENAI_API_KEY')

# Headers for the API request
headers = {
    'Authorization': f'Bearer {api_key}'
}

# URL for the API request
url = 'https://api.openai.com/v1/models'

# Make the GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Extract the model names from the response
    models = response.json().get('data', [])
    for model in models:
        print(model['id'])
else:
    print("Failed to retrieve models:", response.status_code)
