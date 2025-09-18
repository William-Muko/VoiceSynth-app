#!/usr/bin/env python3
"""
Infrastructure Deployment Script
Deploy CloudFormation stack for Voice Synthesis App
"""

import subprocess
import sys

def run_command(cmd):
    """Execute AWS CLI command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        print(result.stdout)
        return True
    except Exception as e:
        print(f"Command failed: {e}")
        return False

def main():
    """Deploy CloudFormation stack"""
    print("🏗️  Deploying Voice Synthesis App Infrastructure...")
    
    cmd = """aws cloudformation deploy \
        --template-file template.yaml \
        --stack-name voicesynth-stack \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameter-overrides ProjectName=voicesynth"""
    
    if run_command(cmd):
        print("✅ Infrastructure deployed successfully!")
    else:
        print("❌ Infrastructure deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()