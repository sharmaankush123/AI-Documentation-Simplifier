"""
🚀 Feature Explainer — Main Pipeline

This script ties everything together:
1. Fetches documentation from a URL
2. Simplifies it using AI (Bedrock Claude)
3. Generates an illustration (Bedrock Titan Image)
4. Creates audio narration (Amazon Polly)

Usage:
    python main.py

You'll be prompted to enter:
    - Documentation URL
    - (Optional) PM email content

Output:
    - output/images/   → Feature illustration (PNG)
    - output/audio/    → Narration (MP3)
    - output/          → explanation.json (full structured result)

Cost per run: ~$0.03-0.05 (less than ₹5!)
"""

import json
from pathlib import Path
from doc_parser import fetch_documentation
from simplifier import simplify_feature
from image_gen import generate_feature_image
from audio_gen import generate_narration


def run_pipeline():
    """Main pipeline — interactive mode."""

    print("\n" + "=" * 60)
    print("🚀 AI Feature Explainer")
    print("=" * 60)

    # --- Step 1: Get inputs ---
    print("\n📎 Step 1: Provide your inputs")
    doc_url = input("\nPaste the documentation URL: ").strip()

    print("\n📧 Paste the PM email content (or press Enter to skip).")
    print("   (Type 'END' on a new line when done)")
    pm_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        if line == "" and not pm_lines:
            break  # Skip if first line is empty
        pm_lines.append(line)
    pm_email = "\n".join(pm_lines)

    # --- Step 2: Fetch documentation ---
    print("\n📄 Step 2: Fetching documentation...")
    try:
        doc_text = fetch_documentation(doc_url)
        print(f"   ✅ Extracted {len(doc_text)} characters from the page")
    except Exception as e:
        print(f"   ❌ Error fetching URL: {e}")
        print("   Tip: Make sure the URL is accessible and try again.")
        return

    # --- Step 3: Simplify with AI ---
    print("\n🧠 Step 3: AI is simplifying the feature...")
    try:
        explanation = simplify_feature(doc_text, pm_email)
        print(f"   ✅ Feature: {explanation['feature_name']}")
        print(f"   ✅ Analogy: {explanation['analogy'][:80]}...")
    except Exception as e:
        print(f"   ❌ Error calling Bedrock: {e}")
        print("   Tip: Check your AWS credentials and Bedrock access.")
        return

    # --- Step 4: Generate illustration ---
    print("\n🎨 Step 4: Generating illustration...")
    try:
        image_path = generate_feature_image(
            explanation["analogy"],
            explanation["feature_name"]
        )
        print(f"   ✅ Image ready!")
    except Exception as e:
        print(f"   ⚠️  Image generation failed: {e}")
        print("   (Continuing without image...)")
        image_path = None

    # --- Step 5: Generate audio narration ---
    print("\n🔊 Step 5: Generating audio narration...")
    try:
        audio_path = generate_narration(
            explanation["narration_script"],
            explanation["feature_name"]
        )
        print(f"   ✅ Audio ready!")
    except Exception as e:
        print(f"   ⚠️  Audio generation failed: {e}")
        print("   (Continuing without audio...)")
        audio_path = None

    # --- Step 6: Save full result ---
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        **explanation,
        "source_url": doc_url,
        "image_path": image_path,
        "audio_path": audio_path
    }

    result_path = output_dir / "explanation.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    # --- Done! Print summary ---
    print("\n" + "=" * 60)
    print("✅ DONE! Here's your feature explanation:")
    print("=" * 60)

    print(f"\n📌 Feature: {explanation['feature_name']}")
    print(f"\n💡 Simple Explanation:\n   {explanation['simple_explanation']}")
    print(f"\n🎯 Analogy:\n   {explanation['analogy']}")

    print(f"\n📋 Key Points:")
    for point in explanation["key_points"]:
        print(f"   • {point}")

    if explanation.get("troubleshooting_tips"):
        print(f"\n🔧 Troubleshooting Tips:")
        for tip in explanation["troubleshooting_tips"]:
            print(f"   🛠️  {tip}")

    if explanation.get("gotchas"):
        print(f"\n⚠️  Gotchas:")
        for gotcha in explanation["gotchas"]:
            print(f"   ⚡ {gotcha}")

    print(f"\n📁 Output files:")
    if image_path:
        print(f"   🖼️  Image: {image_path}")
    if audio_path:
        print(f"   🔊 Audio: {audio_path}")
    print(f"   📄 JSON:  {result_path}")
    print()


if __name__ == "__main__":
    run_pipeline()
