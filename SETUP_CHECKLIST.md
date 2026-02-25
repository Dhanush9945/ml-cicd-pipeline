# ✅ STEP-BY-STEP SETUP CHECKLIST

Follow this checklist in order. Check off each item as you complete it.

## PHASE 1: Prerequisites (10 minutes)

- [ ] AWS Account created with admin access
- [ ] AWS CLI installed (`aws --version` works)
- [ ] AWS CLI configured (`aws configure` completed)
- [ ] GitHub account created
- [ ] Git installed (`git --version` works)
- [ ] Python 3.9+ installed (`python3 --version` works)
- [ ] Docker installed (optional, for local testing)

## PHASE 2: GitHub Setup (5 minutes)

- [ ] Created new GitHub repository: `ml-cicd-pipeline`
- [ ] Repository is public or private (either works)
- [ ] Generated GitHub Personal Access Token:
  - Go to: Settings → Developer settings → Personal access tokens
  - Name: "AWS CodePipeline"
  - Scopes: ✓ All under "repo"
  - **Token saved somewhere safe**: ________________
- [ ] Repository URL noted: https://github.com/YOUR-USERNAME/ml-cicd-pipeline

## PHASE 3: Upload Code to GitHub (5 minutes)

```bash
# Run these commands:
cd /path/to/downloaded/ml-cicd-pipeline
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ml-cicd-pipeline.git
git push -u origin main
```

- [ ] All files pushed to GitHub
- [ ] Can see files at: https://github.com/YOUR-USERNAME/ml-cicd-pipeline
- [ ] Verified these files exist:
  - [ ] README.md
  - [ ] Dockerfile
  - [ ] buildspec.yml
  - [ ] requirements.txt
  - [ ] src/train.py
  - [ ] src/inference.py
  - [ ] infrastructure/cloudformation-template.yaml

## PHASE 4: Deploy AWS Infrastructure (15 minutes)

- [ ] Opened AWS Console
- [ ] Selected region: ________________ (e.g., us-east-1)
- [ ] Navigated to CloudFormation service
- [ ] Clicked "Create stack" → "With new resources"
- [ ] Selected "Upload a template file"
- [ ] Uploaded: `infrastructure/cloudformation-template.yaml`
- [ ] Clicked "Next"

### Stack Parameters:
- [ ] Stack name: `ml-cicd-pipeline`
- [ ] GitHubRepo: `YOUR-USERNAME/ml-cicd-pipeline`
- [ ] GitHubBranch: `main`
- [ ] GitHubToken: `paste your token here`
- [ ] ModelName: `iris-classifier`
- [ ] Clicked "Next"

### Stack Options:
- [ ] (Optional) Added tags
- [ ] Clicked "Next"

### Review:
- [ ] Checked: "I acknowledge that AWS CloudFormation might create IAM resources"
- [ ] Clicked "Create stack"
- [ ] Status: CREATE_IN_PROGRESS ⏳

**WAIT 10-15 minutes**

- [ ] Stack status changed to: CREATE_COMPLETE ✅
- [ ] No errors in Events tab

### Note the Outputs:
- [ ] PipelineName: ________________
- [ ] ECRRepositoryURI: ________________
- [ ] ModelBucket: ________________
- [ ] EndpointName: ________________

## PHASE 5: Verify Resources (5 minutes)

- [ ] **CodePipeline**: Console → CodePipeline → See: `ml-cicd-pipeline-pipeline`
- [ ] **CodeBuild**: Console → CodeBuild → See: `ml-cicd-pipeline-build`
- [ ] **ECR**: Console → ECR → See: `ml-model-repo`
- [ ] **S3**: Console → S3 → See two buckets:
  - [ ] `ml-cicd-pipeline-artifacts-...`
  - [ ] `ml-cicd-pipeline-models-...`
- [ ] **Lambda**: Console → Lambda → See two functions:
  - [ ] `ml-cicd-pipeline-training`
  - [ ] `ml-cicd-pipeline-deploy`

## PHASE 6: Run Pipeline (30-40 minutes)

- [ ] Opened CodePipeline console
- [ ] Found pipeline: `ml-cicd-pipeline-pipeline`
- [ ] Clicked "Release change" to trigger manually
  - (Or just wait - it auto-triggers from GitHub)

