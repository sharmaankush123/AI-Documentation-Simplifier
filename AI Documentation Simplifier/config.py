"""
config.py — Central configuration for the Feature Explainer app.
Modify settings here instead of digging through individual files.
"""

import os

# === AWS Configuration ===
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")

# === Bedrock Models ===
CLAUDE_MODEL_ID = "eu.anthropic.claude-sonnet-4-6"
# Cheaper/faster alternative: "eu.anthropic.claude-haiku-4-5-20251001-v1:0"

# === Video Generation (Nova Reel — only available in us-east-1) ===
VIDEO_REGION = "us-east-1"
NOVA_REEL_MODEL_ID = "amazon.nova-reel-v1:1"
VIDEO_S3_BUCKET = "singholr-feature-explainer"

TITAN_IMAGE_MODEL_ID = "amazon.titan-image-generator-v2:0"
# Alternative: "amazon.nova-canvas-v1:0"

# === Text-to-Speech Configuration ===
# Options: "elevenlabs" (most human-like) or "polly" (Amazon, no extra setup)
TTS_ENGINE = "polly"

# ElevenLabs (free tier: 10,000 chars/month — ~20 explanations)
# Get your API key at: https://elevenlabs.io (sign up free)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# Amazon Polly (fallback — no extra setup needed)
POLLY_VOICE_ID = "Ruth"      # Female, clear and expressive
POLLY_ENGINE = "generative"  # Most human-like Polly engine

# === Generation Settings ===
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
IMAGE_CFG_SCALE = 8.0

MAX_DOC_LENGTH = 15000       # Truncate docs longer than this (chars)
MAX_NARRATION_LENGTH = 3000  # Polly has a 3000 char limit per request

# === Output Paths ===
OUTPUT_DIR = "output"
IMAGES_DIR = f"{OUTPUT_DIR}/images"
AUDIO_DIR = f"{OUTPUT_DIR}/audio"
JSON_DIR = f"{OUTPUT_DIR}/explanations"

# === App Settings ===
APP_TITLE = "🚀 AI Feature Explainer"
APP_DESCRIPTION = "Turn complex AWS docs into simple explanations with visuals & audio"
FASTAPI_PORT = 8000
STREAMLIT_PORT = 8501
