#!/bin/bash
# Quick setup script for local testing

echo "==================================="
echo "ML CI/CD Pipeline - Setup Helper"
echo "==================================="

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Install from: https://aws.amazon.com/cli/"
    exit 1
else
    echo "✓ AWS CLI installed"
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Install from: https://git-scm.com/"
    exit 1
else
    echo "✓ Git installed"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install from: https://www.python.org/"
    exit 1
else
    echo "✓ Python 3 installed"
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install from: https://www.docker.com/"
    exit 1
else
    echo "✓ Docker installed"
fi

echo ""
echo "All prerequisites satisfied!"
echo ""

# Test local build
echo "Would you like to test Docker build locally? (y/n)"
read -r response

if [[ "$response" == "y" ]]; then
    echo ""
    echo "Building Docker image locally..."
    docker build -t ml-model-test .
    
    if [ $? -eq 0 ]; then
        echo "✓ Docker build successful!"
        echo ""
        echo "To test training locally, run:"
        echo "docker run ml-model-test python train.py"
    else
        echo "❌ Docker build failed"
        exit 1
    fi
fi

echo ""
echo "==================================="
echo "Next Steps:"
echo "==================================="
echo "1. Create GitHub repository"
echo "2. Get GitHub personal access token"
echo "3. Push this code to GitHub"
echo "4. Deploy CloudFormation stack in AWS Console"
echo "5. Wait for pipeline to complete"
echo "6. Test endpoint with: python src/test_endpoint.py"
echo ""
echo "See README.md for detailed instructions"
echo ""
