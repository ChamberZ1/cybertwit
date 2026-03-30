# cybertwit

Cybersecurity news bot that pulls RSS feeds, filters stories, and generates a daily digest with Gemini, Groq, or a free model from OpenRouter.

## Make It Your Own

This repo is set up so someone can fork it and customize three things without digging through the code:

1. API keys and email settings go in environment variables.
2. News sources go in `feeds.json`. See below for details.
3. Filtering rules go in `filters.json`.
4. Scheduled execution is handled by GitHub Actions.

## Local Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the example environment file and add your values:

```bash
cp .env.example .env
```

3. Edit `feeds.json` and replace the default sources with your own.

4. Edit `filters.json` if you want different keywords, match fields, or short-word rules.

5. Run the bot locally:

```bash
python main.py
```

## Environment Variables

For local runs, the app loads values from `.env` if present.

Required or commonly used variables:

- `GEMINI_API_KEY`
- `GEMINI_MODEL_NAME`
- `GROQ_API_KEY`
- `GROQ_MODEL_NAME`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_TO`

Notes:

- `MAIL_PASSWORD` should usually be an app password, not your normal inbox password. You will have to set this up with your email service provider (Gmail, Outlook, etc)
- The code accepts `GROQ_API_KEY` and also supports the older `GROQ_API` name for backward compatibility.

## Customizing Sources

Edit `feeds.json` with a list of objects like this:

```json
[
  {
    "name": "BleepingComputer",
    "url": "https://www.bleepingcomputer.com/feed/"
  },
  {
    "name": "CISA",
    "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml"
  }
]
```

Each item needs:

- `name`: display name for the source
- `url`: RSS or Atom feed URL

## Customizing Filtering

Edit `filters.json` to control which stories are kept after feed fetches.

Example structure:

```json
{
  "fields": ["title", "summary"],
  "keywords": ["ransomware", "incident response", "malware"],
  "short_words": ["aws", "ai"]
}
```

Meaning:

- `fields`: which article fields are searched
- `keywords`: case-insensitive substring matches
- `short_words`: whole-word matches for short terms that would otherwise be noisy

## GitHub Actions Setup

If someone forks this repo and wants the scheduled workflow to run in GitHub:

1. Go to the repo on GitHub.
2. Open `Settings` -> `Secrets and variables` -> `Actions`.
3. Add these repository secrets:
   - `GEMINI_API_KEY`
   - `GROQ_API_KEY`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `MAIL_TO`
4. Enable Actions for the fork if GitHub has them disabled by default.
5. Run the workflow manually once from the `Actions` tab to verify setup.

The scheduled workflow lives in `.github/workflows/daily_actions.yml`.

## Files That Matter

- `feeds.json`: editable source list
- `filters.json`: editable filtering rules
- `.env.example`: local configuration template
- `feeds.py`: feed-loading and validation logic
- `main.py`: main bot entry point
- `filter.py`: filter-loading and matching logic
- `summarize.py`: Gemini and Groq integration
- `.github/workflows/daily_actions.yml`: scheduled GitHub Actions runner

## Security

- Do not commit `.env`.
- Do not put real secrets in `feeds.json`, `README.md`, or source files.
- Prefer GitHub Actions secrets for hosted runs.
