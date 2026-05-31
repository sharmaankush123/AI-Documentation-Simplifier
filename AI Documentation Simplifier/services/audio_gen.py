"""
services/audio_gen.py — Text-to-Speech using ElevenLabs (human-like) or Amazon Polly (fallback).

ElevenLabs produces much more natural, human-sounding narration.
Free tier: 10,000 characters/month (enough for ~20 feature explanations).

If no ElevenLabs API key is set, falls back to Amazon Polly.
"""

import boto3
import requests
from pathlib import Path
import sys
sys.path.append("..")
from config import (AWS_REGION, POLLY_VOICE_ID, POLLY_ENGINE, AUDIO_DIR, 
                    MAX_NARRATION_LENGTH, ELEVENLABS_API_KEY, TTS_ENGINE)


# Ensure output directory exists
Path(AUDIO_DIR).mkdir(parents=True, exist_ok=True)


def generate_narration(script: str, feature_name: str = "feature") -> str:
    """
    Convert narration script to speech.
    Uses ElevenLabs if configured, otherwise falls back to Amazon Polly.
    """
    if TTS_ENGINE == "elevenlabs" and ELEVENLABS_API_KEY:
        return _generate_elevenlabs(script, feature_name)
    else:
        return _generate_polly(script, feature_name)


def _generate_elevenlabs(script: str, feature_name: str) -> str:
    """Generate speech using ElevenLabs API (most human-like)."""
    
    # Truncate if needed
    if len(script) > 5000:
        script = script[:4950] + "... and that's the key overview!"

    # ElevenLabs voices (free tier includes these):
    # "Rachel" - calm female, "Adam" - warm male, "Antoni" - friendly male
    # "Bella" - soft female, "Josh" - deep male
    VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # "Adam" - warm, conversational male
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,  # More expressive
            "use_speaker_boost": True
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    
    # Save the audio
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)[:40]
    output_path = Path(AUDIO_DIR) / f"{safe_name}.mp3"
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    return str(output_path)


def _generate_polly(script: str, feature_name: str) -> str:
    """Generate speech using Amazon Polly (fallback)."""
    
    # Generative engine only available in us-east-1
    polly = boto3.client("polly", region_name="us-east-1")
    
    # Truncate if needed
    if len(script) > MAX_NARRATION_LENGTH:
        script = script[:MAX_NARRATION_LENGTH - 50] + "... and that's the key overview!"

    # Use SSML for better pacing
    # Escape XML special chars in script
    script_escaped = (script
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;"))

    ssml_script = f"""<speak>
    <prosody rate="95%">
    {script_escaped}
    </prosody>
    </speak>"""

    response = polly.synthesize_speech(
        Text=ssml_script,
        TextType="ssml",
        OutputFormat="mp3",
        VoiceId=POLLY_VOICE_ID,
        Engine=POLLY_ENGINE
    )

    # Save the audio
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)[:40]
    output_path = Path(AUDIO_DIR) / f"{safe_name}.mp3"

    with open(output_path, "wb") as f:
        f.write(response["AudioStream"].read())

    return str(output_path)


def list_available_voices() -> list:
    """List available Polly neural English voices."""
    polly = boto3.client("polly", region_name=AWS_REGION)
    response = polly.describe_voices(Engine="neural", LanguageCode="en-US")
    return [
        {"id": v["Id"], "name": v["Name"], "gender": v["Gender"]}
        for v in response["Voices"]
    ]