### Watch stages:

**Stage 1: Source** (1-2 min)
- [ ] Status: Succeeded ✅
- [ ] Time: ___:___

**Stage 2: Build** (5-10 min)
- [ ] Status: In Progress → Succeeded ✅
- [ ] Time: ___:___
- [ ] Can view logs: CodeBuild → Build projects → Click latest build

**Stage 3: Train** (10-15 min)
- [ ] Status: In Progress → Succeeded ✅
- [ ] Time: ___:___
- [ ] Can view logs: CloudWatch → `/aws/lambda/ml-cicd-pipeline-training`
- [ ] Can view training: SageMaker → Training jobs

**Stage 4: Deploy** (10-15 min)
- [ ] Status: In Progress → Succeeded ✅
- [ ] Time: ___:___
- [ ] Can view logs: CloudWatch → `/aws/lambda/ml-cicd-pipeline-deploy`

### Final Status:
- [ ] All stages: Succeeded ✅
- [ ] Total time: ___:___
- [ ] SageMaker endpoint status: InService ✅

## PHASE 7: Test the Model (5 minutes)

```bash
# Install boto3
pip install boto3

# Run test
python src/test_endpoint.py
```

- [ ] Test script ran without errors
- [ ] Received predictions: `[0, 1, 2]`
- [ ] Received probabilities for 3 samples
- [ ] Output looks like:
  ```
  ✓ Endpoint is working!
  Predictions: [0, 1, 2]
  ```

## PHASE 8: Test CI/CD (10 minutes)

### Make a code change:

```bash
# Edit src/train.py
# Find line ~26: n_estimators=args.n_estimators
# Change default from 100 to 150

git add src/train.py
git commit -m "Update n_estimators to 150"
git push origin main
```

- [ ] Code pushed to GitHub
- [ ] Pipeline automatically started (check CodePipeline console)
- [ ] Pipeline ran through all stages
- [ ] New model deployed
- [ ] Tested endpoint again - still works

## 🎉 SUCCESS CRITERIA

You've successfully completed the setup if:

- [ ] ✅ CloudFormation stack shows CREATE_COMPLETE
- [ ] ✅ Pipeline visible and ran successfully
- [ ] ✅ SageMaker endpoint shows InService
- [ ] ✅ Test script returns predictions
- [ ] ✅ Code changes trigger automatic pipeline runs
- [ ] ✅ New models deploy automatically

**Congratulations! Your ML CI/CD pipeline is working! 🎊**

## 📊 Next Steps

Now that it's working, you can:

- [ ] Read ARCHITECTURE.md to understand how it works
- [ ] Check QUICK_REFERENCE.md for common commands
- [ ] Try modifying the model (different algorithm, features)
- [ ] Add your own dataset
- [ ] Set up CloudWatch alarms
- [ ] Add manual approval stage before production
- [ ] Implement A/B testing

## 💰 Cost Management

**IMPORTANT**: To avoid unnecessary charges:

- [ ] Understand current costs:
  - Training: ~$0.10 per run
  - Endpoint: ~$0.05/hour (while running)
  - S3: <$0.01/month
  - Other: minimal

- [ ] Delete endpoint when not in use:
  ```bash
  aws sagemaker delete-endpoint --endpoint-name iris-classifier-endpoint
  ```

- [ ] Or delete entire stack:
  ```bash
  aws cloudformation delete-stack --stack-name ml-cicd-pipeline
  ```

## 🐛 Troubleshooting

If something failed, check:

- [ ] CloudFormation Events tab for errors
- [ ] CodePipeline stage details
- [ ] CloudWatch Logs for detailed error messages
- [ ] IAM roles have correct permissions
- [ ] GitHub token is valid and has correct scopes
- [ ] AWS account has sufficient limits/quotas

## 📝 Notes

Use this space to note any issues or observations:

_____________________________________________________________

_____________________________________________________________

_____________________________________________________________

_____________________________________________________________

## ✉️ Share Your Success!

Once working, you can:
- Take screenshots of your working pipeline
- Share your GitHub repo (if public)
- Blog about your experience
- Help others in the community

---

**Setup Date**: ____________
**Completed By**: ____________
**Total Time**: ____________
**Issues Encountered**: ____________
