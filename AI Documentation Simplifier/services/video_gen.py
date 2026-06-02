"""
services/video_gen.py — Generates animated explainer videos using Claude + HyperFrames.

Approach:
    1. Claude generates scene descriptions (what to animate)
    2. We inject those into a WORKING HyperFrames template with proper GSAP timeline
    3. HyperFrames renders to MP4
    4. ffmpeg combines with narration audio

Cost: FREE (HyperFrames open source, Claude via existing Bedrock)
"""

import subprocess
import json
import boto3
from pathlib import Path
from botocore.config import Config

import sys
sys.path.append("..")
from config import OUTPUT_DIR, AWS_REGION, CLAUDE_MODEL_ID

VIDEO_DIR = Path(OUTPUT_DIR) / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

HYPERFRAMES_PROJECT = Path(OUTPUT_DIR) / "hyperframes_project"

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION,
                       config=Config(read_timeout=300))


def generate_explainer_video(narration_script: str, feature_name: str, audio_path: str,
                             analogy: str = "", key_points: list = None) -> str:
    """Generate animated explainer video with motion graphics + narration."""
    from moviepy import AudioFileClip
    audio = AudioFileClip(audio_path)
    duration = int(audio.duration)

    # Step 1: Get animation scene plan from Claude
    print(f"🎬 Generating animation for: {feature_name}")
    scenes = _get_scene_plan(narration_script, feature_name, analogy, key_points or [], duration)

    # Step 2: Build HTML from template + scenes
    html = _build_html(feature_name, scenes, duration)

    # Step 3: Set up project and render
    project_dir = HYPERFRAMES_PROJECT
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "index.html").write_text(html)
    (project_dir / "hyperframes.json").write_text(json.dumps({"name": "explainer"}))
    (project_dir / "package.json").write_text(json.dumps({"name": "explainer", "private": True}))

    print("   🎨 Rendering animation to video...")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)[:40]
    rendered_path = (VIDEO_DIR / f"{safe_name}_noaudio.mp4").resolve()

    result = subprocess.run(
        ["hyperframes", "render", "--output", str(rendered_path)],
        capture_output=True, text=True, cwd=str(project_dir.resolve())
    )

    if result.returncode != 0 and not rendered_path.exists():
        raise RuntimeError(f"Render failed: {result.stderr[-200:]}")

    # Step 4: Combine with audio
    output_path = str(VIDEO_DIR / f"{safe_name}.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(rendered_path), "-i", audio_path,
         "-c:v", "copy", "-c:a", "aac", "-shortest", output_path],
        capture_output=True
    )

    if not Path(output_path).exists():
        import shutil
        shutil.copy(str(rendered_path), output_path)

    rendered_path.unlink(missing_ok=True)
    print(f"✅ Video saved: {output_path}")
    return output_path


def _get_scene_plan(narration, feature_name, analogy, key_points, duration):
    """Create scenes that match EXACTLY what's being spoken at each moment."""
    import re
    
    # Split narration into sentences — these ARE the scenes
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', narration.strip()) if s.strip()]
    time_per_sentence = duration / len(sentences)
    
    # Build timed narration
    timed = ""
    for i, sent in enumerate(sentences):
        start = round(i * time_per_sentence, 1)
        end = round((i + 1) * time_per_sentence, 1)
        timed += f"  [{start}s - {end}s] \"{sent}\"\n"

    prompt = f"""Create a visual scene for EACH spoken sentence below. The on-screen text must match what's being said.

TIMED NARRATION (what the viewer hears):
{timed}

For each sentence, return:
- "start": start time (from timestamps above)
- "end": end time (from timestamps above)
- "title": 2-5 word headline summarizing THAT sentence
- "description": the spoken sentence itself (shortened to max 15 words if needed)
- "icon": best match: cloud, server, file, lock, arrow, folder, database, globe, shield, coin, clock, rocket, check, warning, link, gear
- "color": #FF9900 for AWS, #4CAF50 for positive, #2196F3 for info, #9C27B0 for features
- "animation": one of: slideUp, slideLeft, scaleIn, fadeIn, rotateIn, bounceIn

CRITICAL: Return exactly {len(sentences)} scenes. Each scene's description must reflect the EXACT sentence being spoken at that time.
Return ONLY a JSON array."""

    response = bedrock.converse(
        modelId=CLAUDE_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 2000, "temperature": 0.2}
    )

    text = response["output"]["message"]["content"][0]["text"]
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text.strip())


