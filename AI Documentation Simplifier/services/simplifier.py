"""
services/simplifier.py — Uses Amazon Bedrock (Claude) to simplify technical documentation
                         into easy-to-understand explanations with analogies.

Uses the Converse API (newer, works better with inference profiles).
"""

import json
import boto3
import sys
sys.path.append("..")
from config import AWS_REGION, CLAUDE_MODEL_ID


# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

SIMPLIFY_PROMPT = """You are a friendly tech educator who explains complex AWS features 
to support engineers who need to quickly understand and troubleshoot the feature.

Your job:
1. Explain WHAT the feature does in 2-3 simple sentences (like explaining to a friend)
2. Give a real-world ANALOGY that makes it click instantly
3. List the KEY POINTS an engineer needs to know (5-7 bullets)
4. Extract TROUBLESHOOTING TIPS from the PM email (if provided)
5. Mention common GOTCHAS or edge cases

Rules:
- Use simple, conversational language (no jargon without explanation)
- The analogy should be relatable (kitchen, traffic, library, etc.)
- Keep the total explanation under 500 words
- Format troubleshooting tips as actionable steps
- The narration_script should sound like a human colleague explaining it over coffee

Return your response in this EXACT JSON format (no other text outside the JSON):
{
    "feature_name": "Name of the feature",
    "simple_explanation": "2-3 sentence explanation",
    "analogy": "The real-world analogy",
    "analogy_image_prompt": "A short visual description for generating an illustration of the analogy (no text/words, simple shapes, educational style)",
    "key_points": ["point 1", "point 2", ...],
    "troubleshooting_tips": ["tip 1", "tip 2", ...],
    "gotchas": ["gotcha 1", "gotcha 2", ...],
    "narration_script": "A 1-2 minute spoken explanation combining the above in a natural, conversational tone. Start with 'Hey! Let me explain...' and keep it friendly."
}
"""


def simplify_feature(doc_text: str, pm_email: str = "") -> dict:
    """
    Takes documentation text and optional PM email, returns simplified explanation.
    Uses the Converse API which works better with inference profiles.
    """

    user_message = f"""Here's the technical documentation for a new AWS feature:

---DOCUMENTATION---
{doc_text}
---END DOCUMENTATION---
"""

    if pm_email.strip():
        user_message += f"""

And here's the internal PM email about this feature (may contain troubleshooting info):

---PM EMAIL---
{pm_email}
---END PM EMAIL---
"""

    user_message += "\n\nPlease simplify this feature and generate the explanation in the JSON format specified."

    # Use the Converse API (works better with inference profiles)
    response = bedrock.converse(
        modelId=CLAUDE_MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": SIMPLIFY_PROMPT + "\n\n" + user_message}
                ]
            }
        ],
        inferenceConfig={
            "maxTokens": 2500,
            "temperature": 0.7
        }
    )

    # Extract text from Converse API response
    assistant_text = response["output"]["message"]["content"][0]["text"]

    # Parse JSON from response (handle markdown code blocks)
    if "```json" in assistant_text:
        assistant_text = assistant_text.split("```json")[1].split("```")[0]
    elif "```" in assistant_text:
        assistant_text = assistant_text.split("```")[1].split("```")[0]

    result = json.loads(assistant_text.strip())
    return result
