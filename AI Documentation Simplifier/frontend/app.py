"""
🚀 Feature Explainer — Streamlit Frontend

Generates AI-powered feature explanations with:
- Claude Sonnet 4.6 (simplification + analogies)
- Amazon Polly (human-like narration)

Run:
    streamlit run frontend/app.py
"""

import streamlit as st
import json
import time
from pathlib import Path
import sys
import importlib

sys.path.append(str(Path(__file__).parent.parent))

import services.simplifier
import services.audio_gen
importlib.reload(services.simplifier)
importlib.reload(services.audio_gen)

from services.doc_parser import fetch_documentation
from services.simplifier import simplify_feature
from services.audio_gen import generate_narration
from services.video_gen import generate_explainer_video
from config import APP_TITLE, APP_DESCRIPTION

# === Page Config ===
st.set_page_config(
    page_title="Feature Explainer",
    page_icon="🚀",
    layout="wide"
)

# === Custom CSS ===
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF9900, #232F3E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .analogy-box {
        background: #f0f7ff;
        border-left: 4px solid #FF9900;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    .tip-box {
        background: #fff8e1;
        border-left: 4px solid #ffc107;
        padding: 0.8rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .gotcha-box {
        background: #fff3e0;
        border-left: 4px solid #ff5722;
        padding: 0.8rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .key-point {
        padding: 0.4rem 0;
    }
</style>
""", unsafe_allow_html=True)

# === Header ===
st.markdown(f'<h1 class="main-header">{APP_TITLE}</h1>', unsafe_allow_html=True)
st.caption(APP_DESCRIPTION)
st.divider()

# === Input Section ===
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📎 Documentation URL")
    doc_url = st.text_input(
        "Paste the feature documentation link",
        placeholder="https://docs.aws.amazon.com/...",
        label_visibility="collapsed"
    )

with col2:
    st.subheader("⚙️ Options")
    gen_audio = st.checkbox("🎙️ Generate audio narration (Amazon Polly)", value=True,
                           help="Natural human-like voice explains the feature")
    gen_video = st.checkbox("🎬 Generate explainer video", value=False,
                           help="Animated video with cartoon character + narration (FREE, requires audio)")

st.subheader("📧 PM Email (Optional)")
pm_email = st.text_area(
    "Paste the PM feature email — internal troubleshooting details help!",
    height=150,
    placeholder="Paste the PM's feature announcement email here (optional)...\n\nThis can include:\n- Internal troubleshooting steps\n- Known limitations\n- Edge cases to watch for",
    label_visibility="collapsed"
)

# === Generate Button ===
st.divider()

if st.button("🚀 Explain This Feature!", type="primary", use_container_width=True):
    if not doc_url:
        st.error("Please paste a documentation URL first!")
    else:
        progress = st.progress(0)
        status = st.empty()

        try:
            # Step 1: Fetch docs
            status.info("📄 Fetching documentation...")
            progress.progress(15)
            doc_text = fetch_documentation(doc_url)
            progress.progress(30)

            # Step 2: Simplify with AI
            status.info("🧠 AI is simplifying the feature...")
            explanation = simplify_feature(doc_text, pm_email)
            progress.progress(60)

            # Step 3: Generate audio narration
            audio_path = None
            if gen_audio:
                status.info("🎙️ Generating human-like narration...")
                try:
                    audio_path = generate_narration(explanation["narration_script"], explanation["feature_name"])
                except Exception as aud_err:
                    st.warning(f"⚠️ Audio skipped: {str(aud_err)[:100]}")

            # Step 4: Generate video
            video_path = None
            if gen_video and audio_path:
                status.info("🎬 Generating animated explainer video...")
                try:
                    video_path = generate_explainer_video(
                        explanation["narration_script"],
                        explanation["feature_name"],
                        audio_path,
                        analogy=explanation.get("analogy", ""),
                        key_points=explanation.get("key_points", [])
                    )
                except Exception as vid_err:
                    st.warning(f"⚠️ Video skipped: {str(vid_err)[:100]}")
            elif gen_video and not audio_path:
                st.warning("⚠️ Video requires audio — enable audio generation first")

            progress.progress(100)

            status.success("✅ Done! Here's your feature explanation:")
            time.sleep(0.5)
            status.empty()
            progress.empty()

            # === Display Results ===
            st.divider()
            st.header(f"📌 {explanation['feature_name']}")

            # Audio player at the top
            if audio_path:
                st.subheader("🎙️ Listen to Explanation")
                st.audio(audio_path, format="audio/mp3")
                st.caption("🗣️ Human-like voice powered by Amazon Polly (Generative)")

            # Video player
            if video_path:
                st.subheader("🎬 Watch Explainer Video")
                st.video(video_path)
                st.caption("🎥 Animated video generated locally (FREE — Manim + MoviePy)")

            # Simple explanation
            st.subheader("💡 Simple Explanation")
            st.write(explanation["simple_explanation"])

            # Analogy
            st.subheader("🎯 Analogy")
            st.markdown(f'<div class="analogy-box">💡 {explanation["analogy"]}</div>', unsafe_allow_html=True)

            # Key Points
            st.subheader("📋 Key Points")
            for point in explanation["key_points"]:
                st.markdown(f"• {point}")

            # Troubleshooting Tips
            if explanation.get("troubleshooting_tips"):
                st.subheader("🔧 Troubleshooting Tips")
                for tip in explanation["troubleshooting_tips"]:
                    st.markdown(f'<div class="tip-box">🛠️ {tip}</div>', unsafe_allow_html=True)

            # Gotchas
            if explanation.get("gotchas"):
                st.subheader("⚠️ Gotchas & Edge Cases")
                for gotcha in explanation["gotchas"]:
                    st.markdown(f'<div class="gotcha-box">⚡ {gotcha}</div>', unsafe_allow_html=True)

            # Narration script
            with st.expander("📝 Full Narration Script"):
                st.write(explanation["narration_script"])

            # Download section
            st.divider()
            st.subheader("📥 Download")
            dl_cols = st.columns(3)
            with dl_cols[0]:
                st.download_button(
                    "📄 Download Explanation (JSON)",
                    json.dumps(explanation, indent=2),
                    file_name=f"{explanation['feature_name']}_explanation.json",
                    mime="application/json"
                )
            if audio_path:
                with dl_cols[1]:
                    with open(audio_path, "rb") as f:
                        st.download_button("🎙️ Download Audio (MP3)", f.read(),
                                          file_name=f"{explanation['feature_name']}.mp3",
                                          mime="audio/mpeg")
            if video_path:
                with dl_cols[2]:
                    with open(video_path, "rb") as f:
                        st.download_button("🎬 Download Video (MP4)", f.read(),
                                          file_name=f"{explanation['feature_name']}.mp4",
                                          mime="video/mp4")

        except Exception as e:
            progress.empty()
            status.empty()
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Tips:\n- Check if the URL is accessible\n- Verify AWS credentials are configured\n- Make sure Bedrock model access is enabled")

# === Footer ===
st.divider()
st.caption("Built with ❤️ using Amazon Bedrock (Claude Sonnet 4.6), Amazon Polly & HyperFrames | ~₹5 per explanation")
