"""
ai_code_review_azure.py

This script is triggered by GitHub Actions for an automated AI code review of pull requests.
It uses Azure OpenAI or OpenAI to generate a code review based on the diff of the pull request.
"""

import sys
import os
import requests

# Import both Azure and OpenAI clients
from openai import OpenAI
from openai import AzureOpenAI

# Constants
GITHUB_API_URL = 'https://api.github.com'
REPO = os.getenv('GITHUB_REPOSITORY')
PR_NUMBER = os.getenv('PR_NUMBER')
PR_TITLE = os.getenv('PR_TITLE')
PR_BODY = os.getenv('PR_BODY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# GitHub Actions Secrets for OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# GitHub Actions Secrets for Azure
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
if not AZURE_OPENAI_API_VERSION:
  AZURE_OPENAI_API_VERSION = '2024-02-15-preview'

# OpenAI model or AOAI deployment name, default to GPT-4
OPENAI_MODEL_NAME = os.getenv('OPENAI_MODEL_NAME', 'gpt-4')
if not OPENAI_MODEL_NAME:
  OPENAI_MODEL_NAME = 'gpt-4'

# Function to log messages to a file, note per run
def log_message(message):
  """Logs a message to the workflow.log file."""
  with open('workflow.log', 'a') as log_file:
    log_file.write(message + '\n')

# Define AI Provider
# Highly recommend Azure for private repositories.
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
  AI_PROVIDER = 'azure'
elif OPENAI_API_KEY:
  AI_PROVIDER = 'openai'
else:
  log_message(f"\n#####\nERROR: AI provider credentials not found.\n")
  # raise SystemExit(1)

# Log variables
log_message(f"""
##### AI Provider: {AI_PROVIDER}
##### Model: {OPENAI_MODEL_NAME}
##### Azure Endpoint: {AZURE_OPENAI_ENDPOINT}
##### Azure Version: {AZURE_OPENAI_API_VERSION}

""")


# Try to establish AI client
try:
  # Default to Azure for private repos
  if AI_PROVIDER == 'azure':
    client = AzureOpenAI(
      azure_endpoint = AZURE_OPENAI_ENDPOINT,
      api_key = AZURE_OPENAI_API_KEY,
      api_version = AZURE_OPENAI_API_VERSION,
    )
  
  # OpenAI recommended only for public repositories
  elif AI_PROVIDER == 'openai':
    client = OpenAI()

# Log error if unable to initialize AI client
except Exception as e:
  log_message(f"\n#####\nERROR: Unable to initialize AI client.\n\n{e}\n")
  # raise SystemExit(1)


# Log variables for debugging
log_message(f"""
#####
REPO: {REPO}
PR_NUMBER: {PR_NUMBER}

""")

# Function to get the diff of a PR
def get_pr_diff(repo, pr_number, token):
  """
  Fetches the diff of a pull request.

  Parameters:
  repo (str): The repository name.
  pr_number (str): The pull request number.
  token (str): The GitHub token for authentication.

  Returns:
  str: The diff text of the pull request.
  """
  url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}"
  headers = {
    'Authorization': f"token {token}",
    'Accept': 'application/vnd.github.v3.diff'
  }
  # Try to fetch PR diff
  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    diff_text = response.text
    # log_message(f"\n#####\nPR Diff:\n{diff_text}\n")
    return diff_text
  # Log error if unable to fetch PR diff
  except Exception as e:
    log_message(f"\n#####\nERROR: Unable to fetch PR diff.\n\n{e}\n")
    # raise SystemExit(1)

