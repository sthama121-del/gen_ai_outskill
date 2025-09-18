#hello.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# load .env
load_dotenv()

key = os.getenv("OPENAI_API_KEY")
print("Loaded key?", bool(key))  # DEBUG

if not key:
    raise SystemExit("❌ No OPENAI_API_KEY found in .env")

base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=key, base_url=base_url)

try:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Explain the meaning of the surname Thamagonda?"}]
    )
    print("✅ Response:", resp.choices[0].message.content)
except Exception as e:
    print("❌ Error:", e)

