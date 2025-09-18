#!/usr/bin/env python3
"""
Frontend Deployment Script
Deploy frontend to S3 and invalidate CloudFront cache
"""

import subprocess
import json
import sys
import re

def run_command(cmd):
    """Execute AWS CLI command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Command failed: {e}")
        return None

def main():
    """Deploy frontend to S3 and CloudFront"""
    print("🌐 Deploying frontend...")
    
    # Get CloudFormation stack outputs
    cmd = """aws cloudformation describe-stacks \
        --stack-name voicesynth-stack \
        --query "Stacks[0].Outputs" \
        --output json"""
    
    outputs = run_command(cmd)
    if not outputs:
        print("❌ Failed to get stack outputs!")
        sys.exit(1)
    
    outputs_data = json.loads(outputs)
    bucket_name = None
    api_endpoint = None
    
    for output in outputs_data:
        if output['OutputKey'] == 'WebsiteBucket':
            bucket_name = output['OutputValue']
        elif output['OutputKey'] == 'ApiEndpoint':
            api_endpoint = output['OutputValue']
    
    if not bucket_name or not api_endpoint:
        print("❌ Could not find required stack outputs!")
        sys.exit(1)
    
    print(f"📦 Bucket: {bucket_name}")
    print(f"🔗 API: {api_endpoint}")
    
    # Update API endpoint in app.js
    print("🔧 Updating API endpoint...")
    with open("app.js", "r") as f:
        content = f.read()
    
    # Replace placeholder with actual API endpoint
    updated_content = re.sub(
        r'https://your-api-gateway-url\.amazonaws\.com/prod/synthesize',
        api_endpoint,
        content
    )
    
    with open("app.js", "w") as f:
        f.write(updated_content)
    
    # Upload to S3
    print("📤 Uploading to S3...")
    cmd = f"aws s3 sync . s3://{bucket_name} --delete --exclude '*.py' --exclude '*.bat'"
    if not run_command(cmd):
        print("❌ S3 upload failed!")
        sys.exit(1)
    
    # Get CloudFront distribution ID
    print("🔍 Finding CloudFront distribution...")
    cmd = f"""aws cloudfront list-distributions \
        --query "DistributionList.Items[?Origins.Items[0].DomainName=='{bucket_name}.s3.us-east-1.amazonaws.com'].Id" \
        --output text"""
    
    distribution_id = run_command(cmd)
    
    if distribution_id and distribution_id != "None":
        print(f"🔄 Invalidating CloudFront cache: {distribution_id}")
        cmd = f"aws cloudfront create-invalidation --distribution-id {distribution_id} --paths '/*'"
        run_command(cmd)
        print("✅ CloudFront cache invalidated!")
    else:
        print("⚠️  CloudFront distribution not found - skipping cache invalidation")
    
    print("✅ Frontend deployed successfully!")
    print("🌐 Your app will be available at: https://d1fbfr7wbs38k8.cloudfront.net")

if __name__ == "__main__":
    main()