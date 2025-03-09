import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENAI_API_KEY")
)

completion = client.chat.completions.create(
    model="google/gemini-2.0-flash-001",
    messages=[
        {
            "role": "user",
            "content": "What is the meaning of life?"
        }
    ]
)

print(completion.choices[0].message.content)
