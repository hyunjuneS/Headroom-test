import os
import sys

from dotenv import load_dotenv
from headroom import compress
from openai import OpenAI

load_dotenv()  # reads .env in the current directory

model = os.getenv("OPENAI_MODEL")
base_url = os.getenv("OPENAI_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")

missing = [k for k, v in {"OPENAI_MODEL": model, "OPENAI_BASE_URL": base_url,
                          "OPENAI_API_KEY": api_key}.items() if not v]
if missing:
    sys.exit(f"Set {', '.join(missing)} in .env (see .env.example)")

messages = [{"role": "user", "content": "Analyze these results"}]
result = compress(messages, model=model)

client = OpenAI(api_key=api_key, base_url=base_url)
response = client.chat.completions.create(model=model, messages=result.messages)
print(response.choices[0].message.content)
print(f"Saved {result.tokens_saved} tokens ({result.compression_ratio:.0%})")
