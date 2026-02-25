# Complete ML CI/CD Pipeline Setup Guide

## Prerequisites

Before starting, ensure you have:
- AWS Account with admin access
- GitHub account
- AWS CLI installed and configured
- Git installed
- Python 3.9+ installed

## Step 1: Prepare GitHub Repository

1. **Create a new GitHub repository**
   ```bash
   # On GitHub.com, create a new repository named: ml-cicd-pipeline
   # Make it public or private (your choice)
   ```

2. **Create a GitHub Personal Access Token**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Click "Generate new token (classic)"
   - Give it a name: "AWS CodePipeline"
   - Select scopes: `repo` (all checkboxes under repo)
   - Click "Generate token"
   - **IMPORTANT: Copy and save this token - you'll need it later!**

3. **Clone and push the code to your repository**
   ```bash
   # Clone your empty repository
   git clone https://github.com/YOUR-USERNAME/ml-cicd-pipeline.git
   cd ml-cicd-pipeline
   
   # Copy all the project files here (see file structure below)
   # Then push to GitHub:
   git add .
   git commit -m "Initial commit - ML CI/CD pipeline"
   git push origin main
   ```

## Step 2: Deploy AWS Infrastructure

1. **Open AWS Console and navigate to CloudFormation**
   - Region: Choose your preferred region (e.g., us-east-1)
   - Click "Create stack" → "With new resources (standard)"

2. **Upload the CloudFormation template**
   - Choose "Upload a template file"
   - Upload: `infrastructure/cloudformation-template.yaml`
   - Click "Next"

3. **Configure stack parameters**
   - Stack name: `ml-cicd-pipeline`
   - GitHubRepo: `YOUR-GITHUB-USERNAME/ml-cicd-pipeline`
   - GitHubBranch: `main`
   - GitHubToken: `paste your GitHub token here`
   - ModelName: `iris-classifier`
   - Click "Next"

4. **Configure stack options**
   - Tags (optional): Add any tags you want
   - Click "Next"

5. **Review and create**
   - Check "I acknowledge that AWS CloudFormation might create IAM resources"
   - Click "Create stack"
   - **Wait 10-15 minutes** for stack creation to complete

## Step 3: Verify Infrastructure

1. **Check CloudFormation stack status**
   - Status should show: `CREATE_COMPLETE`
   - Go to "Outputs" tab and note:
     - ECRRepositoryURI
     - ModelBucket
     - EndpointName
     - PipelineName

2. **Verify created resources**
   - **CodePipeline**: AWS Console → CodePipeline → Should see `ml-cicd-pipeline-pipeline`
   - **CodeBuild**: AWS Console → CodeBuild → Should see `ml-cicd-pipeline-build`
   - **ECR**: AWS Console → ECR → Should see `ml-model-repo`
   - **S3**: Should see two buckets (artifacts and models)
   - **Lambda**: Should see two functions (training and deploy)

## Step 4: Trigger the Pipeline

The pipeline will automatically trigger when you push code to GitHub, but let's trigger it manually first:

1. **Go to AWS CodePipeline console**
   - Click on your pipeline: `ml-cicd-pipeline-pipeline`
   - Click "Release change" button

2. **Watch the pipeline execute**
   The pipeline has 4 stages:
   
   **Stage 1: Source** (1-2 minutes)
   - Pulls code from GitHub
   
   **Stage 2: Build** (5-10 minutes)
   - Builds Docker image
   - Pushes to ECR
   - Status: Check CodeBuild logs for details
   
   **Stage 3: Train** (10-15 minutes)
   - Starts SageMaker training job
   - Trains the model
   - Status: Check Lambda logs or SageMaker console
   
   **Stage 4: Deploy** (10-15 minutes)
   - Creates/updates SageMaker endpoint
   - Status: Check SageMaker endpoints

3. **Total time: 25-40 minutes for first run**

## Step 5: Test the Deployed Model

1. **Wait for endpoint to be "InService"**
   - Go to AWS Console → SageMaker → Endpoints
   - Find: `iris-classifier-endpoint`
   - Status should be: `InService`

2. **Test using the test script**
   ```bash
   # Install boto3 if not already installed
   pip install boto3
   
   # Run the test script
   python src/test_endpoint.py
   ```

3. **Expected output**
   ```
   Testing endpoint: iris-classifier-endpoint
   Input data: {'instances': [[5.1, 3.5, 1.4, 0.2], ...]}
   
   ✓ Endpoint is working!
   
   Predictions: [0, 1, 2]
   
   Probabilities:
     Sample 1: ['0.9800', '0.0100', '0.0100']
     Sample 2: ['0.0100', '0.9200', '0.0700']
     Sample 3: ['0.0100', '0.0300', '0.9600']
   ```

