"""Test all possible image generation options"""
import json
import base64
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# List all foundation models that support image
print("Checking available image models in us-east-1...")
bedrock_mgmt = boto3.client("bedrock", region_name="us-east-1")
models = bedrock_mgmt.list_foundation_models(byOutputModality="IMAGE")
print("\nAvailable IMAGE output models:")
for m in models["modelSummaries"]:
    print(f"  {m['modelId']} — {m.get('modelName', 'N/A')} [{m.get('modelLifecycle', {}).get('status', 'active')}]")
