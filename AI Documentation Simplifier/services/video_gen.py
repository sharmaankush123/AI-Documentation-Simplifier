"""
services/video_gen.py — Generates animated explainer videos using Manim + MoviePy.

Pipeline:
    1. Manim renders animated text slides from key points
    2. Avatar image is composited as a "presenter" in the corner
    3. MoviePy combines everything with the Polly/ElevenLabs audio track

Cost: FREE (all open-source, runs locally)
"""

import subprocess
import tempfile
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

from moviepy import (
    ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip
)

import sys
sys.path.append("..")
from config import OUTPUT_DIR

VIDEO_DIR = Path(OUTPUT_DIR) / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

AVATAR_PATH = Path(__file__).parent.parent / "assets" / "avatar.png"
VIDEO_WIDTH, VIDEO_HEIGHT = 1280, 720
FPS = 24

# macOS font paths
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
if not Path(FONT_BOLD).exists():
    FONT_BOLD = "/System/Library/Fonts/Helvetica.ttc"
    FONT_REGULAR = "/System/Library/Fonts/Helvetica.ttc"


def generate_explainer_video(key_points: list, feature_name: str, audio_path: str) -> str:
    """
    Generate an animated explainer video from key points + audio.

    Args:
        key_points: List of strings (bullet points to animate)
        feature_name: Name of the feature being explained
        audio_path: Path to the narration MP3

    Returns:
        Path to the final MP4 video
    """
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Calculate time per slide
    num_slides = len(key_points) + 1  # +1 for title slide
    time_per_slide = total_duration / num_slides

    clips = []

    # Title slide
    clips.append(_make_title_slide(feature_name, time_per_slide))

    # Key point slides
    for i, point in enumerate(key_points):
        clips.append(_make_point_slide(point, i + 1, len(key_points), time_per_slide))

    # Concatenate all slides
    video = concatenate_videoclips(clips, method="compose")

    # Add avatar overlay (bottom-right corner)
    avatar_clip = _make_avatar_clip(total_duration)
    final = CompositeVideoClip([video, avatar_clip])

    # Set audio
    final = final.with_audio(audio)

    # Export
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)[:40]
    output_path = str(VIDEO_DIR / f"{safe_name}.mp4")

    final.write_videofile(output_path, fps=FPS, codec="libx264", audio_codec="aac",
                          logger=None, threads=4)

    print(f"✅ Video saved: {output_path}")
    return output_path


def _make_title_slide(title: str, duration: float) -> CompositeVideoClip:
    """Create an animated title slide."""
    bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(35, 47, 62)).with_duration(duration)

    # Title text
    wrapped = textwrap.fill(title, width=35)
    title_clip = TextClip(
        text=wrapped,
        font_size=48, color="white", font=FONT_BOLD,
        size=(VIDEO_WIDTH - 300, VIDEO_HEIGHT - 200), method="caption"
    ).with_duration(duration).with_position("center")

    # Subtitle
    sub = TextClip(
        text="AI Feature Explainer", font_size=26, color="#FF9900", font=FONT_REGULAR,
        size=(400, 50), method="caption"
    ).with_duration(duration).with_position(("center", VIDEO_HEIGHT - 80))

    return CompositeVideoClip([bg, title_clip, sub]).with_duration(duration)


def _make_point_slide(point: str, index: int, total: int, duration: float) -> CompositeVideoClip:
    """Create a slide for a single key point with animation."""
    # Gradient-style background
    colors = [(26, 35, 126), (0, 77, 64), (74, 20, 140), (21, 101, 192), (230, 81, 0)]
    bg_color = colors[index % len(colors)]
    bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=bg_color).with_duration(duration)

    # Point number badge - positioned with safe margin
    badge = TextClip(
        text=f"  {index}/{total}  ", font_size=22, color="white",
        bg_color="#FF9900", font=FONT_BOLD,
        size=(100, 40), method="caption"
    ).with_duration(duration).with_position((60, 40))

    # Main point text - constrained to safe area with padding
    wrapped = textwrap.fill(point, width=45)
    point_clip = TextClip(
        text=wrapped, font_size=36, color="white", font=FONT_REGULAR,
        size=(VIDEO_WIDTH - 400, VIDEO_HEIGHT - 200), method="caption"
    ).with_duration(duration).with_position(("center", "center"))

    return CompositeVideoClip([bg, badge, point_clip]).with_duration(duration)


def _make_avatar_clip(duration: float) -> ImageClip:
    """Create the avatar overlay for bottom-right corner."""
    if not AVATAR_PATH.exists():
        # Return empty if no avatar
        return ColorClip(size=(1, 1), color=(0, 0, 0, 0)).with_duration(duration).with_position((0, 0))

    # Load and resize avatar
    avatar = Image.open(AVATAR_PATH).convert("RGBA").resize((120, 120))

    # Convert to numpy array for MoviePy
    avatar_array = np.array(avatar)

    clip = ImageClip(avatar_array, is_mask=False, transparent=True)
    clip = clip.with_duration(duration)
    clip = clip.with_position((VIDEO_WIDTH - 140, VIDEO_HEIGHT - 140))

    return clip


if __name__ == "__main__":
    # Quick test with sample data
    test_points = [
        "S3 is like a giant filing cabinet in the cloud",
        "You can store any file type — images, videos, backups",
        "Pay only for what you store — no upfront costs",
        "Access your files from anywhere with a URL",
    ]

    # Check if we have a test audio file
    test_audio = Path(OUTPUT_DIR) / "audio" / "Amazon_S3_Files.mp3"
    if test_audio.exists():
        path = generate_explainer_video(test_points, "Amazon S3 Overview", str(test_audio))
        print(f"\n🎬 Generated: {path}")
    else:
        print("⚠️ No test audio found. Run audio generation first.")
        print(f"   Expected: {test_audio}")
