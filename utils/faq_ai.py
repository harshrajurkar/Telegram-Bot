import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(question):
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Use the latest model
            messages=[{"role": "user", "content": question}],
            max_tokens=200
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"
