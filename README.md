# AI Code Review

* Automatically generate an AI code review on every PR.
* Easily customize [the AI prompt](./.github/workflows/ai_code_review.py#L144) as needed.
* Works with both Azure OpenAI and OpenAI APIs.
* Add to any GitHub repo with only 3 files.
* **[View Sample AI Code Review](https://github.com/mattsavarino/ai-code-review/pull/1)**

## Solution Files

1. **[ai_code_review.yml](./.github/workflows/ai_code_review.yml)**<br>
GitHub Actions file triggered upon pull request.

2. **[ai_code_review.py](./.github/workflows/ai_code_review.py)**<br>
Python script to generate AI code review.

3. **[requirements.txt](./requirements.txt)**<br>
Python package dependencies (only `openai` and `requests`).

## How to Use
1. Open or create a GitHub repo.
1. Confirm or create the [.github/workflows/](./.github/workflows/) directory.
1. Add 3 files from this repo to your project.
1. Choose your AI provider:
    * **Azure OpenAI** is highly recommended for private and enterprise use.
    * **OpenAI** is for public repos or when you give training consent.
1. Update your GitHub repo settings:
    1. Browse to Repo > Settings > Security and variables > Actions
    1. Add action secrets:
        * `OPENAI_API_KEY`
        * `AZURE_OPENAI_ENDPOINT`
        * `AZURE_OPENAI_API_KEY`
        * `AZURE_OPENAI_API_VERSION` (optional, default `2024-02-15-preview`)
        * `OPENAI_MODEL_NAME` (optional, default `gpt-4`, or Azure deployment name)
        * [Learn more about encrypted secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
1. Create new branch, push changes, and create new PR.
1. Improve your code based on the automated AI feedback.
    * Comment with AI code review posted on PR.
    * `workflow.log` created within each action run.

