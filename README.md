# AI Documentation Simplifier v2.0

> Transforms complex AWS documentation into simplified explanations with **human-like audio narration** and **animated explainer videos** — all for ~₹5 per explanation.

## 🎬 What It Does

Paste an AWS docs URL → get a complete explainer package:
- ✅ Simplified explanation with real-world analogy
- ✅ Natural human-like audio narration (Amazon Polly)
- ✅ **Animated explainer video** with motion graphics synced to narration (NEW in v2.0)
- ✅ Key points, troubleshooting tips, gotchas

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            USER INPUT                                         │
│  Documentation URL + PM Email (optional)                                     │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Doc Parser (BeautifulSoup)                                          │
│  Fetches URL → extracts clean text                                           │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: AI Simplifier (Amazon Bedrock — Claude Sonnet 4.6)                  │
│  Simplifies → analogy → key points → narration script                        │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌──────────────────────────┐  ┌────────────────────────────────────────────────┐
│  STEP 3: Audio Generator │  │  STEP 4: Video Generator (NEW v2.0)            │
│  Amazon Polly (Ruth)     │  │                                                │
│  Generative Engine       │  │  ┌──────────────────────────────────────────┐  │
│  → Natural MP3 narration │  │  │ Claude plans scenes per narration        │  │
│                          │  │  │ sentence with timed icons + text         │  │
└────────────┬─────────────┘  │  └──────────────────┬───────────────────────┘  │
             │                │                     ▼                           │
             │                │  ┌──────────────────────────────────────────┐  │
             │                │  │ HTML template + GSAP animations          │  │
             │                │  │ SVG icons, transitions, motion effects   │  │
             │                │  └──────────────────┬───────────────────────┘  │
             │                │                     ▼                           │
             │                │  ┌──────────────────────────────────────────┐  │
             │                │  │ HyperFrames renders HTML → MP4           │  │
             │                │  │ (headless Chrome, frame-by-frame)        │  │
             │                │  └──────────────────┬───────────────────────┘  │
             │                │                     ▼                           │
             │                │  ┌──────────────────────────────────────────┐  │
             │                │  │ ffmpeg combines video + audio → final MP4│  │
             │                │  └──────────────────────────────────────────┘  │
             │                └────────────────────────────────────────────────┘
             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  OUTPUT: Streamlit Web UI                                                    │
│  • Text explanation + analogy + tips                                         │
│  • Audio player (MP3)                                                        │
│  • Video player (MP4) — animated, synced to narration                        │
│  • Download buttons for all formats                                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack & Why

| Technology | Purpose | Why This Choice |
|-----------|---------|-----------------|
| **Amazon Bedrock (Claude Sonnet 4.6)** | Simplification + scene planning | Best reasoning for technical content; already in AWS ecosystem |
| **Amazon Polly (Generative — Ruth)** | Text-to-speech narration | Most natural-sounding voice in AWS; no external API keys needed |
| **HyperFrames** (open-source) | HTML → MP4 video rendering | Free, deterministic, renders GSAP animations frame-by-frame |
| **GSAP** | Animation engine | Industry standard for web animations; seekable timelines |
| **Streamlit** | Web UI | Fastest way to build data apps in Python; zero frontend code |
| **BeautifulSoup** | Doc parsing | Reliable HTML extraction from any AWS docs page |
| **ffmpeg** | Audio/video combining | Universal media tool; lossless stream copying |
| **MoviePy** | Audio duration detection | Python-native audio metadata reading |

### Why HyperFrames over alternatives?

| Option | Cost | Quality | Why not |
|--------|------|---------|---------|
| Amazon Nova Reel | ~₹160/video | Unpredictable | No control over content, expensive |
| Remotion | Free | Great | Requires React knowledge, complex setup |
| Manim | Free | Good for math | Text-only animations, no rich motion graphics |
| **HyperFrames** | **Free** | **YouTube-quality** | ✅ Claude writes HTML, renders to MP4 |

## 🚀 Quick Start

### Prerequisites

```bash
# Check these are installed
node --version    # Need v22+
python3 --version # Need 3.9+
ffmpeg -version   # Need ffmpeg
aws sts get-caller-identity  # AWS credentials configured
```

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/sharmaankush123/AI-Documentation-Simplifier.git
cd AI-Documentation-Simplifier/AI\ Documentation\ Simplifier

# 2. Install HyperFrames (video rendering)
npm install -g hyperframes

# 3. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Set environment variables (optional — for ElevenLabs TTS)
export ELEVENLABS_API_KEY="your_key_here"
```

### Run the Web App

```bash
source venv/bin/activate
streamlit run frontend/app.py
```

**Open → http://localhost:8501**

### How to Use

1. Paste any AWS documentation URL (e.g., `https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html`)
2. ✅ Check **"Generate audio narration"**
3. ✅ Check **"Generate explainer video"**
4. (Optional) Paste a PM email for troubleshooting tips
5. Click **"🚀 Explain This Feature!"**
6. Wait ~60-90 seconds for full generation
7. Play the video, listen to audio, download any format

## 📁 Project Structure

```
AI Documentation Simplifier/
├── config.py              # All settings (models, voices, regions)
├── main.py                # CLI version
├── requirements.txt       # Python dependencies
├── assets/
│   └── avatar.png         # Cartoon character avatar
├── services/
│   ├── doc_parser.py      # URL → clean text extraction
│   ├── simplifier.py      # Claude: simplify + analogy + narration script
│   ├── audio_gen.py       # Polly/ElevenLabs → MP3
│   └── video_gen.py       # Claude + HyperFrames → animated MP4
├── frontend/
│   └── app.py             # Streamlit web UI
├── backend/
│   └── app.py             # FastAPI (API mode)
└── output/
    ├── audio/             # Generated MP3 files
    └── videos/            # Generated MP4 files
```

## ⚙️ Configuration

All settings in `config.py`:

| Setting | Default | Options |
|---------|---------|---------|
| `AWS_REGION` | `eu-west-1` | Any region with Bedrock access |
| `CLAUDE_MODEL_ID` | `eu.anthropic.claude-sonnet-4-6` | Any Claude model ID |
| `TTS_ENGINE` | `polly` | `polly` or `elevenlabs` |
| `POLLY_VOICE_ID` | `Ruth` | `Ruth`, `Matthew`, etc. |
| `POLLY_ENGINE` | `generative` | Most natural voice engine |

## 💰 Cost Per Explanation

| Component | Cost | Notes |
|-----------|------|-------|
| Bedrock Claude (simplify + scenes) | ~₹2-3 | Two API calls |
| Amazon Polly (audio) | ~₹1 | Generative engine |
| Video rendering | **₹0** | Runs locally, open-source |
| **Total** | **~₹4-5** | |

## 🔄 Alternative Run Modes

### CLI Mode
```bash
python main.py
```

### API Mode (FastAPI)
```bash
uvicorn backend.app:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

## 📝 Technical Notes

- **Polly Generative Engine** only available in `us-east-1` — app routes there automatically
- **HyperFrames** requires Node.js 22+ and uses headless Chrome for rendering
- **Video generation** takes ~60s for a 2-minute video (3870 frames at 30fps)
- **Scene planning** uses low temperature (0.2) so visuals match narration precisely

## 🗺️ Roadmap

- [ ] Animated cartoon characters (SadTalker lip-sync when deps mature)
- [ ] Multiple video styles (whiteboard, corporate, playful)
- [ ] Batch processing — explain multiple features at once
- [ ] Slack bot integration
- [ ] PDF/HTML export of explanations

## Author

Ankush Sharma — [GitHub](https://github.com/sharmaankush123)
