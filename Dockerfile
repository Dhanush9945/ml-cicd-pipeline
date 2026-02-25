FROM public.ecr.aws/docker/library/python:3.9-slim

# Set working directory
WORKDIR /opt/ml

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy training and inference scripts
COPY src/train.py /opt/ml/code/train.py
COPY src/inference.py /opt/ml/code/inference.py

# Set Python path
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/ml/code:${PATH}"

# SageMaker uses this as entry point
ENV SAGEMAKER_PROGRAM train.py