# Function to review code with an AI LLM
def review_code_with_llm(diff):
  """
  Generates an AI code review for the given diff using an AI LLM.

  Parameters:
  diff (str): The diff text of the pull request.

  Returns:
  str: The AI-generated code review.
  """
  # Mult-line Prompt
  prompt_diff = f"""# PR {PR_NUMBER}: {PR_TITLE}

## PR Decription:
{PR_BODY}

## PR Code Diff:
{diff}
"""

  # System Prompt
  prompt_system = f"""You are an AI Assistant specializing in GitHub code reviews.

## Objectives:
- Automatically perform a thorough and constructive code review for the following code changes within a GitHub repository.
- Ensure code quality, functionality, performance, security, and adherence to coding standards.

## Instructions:
1. **Preparation**
  - Review the pull request (PR) description to understand the context and scope of the changes.
  - Identify the related issue or feature request and understand its requirements.
2. **Initial Review**
  - Ensure the PR description is clear, concise, and includes necessary information such as issue links, change descriptions, and testing instructions.
  - Verify that the PR addresses all aspects of the related issue or feature request.
3. **Code Quality**
  - **Readability**: Assess the code for readability. Check naming conventions, comments, and documentation for clarity.
  - **Maintainability**: Ensure the code is structured for easy maintenance, adhering to project architecture and modularity principles.
4. **Functionality**
  - **Correctness**: Validate that the code works as intended. Review logic, algorithms, and edge cases.
  - **Testing**: Ensure sufficient unit and integration tests are present and passing. Verify that tests cover main functionality and edge cases.
5. **Performance**
  - **Efficiency**: Evaluate the performance implications of the changes. Ensure no significant performance regressions are introduced.
  - **Optimization**: Suggest obvious optimizations that do not compromise readability or maintainability.
6. **Security**
  - **Vulnerabilities**: Identify potential security issues such as SQL injection, XSS, etc.
  - **Best Practices**: Ensure the code follows security best practices relevant to the project.
7. **Style and Consistency**
  - **Coding Standards**: Verify adherence to the project's coding standards and guidelines.
  - **Consistency**: Ensure the code is consistent with the existing codebase in terms of style and conventions.
8. **Feedback and Communication**
  - **Constructive Feedback**: Provide clear, constructive, and respectful feedback. Highlight strengths and areas for improvement.
  - **Discussion**: Facilitate meaningful discussion with the author. Clarify doubts and discuss potential improvements.
  - **Actionable Comments**: Make comments actionable with clear instructions or suggestions.
9. **Approval or Request Changes**
  - **Approval**: Approve the PR if it meets all standards.
  - **Request Changes**: Clearly outline necessary changes and the reasons for them if the PR does not meet standards.
10. **Follow-Up**
  - **Verify Changes**: Ensure requested changes are implemented correctly.
  - **Final Approval**: Provide final approval if the changes address the concerns satisfactorily.
11. **Merge and Clean-Up**
  - **Merge**: Merge the PR using the appropriate method (e.g., squash and merge, rebase and merge) once approved.
  - **Clean-Up**: Ensure the branch is deleted if no longer needed to keep the repository tidy.
12. **Continuous Improvement**
  - **Retrospective**: Regularly review the code review process and standards. Gather team feedback and continuously improve the process.

**Output Requirements:**
- Final decision ("Approved" or "Changes Requested") with a brief justification.
- Provide a summary of your key findings and recommendations.
- List any required changes with clear instructions
- Include comments on code lines where specific feedback is necessary.
- DO NOT INCLUDE a section-level summary when the code appears compliant and there are no suggestions for improvement.
- DO NOT INCLUDE a summary of the PR description or changes unless necessary for context.
- DO NOT INCLUDE irrelevant topics or opinions unrelated to the code quality.
"""
  
  # Log prompt for debugging
  log_message(f"\n#####\nDIFF:\n{prompt_diff}\n")

  # Generate AI code review
  ai_response = None
  try:
    response = client.chat.completions.create(
      model=OPENAI_MODEL_NAME,
      messages=[
        {'role': 'system', 'content': prompt_system},
        {'role': 'user', 'content': prompt_diff}
      ]
    )
    ai_response = response.choices[0].message.content

  except Exception as e:
    log_message(f"\n#####\nERROR: Unable to generate AI code review.\n\n{e}\n")
    # raise SystemExit(1)

  # Format provider name
  if AI_PROVIDER == 'azure':
      ai_provider_name = 'Azure'
  elif AI_PROVIDER == 'openai':
      ai_provider_name = 'OpenAI'
  else:
      ai_provider_name = 'Unknown'
  
  return f"via {ai_provider_name}\n\n{ai_response}"

# Main function
def main():
  """
  Main function to run the AI code review process.
  Validates environment variables, retrieves the PR diff, generates the AI code review, and prints it.
  """
  # Validate required variables
  if not REPO or not PR_NUMBER or not GITHUB_TOKEN:
    log_message(f"\n#####\nERROR: Environment variables must be set.\n")
    # raise SystemExit(1)
  
  diff = get_pr_diff(REPO, PR_NUMBER, GITHUB_TOKEN)
  review = review_code_with_llm(diff)
  print(review)

# Run the main function
if __name__ == '__main__':
  main()
