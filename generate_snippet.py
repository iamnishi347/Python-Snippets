import os
import datetime
import subprocess
import requests
import json
import sys

# 1. Load the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not set. Please add it to your GitHub Secrets.")
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

# 3. Gemini API endpoint (latest model)
MODEL = "gemini-1.5-pro"
api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
headers = {"Content-Type": "application/json"}
data = {
    "contents": [{"parts": [{"text": prompt}]}]
}

# 4. Call the Gemini API
try:
    response = requests.post(api_url, headers=headers, json=data)
    response.raise_for_status()
    response_json = response.json()

    # Extract generated text safely
    snippet_content = (
        response_json.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )

    if not snippet_content:
        print("❌ Error: API returned no content. Check model name or API key permissions.")
        sys.exit(1)

except requests.exceptions.RequestException as e:
    print(f"❌ API request failed: {e}")
    sys.exit(1)

# 5. Save snippet to file
today = datetime.date.today()
date_string = today.strftime("%Y-%m-%d")
filename = f"snippets/{date_string}.md"

os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, "w", encoding="utf-8") as f:
    f.write(snippet_content)

print(f"✅ Snippet saved to {filename}")

# 6. Update README.md
readme_file = "README.md"
marker = ""  # Add your insertion marker here
snippet_link = f"https://snippets.dft.codes/snippets/{date_string}.html"
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

# 7. Commit and push changes
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
