"""
services/video_gen.py — Uses Amazon Nova Reel to generate animated explainer videos.

Nova Reel generates 6-second video clips from text prompts.
Videos are stored in S3 and downloaded locally after generation.

Requires:
    - An S3 bucket for video output
    - Bedrock access to amazon.nova-reel-v1:1 (us-east-1)
"""

import json
import time
import boto3
from pathlib import Path
import sys
sys.path.append("..")
from config import VIDEO_S3_BUCKET, VIDEO_REGION, NOVA_REEL_MODEL_ID, OUTPUT_DIR


# Regions to try for Nova Reel (fallback order)
VIDEO_REGIONS = [VIDEO_REGION, "us-west-2", "eu-west-1"]

# Ensure output directory exists
VIDEO_DIR = Path(OUTPUT_DIR) / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def generate_feature_video(scene_description: str, feature_name: str = "feature", 
                           duration_seconds: int = 6, wait_timeout: int = 300) -> str:
    """
    Generate an animated video clip using Amazon Nova Reel.

    Args:
        scene_description: Text describing the visual scene to generate
        feature_name: Used for the output filename
        duration_seconds: Video length (6, 12, 18, or 24 seconds — multiples of 6)
        wait_timeout: Max seconds to wait for video generation (default 5 min)

    Returns:
        Path to the downloaded MP4 file
    """
    # Try multiple regions as fallback
    last_error = None
    for region in VIDEO_REGIONS:
        try:
            return _generate_video_in_region(scene_description, feature_name, duration_seconds, wait_timeout, region)
        except Exception as e:
            last_error = e
            print(f"   ⚠️ Region {region} failed: {str(e)[:80]}")
            continue
    
    raise last_error or RuntimeError("All regions failed for video generation")


def _generate_video_in_region(scene_description: str, feature_name: str, 
                              duration_seconds: int, wait_timeout: int, region: str) -> str:
    """Generate video in a specific region."""
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
    s3_client = boto3.client("s3", region_name=region)

    # Clean feature name for S3 key
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)[:40]
    s3_output_prefix = f"feature-explainer/{safe_name}"
    s3_uri = f"s3://{VIDEO_S3_BUCKET}/{s3_output_prefix}"

    # Prepare the video generation request
    model_input = {
        "taskType": "TEXT_VIDEO",
        "textToVideoParams": {
            "text": scene_description
        },
        "videoGenerationConfig": {
            "durationSeconds": duration_seconds,
            "fps": 24,
            "dimension": "1280x720",
            "seed": 0
        }
    }

    # Start async video generation job
    print(f"🎬 Starting video generation in {region} for: {feature_name}")
    print(f"   Scene: {scene_description[:80]}...")
    print(f"   Duration: {duration_seconds}s | Output: {s3_uri}")

    invocation = bedrock_runtime.start_async_invoke(
        modelId=NOVA_REEL_MODEL_ID,
        modelInput=model_input,
        outputDataConfig={
            "s3OutputDataConfig": {
                "s3Uri": s3_uri
            }
        }
    )

    invocation_arn = invocation["invocationArn"]
    print(f"   Job ARN: {invocation_arn}")

    # Poll for completion
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > wait_timeout:
            raise TimeoutError(f"Video generation timed out after {wait_timeout}s")

        status_response = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)
        status = status_response["status"]

        if status == "Completed":
            print(f"   ✅ Video generated in {elapsed:.0f}s!")
            break
        elif status == "Failed":
            failure_msg = status_response.get("failureMessage", "Unknown error")
            raise RuntimeError(f"Video generation failed: {failure_msg}")
        else:
            # Still in progress
            print(f"   ⏳ Generating... ({elapsed:.0f}s elapsed)")
            time.sleep(15)  # Check every 15 seconds

    # Download the video from S3
    s3_video_key = f"{s3_output_prefix}/output.mp4"
    local_path = VIDEO_DIR / f"{safe_name}.mp4"

    print(f"   📥 Downloading from s3://{VIDEO_S3_BUCKET}/{s3_video_key}")
    s3_client.download_file(VIDEO_S3_BUCKET, s3_video_key, str(local_path))
    print(f"   ✅ Video saved: {local_path}")

    return str(local_path)


def combine_video_audio(video_path: str, audio_path: str, output_path: str = None) -> str:
    """
    Combine a video file with an audio narration track using ffmpeg.

    Args:
        video_path: Path to the video file (MP4)
        audio_path: Path to the audio file (MP3)
        output_path: Path for the combined output (optional)

    Returns:
        Path to the combined video file
    """
    import subprocess

    if output_path is None:
        output_path = str(VIDEO_DIR / "final_explainer.mp4")

    # Use ffmpeg to combine video + audio
    # -shortest: end when the shortest stream ends
    cmd = [
        "ffmpeg", "-y",  # overwrite output
        "-i", video_path,    # video input
        "-i", audio_path,    # audio input
        "-c:v", "copy",      # copy video stream (no re-encode)
        "-c:a", "aac",       # encode audio as AAC
        "-shortest",         # end at shortest stream
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[:200]}")

    print(f"   ✅ Final video with narration: {output_path}")
    return output_path


if __name__ == "__main__":
    # Quick test
    test_scene = (
        "An animated visualization of a filing cabinet transforming into a highway, "
        "with files flowing like cars between a cabinet and a computer screen. "
        "Smooth camera dolly forward. Bright colors, clean modern style."
    )
    path = generate_feature_video(test_scene, "s3-files-test")
    print(f"\nGenerated: {path}")
