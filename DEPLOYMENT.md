# CI/CD Deployment Guide

## Automated Deployment with GitHub Actions

This project includes automated CI/CD pipelines for seamless deployment to AWS.

## Setup Instructions

### 1. **GitHub Repository Setup**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/voicesynth-app.git
git push -u origin main
```

### 2. **AWS Credentials Configuration**
Add these secrets to your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

### 3. **Required AWS Permissions**
Your AWS user needs these permissions:
- CloudFormation (full access)
- Lambda (full access)
- S3 (full access)
- API Gateway (full access)
- IAM (create/update roles)

## CI/CD Workflows

### **Test Workflow** (`test.yml`)
Runs on every push and PR:
- ✅ Validates HTML syntax
- ✅ Checks JavaScript syntax
- ✅ Validates Python code
- ✅ Validates CloudFormation template

### **Deploy Workflow** (`deploy.yml`)
Runs on push to `main` branch:
1. Deploys infrastructure (CloudFormation)
2. Packages Lambda function
3. Updates Lambda code
4. Deploys frontend to S3
5. Outputs website URL

## Deployment Process

### **Automatic Deployment:**
1. Push code to `main` branch
2. GitHub Actions automatically:
   - Tests all components
   - Deploys infrastructure
   - Updates Lambda function
   - Deploys frontend
   - Provides website URL

### **Manual Deployment:**
```bash
# Cross-platform Python automation
python setup.py

# Or individual components
python infrastructure/deploy.py
python backend/deploy.py
python frontend/deploy.py

# Traditional AWS CLI (if needed)
cd infrastructure
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name voicesynth-stack \
  --capabilities CAPABILITY_NAMED_IAM
```

## Configuration

### **Environment Variables:**
- `AWS_REGION`: us-east-1 (default)
- `STACK_NAME`: voicesynth-stack

### **Customization:**
- Modify `.github/workflows/deploy.yml` for different regions
- Update stack name in workflow files
- Add environment-specific deployments

## Monitoring

### **GitHub Actions:**
- View deployment status in Actions tab
- Check logs for troubleshooting
- Monitor build times and success rates

### **AWS CloudWatch:**
- Lambda function logs
- API Gateway metrics
- S3 access logs

## Troubleshooting

### **Common Issues:**
1. **AWS Permissions**: Ensure proper IAM permissions
2. **Stack Name Conflicts**: Use unique stack names
3. **Region Mismatch**: Verify AWS region consistency
4. **API Endpoint**: Check CloudFormation outputs

### **Rollback:**
```bash
aws cloudformation delete-stack --stack-name voicesynth-stack
```

## Benefits

- ✅ **Zero-downtime deployments**
- ✅ **Automated testing**
- ✅ **Infrastructure as Code**
- ✅ **Version control integration**
- ✅ **Rollback capabilities**
- ✅ **Cost optimization**