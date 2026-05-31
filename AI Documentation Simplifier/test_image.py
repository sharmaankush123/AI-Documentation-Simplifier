"""Quick test to find which image model works in eu-west-1"""
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="eu-west-1")

models_to_try = [
    "amazon.titan-image-generator-v2:0",
    "amazon.titan-image-generator-v2",  
    "amazon.nova-canvas-v1:0",
    "stability.stable-diffusion-xl-v1",
    "stability.sd3-5-large-v1:0",
]

for model_id in models_to_try:
    try:
        if "titan" in model_id:
            body = json.dumps({
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {"text": "A simple blue circle"},
                "imageGenerationConfig": {"numberOfImages": 1, "height": 512, "width": 512}
            })
        elif "nova" in model_id:
            body = json.dumps({
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {"text": "A simple blue circle"},
                "imageGenerationConfig": {"numberOfImages": 1, "height": 512, "width": 512}
            })
        else:
            body = json.dumps({
                "text_prompts": [{"text": "A simple blue circle"}],
                "cfg_scale": 7, "steps": 30, "height": 512, "width": 512
            })
        
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body
        )
        print(f"  ✅ {model_id} — WORKS!")
        break
    except Exception as e:
        err = str(e)[:100]
        print(f"  ❌ {model_id} — {err}")
