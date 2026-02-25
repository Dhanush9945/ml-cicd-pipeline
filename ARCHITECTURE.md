# ML CI/CD Pipeline Architecture

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ML CI/CD PIPELINE FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

    Developer                     AWS Cloud
        │
        │ git push
        ▼
┌──────────────┐
│   GitHub     │
│ Repository   │──────────┐
└──────────────┘          │
                          │ Webhook trigger
                          ▼
                 ┌──────────────────┐
                 │  CodePipeline    │
                 │   Orchestrator   │
                 └──────────────────┘
                          │
        ┌─────────────────┼─────────────────┬─────────────────┐
        │                 │                 │                 │
        ▼                 ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SOURCE     │  │    BUILD     │  │    TRAIN     │  │    DEPLOY    │
│              │  │              │  │              │  │              │
│  Pull from   │  │  CodeBuild   │  │   Lambda     │  │   Lambda     │
│   GitHub     │  │              │  │   triggers   │  │   creates    │
│              │  │  • Docker    │  │   SageMaker  │  │   endpoint   │
│              │  │    build     │  │   Training   │  │              │
│              │  │  • Push ECR  │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
                          │                 │                 │
                          ▼                 ▼                 ▼
                  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
                  │     ECR      │  │  SageMaker   │  │  SageMaker   │
                  │  Container   │  │   Training   │  │   Endpoint   │
                  │  Registry    │  │     Job      │  │              │
                  └──────────────┘  └──────────────┘  └──────────────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │   S3 Bucket  │
                                    │    Model     │
                                    │   Artifacts  │
                                    └──────────────┘
```

## Component Details

### 1. Source Stage (GitHub)
**Purpose**: Version control and trigger
**Components**:
- GitHub repository with your code
- Webhook integration to trigger pipeline

**What happens**:
1. Developer pushes code to GitHub
2. GitHub webhook notifies CodePipeline
3. CodePipeline pulls latest code

### 2. Build Stage (CodeBuild)
**Purpose**: Build and containerize the model
**Components**:
- CodeBuild project
- Docker
- ECR (Elastic Container Registry)

**What happens**:
1. CodeBuild runs buildspec.yml
2. Builds Docker image with training code
3. Pushes image to ECR
4. Passes image URI to next stage

**Files involved**:
- buildspec.yml
- Dockerfile
- requirements.txt
- src/train.py
- src/inference.py

### 3. Train Stage (Lambda + SageMaker)
**Purpose**: Train the ML model
**Components**:
- Lambda function (orchestrator)
- SageMaker Training Job
- S3 bucket for model artifacts

**What happens**:
1. Lambda receives image URI from Build stage
2. Lambda creates SageMaker training job
3. SageMaker pulls Docker image from ECR
4. Trains model using train.py
5. Saves model artifacts to S3
6. Lambda waits for completion
7. Passes model S3 path to Deploy stage

**Model Quality Gate**:
- Training fails if accuracy < 0.85
- This prevents bad models from deploying

### 4. Deploy Stage (Lambda + SageMaker)
**Purpose**: Deploy model to production endpoint
**Components**:
- Lambda function (orchestrator)
- SageMaker Model
- SageMaker Endpoint Config
- SageMaker Endpoint

**What happens**:
1. Lambda receives model S3 path from Train stage
2. Creates SageMaker Model from artifacts
3. Creates Endpoint Configuration
4. Creates/Updates Endpoint
5. Waits for endpoint to be InService
6. Endpoint ready for predictions!

### 5. Storage Components

**S3 Buckets**:
- `ml-cicd-pipeline-artifacts`: Pipeline artifacts
- `ml-cicd-pipeline-models`: Trained model artifacts

**ECR Repository**:
- `ml-model-repo`: Docker images for training/inference

### 6. IAM Roles

**CodeBuild Role**:
- Access to S3 for artifacts
- Push to ECR
- CloudWatch Logs

**SageMaker Role**:
- Access to S3 for data and models
- Pull from ECR
- CloudWatch Logs

**Lambda Role**:
- Create/manage SageMaker resources
- Read/write S3
- Pass SageMaker role
- CodePipeline job callbacks

**CodePipeline Role**:
- Access S3 artifacts
- Trigger CodeBuild
- Invoke Lambda functions

## Data Flow

```
1. Code Changes
   ↓