## Step 6: Make Changes and Trigger CI/CD

1. **Modify the model (example)**
   ```bash
   # Edit src/train.py - change n_estimators
   # Line ~46, change: n_estimators=args.n_estimators
   # To a higher value or modify other parameters
   ```

2. **Commit and push changes**
   ```bash
   git add .
   git commit -m "Update model hyperparameters"
   git push origin main
   ```

3. **Watch automatic pipeline execution**
   - Go to CodePipeline console
   - Your pipeline should automatically start
   - Wait for all stages to complete
   - Test endpoint again to see the updated model

## Monitoring and Logs

### CodeBuild Logs
- AWS Console → CodeBuild → Build projects → ml-cicd-pipeline-build
- Click on any build run to see logs

### Lambda Logs
- AWS Console → CloudWatch → Log groups
- `/aws/lambda/ml-cicd-pipeline-training` - Training logs
- `/aws/lambda/ml-cicd-pipeline-deploy` - Deployment logs

### SageMaker Logs
- AWS Console → SageMaker → Training jobs - See training logs
- AWS Console → SageMaker → Endpoints - See endpoint status

### Pipeline Execution History
- AWS Console → CodePipeline → Your pipeline
- Click on any execution to see details and logs

## Cleanup (To avoid charges)

When you're done experimenting:

1. **Delete the CloudFormation stack**
   ```bash
   aws cloudformation delete-stack --stack-name ml-cicd-pipeline
   ```

2. **Manually delete (if needed)**
   - SageMaker endpoints (if still running)
   - S3 buckets (empty them first, then delete)
   - ECR images

## Costs Estimation

Running this pipeline will incur AWS charges:
- **SageMaker training**: ~$0.10 per training job (ml.m5.large for ~5 mins)
- **SageMaker endpoint**: ~$0.05/hour (ml.t2.medium)
- **S3 storage**: <$0.01 for small models
- **CodeBuild**: ~$0.01 per build (5-10 mins)
- **Lambda**: Minimal (free tier covers this)

**Estimated total**: $1-2 per full pipeline run

**Important**: DELETE the endpoint when not in use to avoid hourly charges!

## Troubleshooting

### Pipeline fails at Build stage
- Check CodeBuild logs
- Ensure Docker can build successfully
- Verify IAM roles have ECR permissions

### Pipeline fails at Train stage
- Check Lambda training logs in CloudWatch
- Check SageMaker training job logs
- Verify model code doesn't have errors
- Check if model meets accuracy threshold (0.85)

### Pipeline fails at Deploy stage
- Check Lambda deploy logs
- Verify SageMaker role has correct permissions
- Check if endpoint already exists and is updating

### Endpoint returns errors
- Check SageMaker endpoint logs
- Verify inference.py has correct input/output handling
- Test with correctly formatted JSON

### GitHub connection issues
- Verify GitHub token is valid
- Check token has `repo` scope
- Ensure repository name is correct

## Next Steps

Now that you have a working CI/CD pipeline:

1. **Add real data**: Replace iris dataset with your own data
2. **Improve model**: Try different algorithms, add feature engineering
3. **Add tests**: Add unit tests in buildspec.yml
4. **Add manual approval**: Add approval stage before production deployment
5. **Add monitoring**: Set up CloudWatch alarms for endpoint metrics
6. **Add A/B testing**: Deploy multiple model versions
7. **Add model registry**: Use SageMaker Model Registry for versioning

## File Structure

Your repository should have this structure:

```
ml-cicd-pipeline/
├── src/
│   ├── train.py              # Model training script
│   ├── inference.py          # Inference/prediction script
│   └── test_endpoint.py      # Endpoint testing script
├── infrastructure/
│   └── cloudformation-template.yaml  # Infrastructure as Code
├── Dockerfile                # Docker container definition
├── buildspec.yml            # CodeBuild instructions
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Support

If you encounter issues:
1. Check CloudWatch logs for detailed error messages
2. Review AWS documentation for SageMaker, CodePipeline, CodeBuild
3. Ensure all IAM roles have necessary permissions
4. Verify your AWS account has sufficient limits/quotas

## Success Checklist

✓ CloudFormation stack created successfully
✓ Pipeline visible in CodePipeline console
✓ First pipeline run completed successfully
✓ SageMaker endpoint is InService
✓ Test script returns predictions
✓ Can trigger pipeline by pushing code to GitHub

Congratulations! You now have a fully automated ML CI/CD pipeline! 🎉
