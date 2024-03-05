# Stage 1: Build stage for compiling dependencies
FROM amazonlinux:2 as build-stage

# Install Python 3.8, development tools, and AWS CLI
RUN yum install -y amazon-linux-extras && \
    amazon-linux-extras enable python3.8 && \
    yum install -y python3.8 python3.8-devel python3.8-pip && \
    yum groupinstall -y "Development Tools"

# Upgrade pip
RUN python3.8 -m pip install --upgrade pip

# Install AWS CLI
RUN python3.8 -m pip install awscli

# Use ARG to declare AWS credentials and the default region for use during the build
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION=eu-west-2

# Configure AWS CLI using the provided build arguments
RUN aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID && \
    aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY && \
    aws configure set default.region $AWS_DEFAULT_REGION

# Create a directory for the app
WORKDIR /var/task

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install Python dependencies from requirements.txt into the build directory
RUN python3.8 -m pip install -r requirements.txt --target /var/task

# Create the data directory
RUN mkdir /data

# Download the required VCF files from the S3 bucket into the /data directory
RUN aws s3 cp s3://hap1vcf/GATK_variants.vcf.gz /data/ && \
    aws s3 cp s3://hap1vcf/GATK_variants.vcf.gz.tbi /data/

# Stage 2: Setup the Lambda runtime environment with compiled dependencies
FROM public.ecr.aws/lambda/python:3.8

# Copy installed packages from the build stage
COPY --from=build-stage /var/task /var/task

# Copy the downloaded VCF files from the build stage
COPY --from=build-stage /data /data

# Copy your Lambda function code
COPY lambda_function.py /var/task/

# Set the CMD to your handler
CMD ["lambda_function.lambda_handler"]
