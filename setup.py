#!/usr/bin/env python3
"""
Voice Synthesis App - Master Deployment Script
Cross-platform automation for complete application deployment
"""

import subprocess
import sys
import os
import json
import time

def run_command(cmd, cwd=None, shell=True):
    """Execute command and return result"""
    try:
        result = subprocess.run(cmd, shell=shell, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Command failed: {e}")
        return None

def deploy_infrastructure():
    """Deploy CloudFormation stack"""
    print("Deploying infrastructure...")
    cmd = [
        "aws", "cloudformation", "deploy",
        "--template-file", "template.yaml",
        "--stack-name", "voicesynth-stack",
        "--capabilities", "CAPABILITY_NAMED_IAM",
        "--parameter-overrides", "ProjectName=voicesynth"
    ]
    result = run_command(cmd, cwd="infrastructure")
    return result is not None

def deploy_lambda():
    """Package and deploy Lambda function"""
    print("Deploying Lambda function...")
    
    # Create deployment directory
    os.makedirs("backend/deployment", exist_ok=True)
    
    # Copy Lambda function
    run_command("cp src/lambda_function.py deployment/", cwd="backend")
    
    # Install dependencies
    run_command("pip install -r requirements.txt -t deployment/", cwd="backend")
    
    # Create zip file
    if os.name == 'nt':  # Windows
        run_command("powershell Compress-Archive -Path deployment/* -DestinationPath lambda-deployment.zip -Force", cwd="backend")
    else:  # Linux/Mac
        run_command("cd deployment && zip -r ../lambda-deployment.zip .", cwd="backend")
    
    # Update Lambda function
    cmd = [
        "aws", "lambda", "update-function-code",
        "--function-name", "voicesynth-synthesize",
        "--zip-file", "fileb://lambda-deployment.zip"
    ]
    result = run_command(cmd, cwd="backend")
    return result is not None

def deploy_frontend():
    """Deploy frontend to S3 and invalidate CloudFront"""
    print("Deploying frontend...")
    
    # Get stack outputs
    cmd = [
        "aws", "cloudformation", "describe-stacks",
        "--stack-name", "voicesynth-stack",
        "--query", "Stacks[0].Outputs"
    ]
    outputs = run_command(cmd)
    if not outputs:
        return False
    
    outputs_data = json.loads(outputs)
    bucket_name = None
    api_endpoint = None
    
    for output in outputs_data:
        if output['OutputKey'] == 'WebsiteBucket':
            bucket_name = output['OutputValue']
        elif output['OutputKey'] == 'ApiEndpoint':
            api_endpoint = output['OutputValue']
    
    if not bucket_name or not api_endpoint:
        print("Error: Could not get stack outputs")
        return False
    
    # Update API endpoint in app.js
    with open("frontend/app.js", "r") as f:
        content = f.read()
    
    content = content.replace(
        "https://your-api-gateway-url.amazonaws.com/prod/synthesize",
        api_endpoint
    )
    
    with open("frontend/app.js", "w") as f:
        f.write(content)
    
    # Upload to S3
    cmd = ["aws", "s3", "sync", ".", f"s3://{bucket_name}", "--delete", "--exclude", "*.py"]
    if not run_command(cmd, cwd="frontend"):
        return False
    
    # Get CloudFront distribution ID
    cmd = [
        "aws", "cloudfront", "list-distributions",
        "--query", f"DistributionList.Items[?Origins.Items[0].DomainName=='{bucket_name}.s3.us-east-1.amazonaws.com'].Id",
        "--output", "text"
    ]
    distribution_id = run_command(cmd)
    
    if distribution_id:
        print("Invalidating CloudFront cache...")
        cmd = ["aws", "cloudfront", "create-invalidation", "--distribution-id", distribution_id, "--paths", "/*"]
        run_command(cmd)
    
    return True

def main():
    """Main deployment orchestrator"""
    print("Voice Synthesis App - Automated Deployment")
    print("=" * 50)
    
    # Check prerequisites
    if not run_command("aws --version"):
        print("ERROR: AWS CLI not found. Please install and configure AWS CLI.")
        sys.exit(1)
    
    if not run_command("python --version"):
        print("ERROR: Python not found. Please install Python 3.9+.")
        sys.exit(1)
    
    # Deploy components
    steps = [
        ("Infrastructure", deploy_infrastructure),
        ("Lambda Function", deploy_lambda),
        ("Frontend", deploy_frontend)
    ]
    
    for step_name, step_func in steps:
        print(f"\n[DEPLOY] {step_name}...")
        if not step_func():
            print(f"ERROR: {step_name} deployment failed!")
            sys.exit(1)
        print(f"SUCCESS: {step_name} deployed successfully!")
    
    print("\nDeployment completed successfully!")
    print("Your app will be available at: https://d1fbfr7wbs38k8.cloudfront.net")
    print("CloudFront propagation may take 5-15 minutes")

if __name__ == "__main__":
    main()