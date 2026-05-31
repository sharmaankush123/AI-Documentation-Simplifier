"""
services/image_gen.py — Uses Claude to generate SVG illustrations of features.

Claude generates clean educational SVG diagrams — perfect for explaining
concepts visually with shapes, arrows, and labels.
"""

import json
import boto3
from pathlib import Path
import sys
sys.path.append("..")
from config import AWS_REGION, CLAUDE_MODEL_ID, IMAGES_DIR


# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Ensure output directory exists
Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)

SVG_SYSTEM_PROMPT = """You are an expert at creating SVG diagrams for educational content.
When asked to illustrate a concept, you MUST respond with ONLY a valid SVG element.
Do NOT include any explanation, markdown, or code blocks — just the raw SVG starting with <svg.

Requirements for your SVG:
- Start with: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">
- End with: </svg>
- Use professional colors: #FF9900 (orange), #232F3E (dark), #1B8BDB (blue), #2E8B57 (green), #6B48FF (purple)
- Include shapes: rectangles with rounded corners, circles, arrows (using polygon or path)
- Add SHORT text labels (2-4 words max)
- Draw arrows to show flow/relationships
- Keep it clean — max 6-8 elements
- Make it look like a professional architecture/whiteboard diagram
- NO external references, NO images, NO fonts — pure SVG only"""


def generate_feature_image(analogy: str, feature_name: str = "feature") -> str:
    """
    Generate an SVG illustration using Claude.

    Args:
        analogy: The concept/analogy to illustrate
        feature_name: Used for the output filename

    Returns:
        Path to the saved SVG file
    """

    user_prompt = f"Create an SVG diagram illustrating this concept: {analogy}"

    # Call Claude to generate SVG
    response = bedrock.converse(
        modelId=CLAUDE_MODEL_ID,
        system=[{"text": SVG_SYSTEM_PROMPT}],
        messages=[
            {
                "role": "user",
                "content": [{"text": user_prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 4000,
            "temperature": 0.5
        }
    )

    assistant_text = response["output"]["message"]["content"][0]["text"]

    # Extract SVG content — try multiple approaches
    svg_content = None

    # Method 1: Code blocks
    if "```" in assistant_text:
        parts = assistant_text.split("```")
        for i, part in enumerate(parts):
            # Check odd-indexed parts (inside code blocks)
            if i % 2 == 1:
                clean = part.strip()
                # Remove language identifier (svg, xml, html)
                if clean.startswith(("svg", "xml", "html")):
                    clean = clean.split("\n", 1)[1] if "\n" in clean else clean
                if "<svg" in clean:
                    svg_content = clean.strip()
                    break

    # Method 2: Raw SVG in text
    if svg_content is None and "<svg" in assistant_text and "</svg>" in assistant_text:
        start = assistant_text.find("<svg")
        end = assistant_text.rfind("</svg>") + 6
        svg_content = assistant_text[start:end]

    # Method 3: The entire response might be just SVG
    if svg_content is None and assistant_text.strip().startswith("<svg"):
        svg_content = assistant_text.strip()

    # Fallback: Generate a simple placeholder
    if svg_content is None or "<svg" not in svg_content:
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">
  <rect width="800" height="500" fill="#f0f4f8" rx="12"/>
  <rect x="50" y="50" width="300" height="80" fill="#FF9900" rx="8"/>
  <text x="200" y="98" text-anchor="middle" font-size="18" font-family="Arial" fill="white" font-weight="bold">{feature_name[:25]}</text>
  <rect x="450" y="50" width="300" height="80" fill="#232F3E" rx="8"/>
  <text x="600" y="98" text-anchor="middle" font-size="16" font-family="Arial" fill="white">Simplified Explanation</text>
  <polygon points="370,90 430,90 400,90" fill="#666"/>
  <line x1="350" y1="90" x2="450" y2="90" stroke="#666" stroke-width="3" marker-end="url(#arrow)"/>
  <rect x="150" y="200" width="500" height="250" fill="white" rx="8" stroke="#ddd" stroke-width="2"/>
  <text x="400" y="240" text-anchor="middle" font-size="16" font-family="Arial" fill="#333">See text explanation above</text>
  <text x="400" y="280" text-anchor="middle" font-size="14" font-family="Arial" fill="#666">AI diagram generation in progress...</text>
</svg>'''

    # Save as SVG file
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)[:40]
    output_path = Path(IMAGES_DIR) / f"{safe_name}.svg"

    with open(output_path, "w") as f:
        f.write(svg_content)

    return str(output_path)


def generate_multiple_frames(key_points: list, feature_name: str, analogy: str) -> list:
    """
    Generate multiple SVG frames (one per key point) for video creation.
    
    Returns:
        List of paths to SVG files
    """
    frames = []
    
    # Frame 1: Title + Analogy
    frames.append(generate_feature_image(analogy, f"{feature_name}_frame1"))
    
    # Additional frames for key points (group 2-3 points per frame)
    for i in range(0, len(key_points), 2):
        chunk = key_points[i:i+2]
        prompt = f"A diagram showing: {', '.join(chunk)}. In the context of {feature_name}."
        frame_path = generate_feature_image(prompt, f"{feature_name}_frame{i+2}")
        frames.append(frame_path)
    
    return frames
