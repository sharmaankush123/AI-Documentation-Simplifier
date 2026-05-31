# Prompt to Recreate the AI Feature Explainer App

Use this prompt with any AI assistant (ChatGPT, Claude, Copilot) to build the same app from scratch.

---

## The Prompt

```
Build me a Python Streamlit web application called "AI Feature Explainer" that does the following:

INPUT:
- A documentation URL (e.g., AWS docs page)
- An optional PM/internal email with troubleshooting context

OUTPUT:
- A simplified explanation of the feature with a relatable analogy
- Key points engineers need to know (5-7 bullets)
- Troubleshooting tips extracted from the PM email
- Gotchas and edge cases
- A human-like audio narration (MP3) explaining the feature conversationally

TECH STACK:
- Frontend: Streamlit (Python-only, no React/npm needed)
- LLM: Amazon Bedrock with Claude Sonnet 4.6 (model ID: "eu.anthropic.claude-sonnet-4-6") using the Converse API
- Audio: Amazon Polly with the GENERATIVE engine and "Ruth" voice (us-east-1 region only)
- Doc parsing: requests + BeautifulSoup

ARCHITECTURE:
1. doc_parser.py - Fetches the URL and extracts clean text (strips nav, footer, scripts)
2. simplifier.py - Calls Bedrock Claude via bedrock.converse() to simplify the docs
3. audio_gen.py - Calls Polly with Engine="generative", VoiceId="Ruth" in us-east-1
4. frontend/app.py - Streamlit UI tying it all together

KEY REQUIREMENTS:

For the LLM (simplifier.py):
- Use boto3 bedrock-runtime client with converse() API (NOT invoke_model)
- Model ID: "eu.anthropic.claude-sonnet-4-6" (change region prefix based on your AWS region)
- Region: "eu-west-1" (or your default region)
- Temperature: 0.7, max_tokens: 2500
- The prompt should ask Claude to return a JSON with these fields:
  - feature_name, simple_explanation, analogy, key_points[], 
  - troubleshooting_tips[], gotchas[], narration_script
- The narration_script should be conversational ("Hey! Let me explain...")

For the Audio (audio_gen.py):
- Use boto3 polly client pointed to REGION "us-east-1" (generative voices only available there)
- VoiceId: "Ruth" (female, clear, expressive)
- Engine: "generative" (NOT "neural" — generative is much more human-like)
- Use SSML with <prosody rate="95%"> for slightly slower, clearer speech
- Escape XML special characters (&, <, >, ", ') in the narration text before wrapping in SSML
- OutputFormat: "mp3"
- Max narration length: 3000 characters (Polly limit)

For the Frontend (frontend/app.py):
- Clean UI with gradient header
- Text input for URL, text area for PM email
- Checkbox to enable/disable audio generation
- Progress bar showing steps: Fetching → Simplifying → Generating audio
- Display results: explanation, analogy (highlighted box), key points, tips, gotchas
- Audio player with download button
- Error handling: if audio fails, still show text explanation

For the Doc Parser (doc_parser.py):
- Use requests with a browser-like User-Agent header
- Find main content via: <main>, <article>, div#main-content, div[role="main"]
- Remove: script, style, nav, footer, header, aside, iframe tags
- Truncate to 15000 chars max

IMPORTANT NOTES:
- Bedrock Converse API format (NOT invoke_model):
  ```python
  response = bedrock.converse(
      modelId="eu.anthropic.claude-sonnet-4-6",
      messages=[{"role": "user", "content": [{"text": "..."}]}],
      inferenceConfig={"maxTokens": 2500, "temperature": 0.7}
  )
  text = response["output"]["message"]["content"][0]["text"]

```

- Polly Generative call:```python
polly = boto3.client("polly", region_name="us-east-1")
response = polly.synthesize_speech(
    Text=ssml_script,
    TextType="ssml",
    OutputFormat="mp3",
    VoiceId="Ruth",
    Engine="generative"
)

```
- The app should work with `streamlit run frontend/app.py` after `pip install boto3 requests beautifulsoup4 streamlit`
- AWS credentials should already be configured via `aws configure`
- Cost per explanation: ~$0.03 (Claude) + ~$0.01 (Polly) = ~$0.04 total

Please generate the complete project with all files.

```

---

## Customization Tips

### Change Voice
Replace `"Ruth"` with:
- `"Matthew"` — Male, warm and conversational
- `"Ruth"` — Female, clear and expressive (current)

### Change Region
If your default AWS region is NOT eu-west-1, change:
- `"eu.anthropic.claude-sonnet-4-6"` → `"us.anthropic.claude-sonnet-4-6"` (for us-east-1)
- Keep Polly in `us-east-1` regardless (generative only available there)

### Add ElevenLabs (even more human)
If you want even more natural voice, sign up at elevenlabs.io (free 10k chars/month) and use:
```python
import requests
url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
headers = {"Accept": "audio/mpeg", "xi-api-key": "YOUR_KEY", "Content-Type": "application/json"}
data = {"text": script, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
response = requests.post(url, json=data, headers=headers)

```

