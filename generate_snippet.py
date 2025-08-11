import os
import google.generativeai as genai
import datetime
import subprocess

# 1. Configure the Gemini Pro API
# This line gets your API key from the environment variable, which is set by GitHub Actions.
# It's crucial for security to not hardcode your key here.
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("Error: GEMINI_API_KEY environment variable not set. Please add it to your GitHub Secrets.")
    exit(1)

# 2. Define the Prompt for the AI
# This is where you tell Gemini Pro what you want it to do.
# Be as specific as possible to get the best results.
# You can change the language/framework to whatever you want your library to be about.
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
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    snippet_content = response.text
except Exception as e:
    print(f"Error calling the Gemini API: {e}")
    exit(1)

# 4. Process the Response and Create a File
# Generate a unique filename based on the current date.
today = datetime.date.today()
date_string = today.strftime("%Y-%m-%d")
filename = f"snippets/{date_string}.md"

# Make sure the 'snippets' directory exists
os.makedirs(os.path.dirname(filename), exist_ok=True)

# Write the generated content to the new file.
with open(filename, 'w') as f:
    f.write(snippet_content)

print(f"Successfully generated new snippet and saved to {filename}")

# 5. Commit the New File to the Repository
# This is where we use the command line to interact with Git.
try:
    # Set up Git user info (required for commits in a GitHub Action)
    subprocess.run(['git', 'config', '--global', 'user.name', 'github-actions[bot]'], check=True)
    subprocess.run(['git', 'config', '--global', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)

    # Add the new file to the staging area
    subprocess.run(['git', 'add', filename], check=True)

    # Commit the changes
    commit_message = f"docs: Add new code snippet for {date_string}"
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)

    # Push the changes to the 'main' branch
    # The GITHUB_TOKEN is a built-in secret that allows the action to push to the repo.
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)

    print("Successfully committed and pushed new snippet to GitHub.")

except subprocess.CalledProcessError as e:
    print(f"Git command failed: {e}")
    exit(1)
