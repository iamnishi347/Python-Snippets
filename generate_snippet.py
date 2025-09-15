import os
import sys
import requests
import datetime
import time
import re

# 1. Load the OpenRouter API key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("❌ Error: OPENROUTER_API_KEY environment variable not set.")
    sys.exit(1)

# 2. Collect existing snippet titles from README (to avoid duplicates)
existing_titles = []
readme_file = "README.md"
if os.path.exists(readme_file):
    with open(readme_file, "r", encoding="utf-8") as f:
        readme_content = f.read()
        match = re.search(r"<!-- SNIPPETS:LIST -->(.*?)<!-- SNIPPETS:LIST-END -->", readme_content, re.S)
        if match:
            existing_titles = re.findall(r"\* \[(.*?)\]", match.group(1))

# 3. Define prompt for snippet generation
avoid_text = ""
if existing_titles:
    avoid_text = "Avoid generating snippets about: " + ", ".join(existing_titles[:10]) + ". "

prompt = (
    avoid_text +
    "Generate a useful, modern code snippet for a specific task in Python. "
    "The snippet should be practical and solve a common problem. "
    "Provide a detailed, markdown-formatted explanation of what the code does, "
    "why it's useful, and how to run it. "
    "The response should start with a clear, descriptive title using a markdown heading (e.g., # Snippet Title). "
    "Place the code in a markdown code block, and the explanation below it."
)

# 4. OpenRouter API
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = [
    "deepseek/deepseek-chat-v3-0324:free",
    "qwen/qwen3-coder:free"  # fallback
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

snippet_content = None

# 5. Try models with retries
for model in MODELS:
    print(f"Trying model: {model}")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates Python snippets."},
            {"role": "user", "content": prompt},
        ],
        "max_output_tokens": 800,
        "temperature": 0.9,
    }

    for attempt in range(3):
        try:
            response = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            snippet_content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if snippet_content:
                print(f"✅ Snippet generated successfully using {model}")
                break
            else:
                raise ValueError(f"No content from model {model}")
        except Exception as e:
            print(f"Attempt {attempt+1} failed for model {model}: {e}")
            if attempt < 2:
                time.sleep(5)
            else:
                print(f"❌ Model {model} failed after 3 attempts.")
    if snippet_content:
        break

if not snippet_content:
    print("❌ All models failed. Exiting.")
    sys.exit(1)

# 6. Save snippet to file
today = datetime.date.today()
date_string = today.strftime("%Y-%m-%d")
filename = f"snippets/{date_string}.md"

os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w", encoding="utf-8") as f:
    f.write(snippet_content)

print(f"✅ Snippet saved to {filename}")
