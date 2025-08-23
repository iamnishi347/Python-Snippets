import os
import datetime
import subprocess
import sys
from huggingface_hub import InferenceClient

# 1. Load the Hugging Face API token
api_key = os.getenv("HF_API_TOKEN")
if not api_key:
    print("❌ Error: HF_API_TOKEN environment variable not set. Please add it to your GitHub Secrets.")
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

# 3. Initialize Hugging Face Inference Client with FLAN-T5-Large
MODEL = "google/flan-t5-large"
client = InferenceClient(model=MODEL, token=api_key)

# 4. Generate snippet
try:
    response = client.text_generation(
        prompt,
        max_new_tokens=800,
        temperature=0.7,
        return_full_text=False,
    )

    if isinstance(response, str):
        snippet_content = response.strip()
    else:
        snippet_content = str(response)

    if not snippet_content:
        print("❌ Error: Model returned no content. Check model name or token.")
        sys.exit(1)

except Exception as e:
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

# 6. Update README.md (optional, requires a marker present in README)
readme_file = "README.md"
marker = "<!-- SNIPPETS:LIST -->"  # add this marker to README.md where you want links to appear
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
