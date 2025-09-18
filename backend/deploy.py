#!/usr/bin/env python3
"""
Lambda Function Deployment Script
Package and deploy Lambda function for Voice Synthesis App
"""

import subprocess
import os
import sys
import shutil

def run_command(cmd, cwd=None):
    """Execute command"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Command failed: {e}")
        return False

def main():
    """Package and deploy Lambda function"""
    print("⚡ Packaging Lambda function...")
    
    # Clean and create deployment directory
    if os.path.exists("deployment"):
        shutil.rmtree("deployment")
    os.makedirs("deployment")
    
    # Copy Lambda function
    shutil.copy("src/lambda_function.py", "deployment/")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if not run_command("pip install -r requirements.txt -t deployment/"):
        print("❌ Failed to install dependencies!")
        sys.exit(1)
    
    # Create deployment package
    print("📦 Creating deployment package...")
    if os.name == 'nt':  # Windows
        cmd = "powershell Compress-Archive -Path deployment/* -DestinationPath lambda-deployment.zip -Force"
    else:  # Linux/Mac
        cmd = "cd deployment && zip -r ../lambda-deployment.zip ."
    
    if not run_command(cmd):
        print("❌ Failed to create deployment package!")
        sys.exit(1)
    
    # Deploy to AWS Lambda
    print("🚀 Deploying to AWS Lambda...")
    cmd = """aws lambda update-function-code \
        --function-name voicesynth-synthesize \
        --zip-file fileb://lambda-deployment.zip"""
    
    if run_command(cmd):
        print("✅ Lambda function deployed successfully!")
    else:
        print("❌ Lambda deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()