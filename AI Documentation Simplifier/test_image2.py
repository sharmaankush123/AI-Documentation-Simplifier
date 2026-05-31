"""Quick test for Nova Canvas image generation"""
import json
import base64
import boto3

# Try eu-west-1 first, then us-east-1
regions_to_try = ["eu-west-1", "us-east-1"]

for region in regions_to_try:
    print(f"\n--- Testing in {region} ---")
    bedrock = boto3.client("bedrock-runtime", region_name=region)
    
    # Nova Canvas request format
    body = json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": "A simple blue circle on white background"
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 512,
            "width": 512,
            "quality": "standard"
        }
    })
    
    try:
        response = bedrock.invoke_model(
            modelId="amazon.nova-canvas-v1:0",
            contentType="application/json",
            accept="application/json",
            body=body
        )
        result = json.loads(response["body"].read())
        img_data = base64.b64decode(result["images"][0])
        
        # Save test image
        with open(f"test_image_{region}.png", "wb") as f:
            f.write(img_data)
        
        print(f"  ✅ Nova Canvas works in {region}! Image saved as test_image_{region}.png")
        print(f"     Image size: {len(img_data)} bytes")
        break  # Stop on first success
        
    except Exception as e:
        err = str(e)[:150]
        print(f"  ❌ {err}")

print("\nDone!")
