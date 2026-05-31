"""
FastAPI Backend — Feature Explainer API

Endpoints:
    POST /api/explain     → Full pipeline (URL + email → explanation + image + audio)
    POST /api/simplify    → Text simplification only (no image/audio)
    GET  /api/voices      → List available Polly voices
    GET  /api/health      → Health check

Run:
    uvicorn backend.app:app --reload --port 8000
    Then visit: http://localhost:8000/docs (interactive API docs)
"""

import json
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

import sys
sys.path.append(str(Path(__file__).parent.parent))

from services.doc_parser import fetch_documentation
from services.simplifier import simplify_feature
from services.image_gen import generate_feature_image
from services.audio_gen import generate_narration, list_available_voices
from config import APP_TITLE, APP_DESCRIPTION, OUTPUT_DIR

# Create output directories
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(f"{OUTPUT_DIR}/images").mkdir(parents=True, exist_ok=True)
Path(f"{OUTPUT_DIR}/audio").mkdir(parents=True, exist_ok=True)

# Initialize FastAPI
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version="1.0.0"
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve output files (images, audio)
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")


# === Request/Response Models ===

class ExplainRequest(BaseModel):
    doc_url: str = Field(..., description="URL of the documentation page")
    pm_email: Optional[str] = Field("", description="Optional PM email content with internal details")
    generate_image: bool = Field(True, description="Whether to generate an illustration")
    generate_audio: bool = Field(True, description="Whether to generate audio narration")


class ExplainResponse(BaseModel):
    id: str
    feature_name: str
    simple_explanation: str
    analogy: str
    key_points: list[str]
    troubleshooting_tips: list[str]
    gotchas: list[str]
    narration_script: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    source_url: str


class SimplifyRequest(BaseModel):
    doc_url: str = Field(..., description="URL of the documentation page")
    pm_email: Optional[str] = Field("", description="Optional PM email content")


# === API Endpoints ===

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "feature-explainer"}


@app.post("/api/explain", response_model=ExplainResponse)
async def explain_feature(request: ExplainRequest):
    """
    Full pipeline: Fetch docs → Simplify → Generate image → Generate audio.
    Returns the complete explanation with links to image and audio files.
    """
    request_id = str(uuid.uuid4())[:8]

    # Step 1: Fetch documentation
    try:
        doc_text = fetch_documentation(request.doc_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch documentation: {str(e)}")

    # Step 2: Simplify with AI
    try:
        explanation = simplify_feature(doc_text, request.pm_email or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI simplification failed: {str(e)}")

    # Step 3: Generate image (optional)
    image_url = None
    if request.generate_image:
        try:
            image_path = generate_feature_image(
                explanation["analogy"],
                f"{request_id}_{explanation['feature_name']}"
            )
            image_url = f"/output/images/{Path(image_path).name}"
        except Exception as e:
            print(f"⚠️ Image generation failed: {e}")

    # Step 4: Generate audio (optional)
    audio_url = None
    if request.generate_audio:
        try:
            audio_path = generate_narration(
                explanation["narration_script"],
                f"{request_id}_{explanation['feature_name']}"
            )
            audio_url = f"/output/audio/{Path(audio_path).name}"
        except Exception as e:
            print(f"⚠️ Audio generation failed: {e}")

    return ExplainResponse(
        id=request_id,
        feature_name=explanation["feature_name"],
        simple_explanation=explanation["simple_explanation"],
        analogy=explanation["analogy"],
        key_points=explanation["key_points"],
        troubleshooting_tips=explanation.get("troubleshooting_tips", []),
        gotchas=explanation.get("gotchas", []),
        narration_script=explanation["narration_script"],
        image_url=image_url,
        audio_url=audio_url,
        source_url=request.doc_url
    )


@app.post("/api/simplify")
async def simplify_only(request: SimplifyRequest):
    """Simplify documentation without generating image/audio (faster, cheaper)."""
    try:
        doc_text = fetch_documentation(request.doc_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch documentation: {str(e)}")

    try:
        explanation = simplify_feature(doc_text, request.pm_email or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI simplification failed: {str(e)}")

    return explanation


@app.get("/api/voices")
async def get_voices():
    """List available Polly neural voices."""
    return list_available_voices()
