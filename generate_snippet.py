import os
import google.generativeai as genai
import datetime
import subprocess

# 1. Configure the Gemini Pro API
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("Error: GEMINI_API_KEY environment variable not set. Please add it to your GitHub Secrets.")
    exit(1)

# 2. Define the Prompt for the AI
prompt = (
    "Generate a useful, modern code snippet for a specific task in Python. "
    "The snippet should be practical and solve a common problem. "
    "Also, provide a detailed, markdown-formatted explanation of what the code does, "
    "why it's useful, and how to run it. "
    "The response should start with a clear, descriptive title using a markdown heading (e.g., # Snippet Title). "
    "Place the code in a markdown code block, and the explanation below it."
)

# 3. Call the Gemini Pro API
try:
    # This is the corrected line to use the fully-qualified model name.
    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(prompt)
    snippet_content = response.text
except Exception as e:
    print(f"Error calling the Gemini API: {e}")
    exit(1)

# 4. Process the Response and Create a File
today = datetime.date.today()
date_string = today.strftime("%Y-%m-%d")
filename = f"snippets/{date_string}.md"

# Make sure the 'snippets' directory exists
os.makedirs(os.path.dirname(filename), exist_ok=True)

# Write the generated content to the new file.
with open(filename, 'w') as f:
    f.write(snippet_content)

print(f"Successfully generated new snippet and saved to {filename}")

# 5. Automate the README.md Update
readme_file = "README.md"
readme_content = ""
# Note: The marker variable was missing a value in your code.
marker = "<!-- SNIPPET_INSERT_POINT -->"
snippet_link = f"https://snippets.dft.codes/snippets/{date_string}.html" # Assuming your GitHub Pages URL structure

new_snippet_link = f"* [{date_string}]({snippet_link})\n"

with open(readme_file, 'r') as f:
    readme_content = f.read()

# Find the marker and insert the new link.
if marker in readme_content:
    updated_readme = readme_content.replace(marker, f"{marker}\n{new_snippet_link}")
    with open(readme_file, 'w') as f:
        f.write(updated_readme)
    print("Successfully updated README.md with a link to the new snippet.")
else:
    print("Warning: Could not find the snippet insertion marker in README.md. Please add '<!-- SNIPPET_INSERT_POINT -->' to your file.")

# 6. Commit the New Files to the Repository
try:
    subprocess.run(['git', 'config', '--global', 'user.name', 'github-actions[bot]'], check=True)
    subprocess.run(['git', 'config', '--global', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)

    # Add both the new snippet and the updated README file.
    subprocess.run(['git', 'add', filename, readme_file], check=True)

    commit_message = f"docs: Add new code snippet for {date_string} and update README"
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)

    subprocess.run(['git', 'push', 'origin', 'main'], check=True)

    print("Successfully committed and pushed new snippet and updated README to GitHub.")

except subprocess.CalledProcessError as e:
    print(f"Git command failed: {e}")
    exit(1)
