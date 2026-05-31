# AI Documentation Simplifier

This tool transforms complex AWS documentation into easy-to-understand feature explanations with human-like audio narration. It's designed for **Support Engineers** who need to quickly ramp up on new AWS features by providing simplified explanations, relatable analogies, troubleshooting tips, and natural-sounding audio walkthroughs.

## Why This Tool?

When a new AWS feature launches, engineers receive:
- Dense technical documentation
- Internal PM emails with troubleshooting context
- Training materials that take hours to consume

This tool processes all of that in **~15 seconds** and produces:
- A simplified explanation a 10-year-old could understand
- A real-world analogy that makes the concept click
- Key points engineers need to know
- Troubleshooting tips extracted from internal emails
- A **human-like audio narration** explaining it conversationally

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: Documentation URL + PM Email (optional)              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Doc Parser (BeautifulSoup)                               │
│    Fetches URL → extracts clean text content                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. AI Simplifier (Amazon Bedrock — Claude Sonnet 4.6)       │
│    Simplifies → creates analogy → extracts tips → writes    │
│    narration script                                         │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Audio Generator (Amazon Polly — Generative Engine)       │
│    Converts narration script → natural human-like MP3       │
│    Voice: "Ruth" (Generative) — most natural Polly voice    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT: Simplified explanation + Audio narration + Tips      │
│ Displayed in Streamlit web UI with download options          │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone or navigate to the project
cd ~/Desktop/"AI Documentation Simplifier"

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the web app
streamlit run frontend/app.py
```

Open **http://localhost:8501** in your browser.

## Prerequisites

| Requirement | How to verify |
|-------------|--------------|
| Python 3.9+ | `python3 --version` |
| AWS CLI configured | `aws sts get-caller-identity` |
| Bedrock access (Claude Sonnet 4.6) | Auto-enabled on first invocation |
| Amazon Polly access | Enabled by default |

### AWS Configuration

```bash
aws configure
# Region: eu-west-1 (or your preferred region)
# Output: json
```

## Project Structure

```
AI Documentation Simplifier/
├── config.py              # ⚙️ All settings (models, voices, regions)
├── main.py                # 📟 CLI version
├── run.sh                 # 🚀 Quick start script
├── requirements.txt       # 📦 Python dependencies
├── README.md              # 📖 This file
├── PROMPT_TO_RECREATE.md  # 🤖 Prompt to rebuild this app with any AI
│
├── services/              # 🔧 Core AI services
│   ├── doc_parser.py      #    Fetches & extracts docs from URL
│   ├── simplifier.py      #    Bedrock Claude — simplify + analogies
│   ├── audio_gen.py       #    Amazon Polly Generative / ElevenLabs
│   ├── image_gen.py       #    SVG diagram generation (via Claude)
│   └── video_gen.py       #    Amazon Nova Reel (async video gen)
│
├── backend/               # 🔌 FastAPI server (API mode)
│   └── app.py
│
├── frontend/              # 🖥️ Streamlit web UI
│   └── app.py
│
└── output/                # 📁 Generated files
    ├── images/
    ├── audio/
    └── videos/
```

## Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `AWS_REGION` | `eu-west-1` | AWS region for Bedrock Claude |
| `CLAUDE_MODEL_ID` | `eu.anthropic.claude-sonnet-4-6` | LLM for simplification |
| `TTS_ENGINE` | `polly` | `"polly"` or `"elevenlabs"` |
| `POLLY_VOICE_ID` | `Ruth` | Female, expressive voice |
| `POLLY_ENGINE` | `generative` | Most human-like Polly engine |

### Available Polly Generative Voices

| Voice | Gender | Style |
|-------|--------|-------|
| `Ruth` | Female | Clear, expressive (recommended) |
| `Matthew` | Male | Warm, conversational |

> **Note:** Generative engine is only available in `us-east-1`. The app automatically routes Polly calls there.

## Cost Per Explanation

| Service | Cost | Notes |
|---------|------|-------|
| Bedrock Claude Sonnet 4.6 | ~$0.01-0.03 | Depends on doc length |
| Amazon Polly (Generative) | ~$0.016 per 1000 chars | ~$0.03 for 2-min narration |
| **Total** | **~$0.04-0.06** | Less than ₹5 per explanation |

## Usage

### Web UI (Recommended)
```bash
streamlit run frontend/app.py
```

### CLI Mode
```bash
python main.py
```

### API Mode (FastAPI)
```bash
uvicorn backend.app:app --reload --port 8000
# Interactive docs at http://localhost:8000/docs
```

## Example Output

**Input:** `https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files.html`

**Output:**
- 📌 **Feature:** Amazon S3 Files
- 💡 **Explanation:** S3 Files lets you access your S3 data as a file system without copying it...
- 🎯 **Analogy:** It's like having a library card that lets you read books directly on the shelf without checking them out...
- 📋 **Key Points:** 5-7 bullets
- 🔧 **Troubleshooting Tips:** Extracted from PM email
- 🎙️ **Audio:** 1-2 minute MP3 narration in natural human voice

## Future Enhancements

- [ ] AI-generated explainer video (D-ID / Runway ML / Nova Reel)
- [ ] AI image generation (when Bedrock image models return)
- [ ] History — browse past explanations
- [ ] Batch mode — process multiple features at once
- [ ] Team sharing — export as HTML/PDF
- [ ] Slack integration — explain features from Slack commands

## Technical Notes

- **Bedrock API:** Uses `converse()` API (not `invoke_model`) for Claude — required for cross-region inference profiles
- **Polly Region:** Generative engine only available in `us-east-1` — app routes there automatically
- **Model IDs:** Use `eu.anthropic.claude-sonnet-4-6` format for EU, `us.anthropic.claude-sonnet-4-6` for US
- **Image/Video Models:** All Bedrock media generation models (Titan Image, Nova Canvas, Nova Reel) marked LEGACY as of May 2026

## License

MIT-0 — See LICENSE

## Author

Ankush Singh (singholr@amazon.com)
