# Quick Reference Card - ML CI/CD Pipeline

## 🚀 Quick Start Commands

### 1. Initial Setup (One-time)
```bash
# Clone your repo
git clone https://github.com/YOUR-USERNAME/ml-cicd-pipeline.git
cd ml-cicd-pipeline

# Make setup script executable
chmod +x setup.sh

# Run setup helper
./setup.sh
```

### 2. Deploy Infrastructure (One-time)
```bash
# Using AWS Console:
# CloudFormation → Create Stack → Upload cloudformation-template.yaml

# OR using AWS CLI:
aws cloudformation create-stack \
  --stack-name ml-cicd-pipeline \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --parameters \
    ParameterKey=GitHubRepo,ParameterValue=YOUR-USERNAME/ml-cicd-pipeline \
    ParameterKey=GitHubBranch,ParameterValue=main \
    ParameterKey=GitHubToken,ParameterValue=YOUR-GITHUB-TOKEN \
    ParameterKey=ModelName,ParameterValue=iris-classifier \
  --capabilities CAPABILITY_IAM
```

### 3. Test Endpoint
```bash
# Install dependencies
pip install boto3

# Test the deployed model
python src/test_endpoint.py

# Or specify endpoint name
python src/test_endpoint.py iris-classifier-endpoint
```

### 4. Make Changes & Deploy
```bash
# Edit your code
vim src/train.py

# Commit and push (triggers pipeline automatically)
git add .
git commit -m "Update model"
git push origin main

# Pipeline will automatically run!
```

## 📊 Pipeline Stages

| Stage | Duration | What Happens |
|-------|----------|--------------|
| Source | 1-2 min | Pulls code from GitHub |
| Build | 5-10 min | Builds Docker image, pushes to ECR |
| Train | 10-15 min | Trains model on SageMaker |
| Deploy | 10-15 min | Deploys model to endpoint |
| **Total** | **25-40 min** | **Complete CI/CD cycle** |

## 🔍 Check Pipeline Status

```bash
# Get pipeline status
aws codepipeline get-pipeline-state --name ml-cicd-pipeline-pipeline

# Get latest execution
aws codepipeline list-pipeline-executions --pipeline-name ml-cicd-pipeline-pipeline

# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name iris-classifier-endpoint
```

## 📝 View Logs

```bash
# CodeBuild logs
aws logs tail /aws/codebuild/ml-cicd-pipeline-build --follow

# Training Lambda logs
aws logs tail /aws/lambda/ml-cicd-pipeline-training --follow

# Deploy Lambda logs
aws logs tail /aws/lambda/ml-cicd-pipeline-deploy --follow

# SageMaker training logs
# (Get training job name from Lambda logs first)
aws logs tail /aws/sagemaker/TrainingJobs --follow
```

## 🧪 Test Endpoint with curl

```bash
# Get endpoint URL
ENDPOINT_NAME="iris-classifier-endpoint"

# Prepare test data
cat > test_data.json << EOF
{
  "instances": [
    [5.1, 3.5, 1.4, 0.2],
    [6.2, 2.9, 4.3, 1.3],
    [7.3, 2.9, 6.3, 1.8]
  ]
}
EOF

# Invoke endpoint (requires AWS CLI with SageMaker access)
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name $ENDPOINT_NAME \
  --content-type application/json \
  --body fileb://test_data.json \
  output.json

# View results
cat output.json
```

## 🎯 Common Tasks

### Update Model Hyperparameters
Edit `infrastructure/cloudformation-template.yaml`:
```yaml
HyperParameters={
  'n-estimators': '200',  # Change this
  'max-depth': '10'       # Or this
}
```
Then update stack:
```bash
aws cloudformation update-stack \
  --stack-name ml-cicd-pipeline \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --capabilities CAPABILITY_IAM
```

### Manual Pipeline Trigger
```bash
aws codepipeline start-pipeline-execution \
  --name ml-cicd-pipeline-pipeline
```

### Delete Endpoint (to save costs)
```bash
aws sagemaker delete-endpoint --endpoint-name iris-classifier-endpoint
```

### Check Costs
```bash
# View current month costs (requires AWS Cost Explorer)
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=SERVICE
```

## 🧹 Complete Cleanup

```bash
# Delete CloudFormation stack (this deletes everything)
aws cloudformation delete-stack --stack-name ml-cicd-pipeline

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name ml-cicd-pipeline

# Manually delete S3 buckets if needed
aws s3 rb s3://ml-cicd-pipeline-artifacts-ACCOUNT-ID --force
aws s3 rb s3://ml-cicd-pipeline-models-ACCOUNT-ID --force
```

## 🐛 Troubleshooting Quick Fixes

### Build fails with "Cannot connect to Docker daemon"
```bash
# Start Docker
sudo systemctl start docker

# Or on Mac
open -a Docker
```

### "Access Denied" errors
```bash
# Check AWS credentials
aws sts get-caller-identity

# Configure if needed
aws configure
```

### Pipeline stuck in progress
```bash
# Check specific stage
aws codepipeline get-pipeline-execution \
  --pipeline-name ml-cicd-pipeline-pipeline \
  --pipeline-execution-id EXECUTION-ID
```

### Endpoint not responding
```bash
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name iris-classifier-endpoint

# Check endpoint logs
aws logs tail /aws/sagemaker/Endpoints/iris-classifier-endpoint --follow
```

## 📚 Important URLs

- **CloudFormation Console**: https://console.aws.amazon.com/cloudformation
- **CodePipeline Console**: https://console.aws.amazon.com/codepipeline
- **SageMaker Console**: https://console.aws.amazon.com/sagemaker
- **CloudWatch Logs**: https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups
- **ECR Console**: https://console.aws.amazon.com/ecr

## 💰 Cost Monitoring

| Service | Cost | Frequency |
|---------|------|-----------|
| SageMaker Training | ~$0.10 | Per run |
| SageMaker Endpoint | ~$0.05/hr | While running |
| CodeBuild | ~$0.01 | Per build |
| S3 | <$0.01 | Monthly |
| Lambda | Free tier | - |

**💡 Tip**: Delete the endpoint when not in use to avoid hourly charges!

```bash
# Delete endpoint to stop charges
aws sagemaker delete-endpoint --endpoint-name iris-classifier-endpoint
```

## ✅ Health Check

```bash
# Quick health check script
echo "Checking pipeline health..."
aws codepipeline get-pipeline-state --name ml-cicd-pipeline-pipeline | grep -A 2 "latestExecution"
aws sagemaker describe-endpoint --endpoint-name iris-classifier-endpoint | grep "EndpointStatus"
```

## 🎓 Learn More

- **AWS SageMaker**: https://docs.aws.amazon.com/sagemaker/
- **AWS CodePipeline**: https://docs.aws.amazon.com/codepipeline/
- **Scikit-learn**: https://scikit-learn.org/
- **Docker**: https://docs.docker.com/