2. GitHub (source code)
   ↓
3. CodePipeline (orchestration)
   ↓
4. CodeBuild (containerization)
   ↓
5. ECR (Docker image storage)
   ↓
6. SageMaker Training (model training)
   ↓
7. S3 (model artifacts)
   ↓
8. SageMaker Endpoint (model serving)
   ↓
9. Production (ready for predictions!)
```

## Request Flow (Inference)

```
User/Application
      │
      │ HTTP POST
      │ JSON payload
      ▼
SageMaker Endpoint
      │
      │ Calls inference.py
      │
      ├─► model_fn() ──► Load model from S3
      │
      ├─► input_fn() ──► Parse JSON input
      │
      ├─► predict_fn() ──► Make predictions
      │
      └─► output_fn() ──► Format JSON response
      │
      ▼
Return predictions to user
```

## Monitoring & Logging

```
CloudWatch Logs
    ├── /aws/codebuild/ml-cicd-pipeline-build
    │   └── Build process logs
    │
    ├── /aws/lambda/ml-cicd-pipeline-training
    │   └── Training orchestration logs
    │
    ├── /aws/lambda/ml-cicd-pipeline-deploy
    │   └── Deployment orchestration logs
    │
    ├── /aws/sagemaker/TrainingJobs
    │   └── Model training logs
    │
    └── /aws/sagemaker/Endpoints/iris-classifier-endpoint
        └── Endpoint inference logs

CloudWatch Metrics
    ├── SageMaker Endpoint Metrics
    │   ├── Invocations
    │   ├── ModelLatency
    │   └── Invocation4XXErrors
    │
    └── Lambda Metrics
        ├── Duration
        ├── Errors
        └── Invocations
```

## Security Features

1. **IAM Least Privilege**: Each component has minimal permissions
2. **Encrypted Storage**: S3 buckets use encryption at rest
3. **Private Networking**: SageMaker can use VPC
4. **Secrets Management**: GitHub token stored in CloudFormation parameters
5. **Image Scanning**: ECR scans Docker images for vulnerabilities

## Scalability

- **Horizontal**: Add more endpoint instances
- **Vertical**: Use larger instance types
- **Auto-scaling**: Can add auto-scaling policies to endpoints
- **Multi-region**: Deploy stack in multiple regions

## High Availability

- **Multi-AZ**: SageMaker endpoints run across multiple AZs
- **Versioning**: S3 versioning keeps model history
- **Blue/Green**: Can implement blue/green deployments
- **Rollback**: CloudFormation enables easy rollbacks

## Cost Optimization Tips

1. **Use spot instances** for training (can save 70%)
2. **Delete endpoints** when not in use
3. **Use smaller instances** for development
4. **Implement auto-scaling** for production
5. **Clean up old models** in S3
6. **Use S3 lifecycle policies** to move old artifacts to cheaper storage

## Extending the Pipeline

### Add Stages:
- **Testing Stage**: Automated model testing before deploy
- **Approval Stage**: Manual approval before production
- **Monitoring Stage**: Model drift detection
- **A/B Testing Stage**: Deploy multiple model versions

### Add Features:
- **SageMaker Pipelines**: For more complex ML workflows
- **Model Registry**: Version and track models
- **Feature Store**: Manage ML features
- **Data Quality**: Validate input data
- **Model Explainability**: Add SHAP/LIME explanations

### Integration Options:
- **API Gateway**: REST API for model
- **Lambda**: Serverless inference
- **Batch Transform**: Batch predictions
- **Edge Deployment**: Deploy to edge devices
