"""Test Stability AI image generation models"""
import json
import base64
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# Also check if there's a text-to-image specific model
bedrock_mgmt = boto3.client("bedrock", region_name="us-east-1")

# List ALL models (not just image output) to find text-to-image
print("Searching for Stability text-to-image models...")
all_models = bedrock_mgmt.list_foundation_models(byProvider="stability")
for m in all_models["modelSummaries"]:
    status = m.get('modelLifecycle', {}).get('status', 'ACTIVE')
    print(f"  {m['modelId']:50} | {status:8} | in: {m.get('inputModalities',[])} → out: {m.get('outputModalities',[])}")

# Try Stability models that might support text-to-image generation
print("\n\nTrying Stability text-to-image generation...")
models_to_try = [
    "stability.stable-image-core-v1:0",
    "stability.sd3-5-large-v1:0", 
    "stability.sd3-large-v1:0",
    "stability.stable-image-ultra-v1:0",
    "stability.stable-image-control-sketch-v1:0",
    "stability.stable-image-style-guide-v1:0",
]

for model_id in models_to_try:
    try:
        # Stability AI uses a different request format
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": "A simple blue circle on white background, flat design, minimal",
                "mode": "text-to-image",
                "output_format": "png"
            })
        )
        result = json.loads(response["body"].read())
        print(f"  ✅ {model_id} — WORKS!")
        print(f"     Response keys: {list(result.keys())}")
        
        # Try to save the image
        if "images" in result:
            img_data = base64.b64decode(result["images"][0])
            with open("test_stability.png", "wb") as f:
                f.write(img_data)
            print(f"     Saved test_stability.png ({len(img_data)} bytes)")
        break
    except Exception as e:
        err = str(e)[:120]
        print(f"  ❌ {model_id} — {err}")
