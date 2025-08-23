import os
import datetime
import subprocess
import sys
import requests

# 1. Load the OpenRouter API key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("❌ Error: OPENROUTER_API_KEY environment variable not set. Please add it to your GitHub Secrets.")
    sys.exit(1)

# 2. Define prompt for snippet generation
prompt = (
    "Generate a useful, modern code snippet for a specific task in Python. "
    "The snippet should be practical and solve a common problem. "
    "Also, provide a detailed, markdown-formatted explanation of what the code does, "
    "why it's useful, and how to run it. "
    "The response should start with a clear, descriptive title using a markdown heading (e.g., # Snippet Title). "
    "Place the code in a markdown code block, and the explanation below it."
)

# 3. Call DeepSeek V3 (free) through OpenRouter
MODEL = "deepseek/deepseek-chat-v3-0324:free"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant that generates Python snippets."},
        {"role": "user", "content": prompt},
    ],
    "max_output_tokens": 800,
    "temperature": 0.7,
}

try:
    response = requests.post(BASE_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    snippet_content = data["choices"][0]["message"]["content"].strip()

    if not snippet_content:
        print("❌ Error: Model returned no content. Check model name or key.")
        sys.exit(1)

except Exception as e:
    print(f"❌ API request failed: {e}")
    sys.exit(1)

# 4. Save snippet to file
today = datetime.date.today()
date_string = today.strftime("%Y-%m-%d")
filename = f"snippets/{date_string}.md"

os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w", encoding="utf-8") as f:
    f.write(snippet_content)

print(f"✅ Snippet saved to {filename}")

# 5. Update README.md (optional, requires marker)
readme_file = "README.md"
marker = "<!-- SNIPPETS:LIST -->"
snippet_link = f"snippets/{date_string}.md"
new_snippet_link = f"* [{date_string}]({snippet_link})\n"

if os.path.exists(readme_file):
    with open(readme_file, "r", encoding="utf-8") as f:
        readme_content = f.read()

    if marker and marker in readme_content:
        updated_readme = readme_content.replace(marker, f"{marker}\n{new_snippet_link}")
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(updated_readme)
        print("✅ README.md updated.")
    else:
        print("⚠️ Marker not found in README.md — skipping update.")

# 6. Commit and push changes
try:
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", filename, readme_file], check=True)
    commit_message = f"docs: Add new code snippet for {date_string} and update README"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Changes committed and pushed.")
except subprocess.CalledProcessError as e:
    print(f"❌ Git command failed: {e}")
    sys.exit(1)