def _build_html(feature_name, scenes, duration):
    """Build HyperFrames HTML with proper timeline from scene plan."""

    # SVG icons library
    icons = {
        "cloud": '<path d="M25 60 C10 60 0 50 0 40 C0 28 10 20 20 20 C22 10 32 2 45 2 C58 2 68 12 70 22 C82 22 90 32 90 42 C90 55 80 62 70 60 Z" fill="{color}" opacity="0.9"/>',
        "server": '<rect x="15" y="10" width="60" height="70" rx="5" fill="{color}" opacity="0.9"/><rect x="25" y="20" width="40" height="8" rx="2" fill="#1a1a2e"/><rect x="25" y="35" width="40" height="8" rx="2" fill="#1a1a2e"/><rect x="25" y="50" width="40" height="8" rx="2" fill="#1a1a2e"/><circle cx="60" cy="68" r="4" fill="#00ff88"/>',
        "file": '<rect x="15" y="5" width="50" height="70" rx="3" fill="{color}" opacity="0.9"/><polygon points="45,5 65,25 45,25" fill="#1a1a2e" opacity="0.3"/><rect x="25" y="35" width="30" height="4" rx="1" fill="#1a1a2e" opacity="0.5"/><rect x="25" y="45" width="25" height="4" rx="1" fill="#1a1a2e" opacity="0.5"/><rect x="25" y="55" width="20" height="4" rx="1" fill="#1a1a2e" opacity="0.5"/>',
        "lock": '<rect x="25" y="40" width="40" height="35" rx="5" fill="{color}"/><path d="M32 40 V28 C32 15 58 15 58 28 V40" fill="none" stroke="{color}" stroke-width="6"/><circle cx="45" cy="55" r="5" fill="#1a1a2e"/>',
        "arrow": '<path d="M10 45 H70 L55 30 M70 45 L55 60" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>',
        "folder": '<path d="M5 25 H35 L40 20 H85 V70 H5 Z" fill="{color}" opacity="0.9"/><rect x="5" y="30" width="80" height="40" rx="2" fill="{color}"/>',
        "database": '<ellipse cx="45" cy="20" rx="35" ry="12" fill="{color}"/><rect x="10" y="20" width="70" height="45" fill="{color}"/><ellipse cx="45" cy="65" rx="35" ry="12" fill="{color}"/><ellipse cx="45" cy="42" rx="35" ry="8" fill="#1a1a2e" opacity="0.2"/>',
        "globe": '<circle cx="45" cy="45" r="35" fill="none" stroke="{color}" stroke-width="4"/><ellipse cx="45" cy="45" rx="18" ry="35" fill="none" stroke="{color}" stroke-width="2"/><line x1="10" y1="45" x2="80" y2="45" stroke="{color}" stroke-width="2"/><path d="M15 28 Q45 22 75 28" fill="none" stroke="{color}" stroke-width="2"/><path d="M15 62 Q45 68 75 62" fill="none" stroke="{color}" stroke-width="2"/>',
        "shield": '<path d="M45 5 L80 20 V50 C80 70 45 85 45 85 C45 85 10 70 10 50 V20 Z" fill="{color}" opacity="0.9"/><path d="M35 45 L43 55 L60 35" fill="none" stroke="#1a1a2e" stroke-width="5" stroke-linecap="round"/>',
        "coin": '<circle cx="45" cy="45" r="35" fill="{color}"/><circle cx="45" cy="45" r="28" fill="none" stroke="#1a1a2e" stroke-width="3" opacity="0.3"/><text x="45" y="55" text-anchor="middle" font-size="30" font-weight="bold" fill="#1a1a2e">$</text>',
        "clock": '<circle cx="45" cy="45" r="35" fill="none" stroke="{color}" stroke-width="5"/><line x1="45" y1="45" x2="45" y2="22" stroke="{color}" stroke-width="4" stroke-linecap="round"/><line x1="45" y1="45" x2="62" y2="45" stroke="{color}" stroke-width="3" stroke-linecap="round"/><circle cx="45" cy="45" r="4" fill="{color}"/>',
        "rocket": '<path d="M45 10 C55 10 65 25 65 50 L55 65 H35 L25 50 C25 25 35 10 45 10Z" fill="{color}"/><rect x="35" y="60" width="20" height="10" rx="2" fill="#FF6B35"/><polygon points="25,50 15,60 25,55" fill="{color}"/><polygon points="65,50 75,60 65,55" fill="{color}"/>',
        "check": '<circle cx="45" cy="45" r="35" fill="{color}"/><path d="M25 45 L40 60 L65 30" fill="none" stroke="white" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
        "warning": '<path d="M45 10 L85 75 H5 Z" fill="{color}"/><text x="45" y="62" text-anchor="middle" font-size="35" font-weight="bold" fill="#1a1a2e">!</text>',
        "link": '<path d="M30 50 Q30 35 45 35 L55 35 Q70 35 70 50 Q70 65 55 65" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/><path d="M60 40 Q60 55 45 55 L35 55 Q20 55 20 40 Q20 25 35 25" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>',
        "gear": '<circle cx="45" cy="45" r="15" fill="none" stroke="{color}" stroke-width="8"/><circle cx="45" cy="45" r="6" fill="{color}"/>'
    }

    # Build scene elements
    elements = ""
    animations = ""

    for i, scene in enumerate(scenes):
        start = scene.get("start", i * (duration / len(scenes)))
        icon_name = scene.get("icon", "cloud")
        color = scene.get("color", "#FF9900")
        title = scene.get("title", "")
        desc = scene.get("description", "")
        anim_type = scene.get("animation", "fadeIn")

        icon_svg = icons.get(icon_name, icons["cloud"]).replace("{color}", color)

        # Position elements
        elements += f'''
    <div id="scene{i}" style="position:absolute;top:0;left:0;width:100%;height:100%;opacity:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
      <svg width="180" height="180" viewBox="0 0 90 90" id="icon{i}" style="margin-bottom:30px;">{icon_svg}</svg>
      <div id="title{i}" style="font-size:52px;font-weight:bold;color:white;text-align:center;margin-bottom:15px;text-shadow:0 0 20px {color};">{title}</div>
      <div id="desc{i}" style="font-size:28px;color:#ccccee;text-align:center;max-width:900px;line-height:1.4;">{desc}</div>
    </div>'''

        # Build GSAP animations based on type
        enter_props = {
            "slideUp": "y: 80, opacity: 0",
            "slideLeft": "x: -100, opacity: 0",
            "scaleIn": "scale: 0.3, opacity: 0",
            "fadeIn": "opacity: 0",
            "rotateIn": "rotation: -15, scale: 0.5, opacity: 0",
            "bounceIn": "scale: 0, opacity: 0, ease: 'back.out(1.7)'"
        }.get(anim_type, "opacity: 0")

        scene_dur = scene.get("end", start + duration/len(scenes)) - start
        animations += f'''
      // Scene {i}: {title}
      tl.to("#scene{i}", {{ opacity: 1, duration: 0.3 }}, {start});
      tl.from("#icon{i}", {{ {enter_props}, duration: 0.8 }}, {start + 0.2});
      tl.from("#title{i}", {{ y: 30, opacity: 0, duration: 0.6 }}, {start + 0.5});
      tl.from("#desc{i}", {{ y: 20, opacity: 0, duration: 0.6 }}, {start + 0.8});
      tl.to("#scene{i}", {{ opacity: 0, duration: 0.5 }}, {start + scene_dur - 0.5});
'''

    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=1920, height=1080"/>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    html, body {{ margin:0; width:1920px; height:1080px; overflow:hidden; background:#1a1a2e; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1920" data-height="1080">
    {elements}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    {animations}
    window.__timelines["main"] = tl;
  </script>
</body>
</html>'''

    return html


if __name__ == "__main__":
    test_narration = (
        "Hey! Let me explain Amazon S3 Files to you. "
        "Think of S3 as a massive online hard drive that never runs out of space. "
        "You upload files, and AWS stores them safely across multiple locations. "
        "Each file gets a unique web address so you can access it from anywhere. "
        "The cool part? You only pay for what you actually store. No upfront costs. "
        "S3 also handles security automatically — your files are encrypted by default. "
        "And if you accidentally delete something, versioning can save you. "
        "That's basically it — cloud storage that's simple, safe, and scales forever."
    )

    test_audio = Path(OUTPUT_DIR) / "audio" / "Amazon_S3_Files.mp3"
    if test_audio.exists():
        path = generate_explainer_video(
            test_narration, "Amazon S3 Files", str(test_audio),
            analogy="S3 is like a self-expanding storage unit with automatic backups",
            key_points=[
                "Upload any file type — documents, images, videos",
                "Each file gets a unique URL",
                "Pay only for what you store",
                "Encryption by default",
                "Versioning protects against accidental deletion",
            ]
        )
        print(f"\n🎬 Generated: {path}")
    else:
        print(f"⚠️ No test audio at: {test_audio}")
