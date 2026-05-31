"""
Quick test script to verify Bedrock connectivity.
Run: python test_bedrock.py
"""
import json
import boto3
import sys

# Test configuration
REGION = "eu-west-1"
MODEL_ID = "eu.anthropic.claude-sonnet-4-5-20250929-v1:0"

print(f"Testing Bedrock connection...")
print(f"  Region: {REGION}")
print(f"  Model:  {MODEL_ID}")
print(f"  Boto3:  {boto3.__version__}")
print()

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# Test 1: Try converse API
print("--- Test 1: Converse API ---")
try:
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": "Say hello in one word."}]
            }
        ],
        inferenceConfig={"maxTokens": 50, "temperature": 0.5}
    )
    text = response["output"]["message"]["content"][0]["text"]
    print(f"  ✅ Converse API works! Response: {text}")
except Exception as e:
    print(f"  ❌ Converse API failed: {e}")

# Test 2: Try invoke_model API
print("\n--- Test 2: InvokeModel API ---")
try:
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "Say hello in one word."}]
        })
    )
    body = json.loads(response["body"].read())
    text = body["content"][0]["text"]
    print(f"  ✅ InvokeModel API works! Response: {text}")
except Exception as e:
    print(f"  ❌ InvokeModel API failed: {e}")

# Test 3: Try different model IDs
print("\n--- Test 3: Alternative model IDs ---")
alt_models = [
    "eu.anthropic.claude-sonnet-4-6",
    "eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-haiku-4-5-20251001-v1:0",
]
for mid in alt_models:
    try:
        response = bedrock.converse(
            modelId=mid,
            messages=[{"role": "user", "content": [{"text": "Hi"}]}],
            inferenceConfig={"maxTokens": 10}
        )
        text = response["output"]["message"]["content"][0]["text"]
        print(f"  ✅ {mid} → {text[:30]}")
    except Exception as e:
        err_msg = str(e)[:80]
        print(f"  ❌ {mid} → {err_msg}")
