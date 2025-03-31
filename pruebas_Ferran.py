import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

client = Groq(
    api_key=os.getenv("LLMsAPIkey_Groq"),
    )

chat_completion = client.chat.completions.create(
messages=[
    {
        "role": "system",
        "content": "Eres un experto en física",
    },
    {
        "role": "user",
        "content": "Cuéntame un chiste sobre física",
    }
],
model="llama-3.3-70b-versatile",
temperature=0,
frequency_penalty=0
)

print(chat_completion.choices[0].message.content)