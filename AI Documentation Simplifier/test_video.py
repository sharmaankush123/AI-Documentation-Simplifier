"""Test Nova Reel video model availability"""
import boto3
import json

# Check which Nova Reel model ID works
regions = ["us-east-1", "us-west-2"]

for region in regions:
    print(f"\n--- {region} ---")
    bedrock_mgmt = boto3.client("bedrock", region_name=region)
    
    # List all Nova models
    models = bedrock_mgmt.list_foundation_models(byProvider="amazon")
    nova_reel_models = [m for m in models["modelSummaries"] if "reel" in m["modelId"].lower()]
    
    print(f"  Nova Reel models found:")
    for m in nova_reel_models:
        status = m.get('modelLifecycle', {}).get('status', 'ACTIVE')
        print(f"    {m['modelId']} [{status}]")
    
    # Also check inference profiles for Nova Reel
    bedrock_profiles = boto3.client("bedrock", region_name=region)
    profiles = bedrock_profiles.list_inference_profiles()
    reel_profiles = [p for p in profiles["inferenceProfileSummaries"] 
                     if "reel" in p.get("inferenceProfileName", "").lower() 
                     or "reel" in p.get("inferenceProfileId", "").lower()]
    
    if reel_profiles:
        print(f"  Nova Reel inference profiles:")
        for p in reel_profiles:
            print(f"    {p['inferenceProfileId']} — {p['inferenceProfileName']}")
    else:
        print(f"  No Nova Reel inference profiles found")

    # Try different model IDs
    print(f"\n  Testing StartAsyncInvoke...")
    bedrock_rt = boto3.client("bedrock-runtime", region_name=region)
    
    model_ids_to_try = [
        "amazon.nova-reel-v1:1",
        "amazon.nova-reel-v1:0",
        "us.amazon.nova-reel-v1:0",
    ]
    
    for mid in model_ids_to_try:
        try:
            response = bedrock_rt.start_async_invoke(
                modelId=mid,
                modelInput={
                    "taskType": "TEXT_VIDEO",
                    "textToVideoParams": {"text": "A blue circle spinning slowly"},
                    "videoGenerationConfig": {"durationSeconds": 6, "fps": 24, "dimension": "1280x720"}
                },
                outputDataConfig={
                    "s3OutputDataConfig": {"s3Uri": "s3://singholr-feature-explainer/test"}
                }
            )
            print(f"    ✅ {mid} — WORKS! ARN: {response['invocationArn'][:60]}...")
            break
        except Exception as e:
            err = str(e)[:100]
            print(f"    ❌ {mid} — {err}")
