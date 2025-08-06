# Deployment Guide

This document provides comprehensive instructions for deploying the Real State Search API to AWS using GitHub Actions.

## 🚀 Overview

The deployment pipeline uses:
- **GitHub Actions** for CI/CD
- **Amazon ECR** for container registry
- **Amazon ECS Fargate** for container orchestration
- **AWS Secrets Manager** for secure configuration
- **AWS CloudWatch** for logging

## 📋 Prerequisites

### AWS Resources Required
1. **ECR Repository**: `real-state-api`
2. **ECS Cluster**: `real-state-cluster`
3. **ECS Service**: `real-state-api-service`
4. **IAM Roles**: `ecsTaskExecutionRole` and `ecsTaskRole`
5. **Secrets Manager**: Secrets for configuration
6. **CloudWatch Log Group**: `/ecs/real-state-api`

### GitHub Secrets Required
Configure these secrets in your GitHub repository:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

## 🛠️ AWS Setup

### 1. Create ECR Repository
```bash
aws ecr create-repository \
  --repository-name real-state-api \
  --region us-east-2
```

### 2. Create ECS Cluster
```bash
aws ecs create-cluster \
  --cluster-name real-state-cluster \
  --region us-east-2
```

### 3. Create IAM Roles

#### ECS Task Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

#### ECS Task Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-2:ACCOUNT_ID:secret:real-state/*"
      ]
    }
  ]
}
```

### 4. Create Secrets in AWS Secrets Manager

#### Database URL Secret
```bash
aws secretsmanager create-secret \
  --name real-state/database-url \
  --description "Database connection URL" \
  --secret-string "mysql+pymysql://user:password@host:port/database" \
  --region us-east-2
```

#### API Keys Secret
```bash
aws secretsmanager create-secret \
  --name real-state/api-keys \
  --description "API authentication keys" \
  --secret-string '["key1", "key2"]' \
  --region us-east-2
```

#### Allowed Hosts Secret
```bash
aws secretsmanager create-secret \
  --name real-state/allowed-hosts \
  --description "Allowed hosts configuration" \
  --secret-string '["your-domain.com", "api.your-domain.com"]' \
  --region us-east-2
```

#### Allowed Origins Secret
```bash
aws secretsmanager create-secret \
  --name real-state/allowed-origins \
  --description "CORS allowed origins" \
  --secret-string '["https://your-frontend.com"]' \
  --region us-east-2
```

### 5. Create CloudWatch Log Group
```bash
aws logs create-log-group \
  --log-group-name /ecs/real-state-api \
  --region us-east-2
```

## 🔄 Deployment Process

### Automatic Deployment
The deployment is triggered automatically when code is pushed to the `developer` branch:

1. **Test Job**: Runs all tests with MySQL service
2. **Deploy Job**: Builds and deploys to AWS (only on push to developer)
3. **Security Scan**: Runs security checks

### Manual Deployment
For manual deployment:

```bash
# Build Docker image locally
docker build -t real-state-api .

# Tag for ECR
docker tag real-state-api:latest ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/real-state-api:latest

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/real-state-api:latest

# Update ECS service
aws ecs update-service \
  --cluster real-state-cluster \
  --service real-state-api-service \
  --force-new-deployment \
  --region us-east-2
```

## 📊 Monitoring

### CloudWatch Logs
Access application logs:
```bash
aws logs describe-log-streams \
  --log-group-name /ecs/real-state-api \
  --region us-east-2
```

### ECS Service Status
Check service status:
```bash
aws ecs describe-services \
  --cluster real-state-cluster \
  --services real-state-api-service \
  --region us-east-2
```

### Health Check
Monitor application health:
```bash
curl https://your-api-domain.com/health
```

## 🔧 Configuration

### Environment Variables
The application uses these environment variables:

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Secrets Manager | Database connection string |
| `API_KEYS` | Secrets Manager | API authentication keys |
| `ALLOWED_HOSTS` | Secrets Manager | Allowed host domains |
| `ALLOWED_ORIGINS` | Secrets Manager | CORS allowed origins |
| `ENVIRONMENT` | Task Definition | Environment name (production) |
| `AWS_REGION` | Task Definition | AWS region (us-east-2) |

### Task Definition Configuration
- **CPU**: 512 units (0.5 vCPU)
- **Memory**: 1024 MB
- **Port**: 8000
- **Health Check**: HTTP GET /health

## 🚨 Troubleshooting

### Common Issues

#### 1. ECS Task Fails to Start
- Check IAM roles have correct permissions
- Verify secrets exist in Secrets Manager
- Check CloudWatch logs for error messages

#### 2. Application Can't Connect to Database
- Verify DATABASE_URL secret is correct
- Check security groups allow database access
- Ensure database is accessible from ECS

#### 3. Health Check Fails
- Verify application is listening on port 8000
- Check application logs for startup errors
- Ensure /health endpoint is working

#### 4. CORS Issues
- Verify ALLOWED_ORIGINS secret is correctly formatted
- Check frontend domain is included in allowed origins

### Debug Commands

#### Check ECS Task Logs
```bash
aws logs get-log-events \
  --log-group-name /ecs/real-state-api \
  --log-stream-name ecs/real-state-api/TASK_ID \
  --region us-east-2
```

#### Describe ECS Task
```bash
aws ecs describe-tasks \
  --cluster real-state-cluster \
  --tasks TASK_ID \
  --region us-east-2
```

#### Check Secrets
```bash
aws secretsmanager get-secret-value \
  --secret-id real-state/database-url \
  --region us-east-2
```

## 🔒 Security Considerations

### Network Security
- Use private subnets for ECS tasks
- Configure security groups to allow only necessary traffic
- Use VPC endpoints for AWS services

### Secrets Management
- Never commit secrets to version control
- Use AWS Secrets Manager for all sensitive data
- Rotate secrets regularly

### Container Security
- Use minimal base images
- Scan images for vulnerabilities
- Keep dependencies updated

## 📈 Scaling

### Auto Scaling
Configure auto scaling for the ECS service:

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/real-state-cluster/real-state-api-service \
  --min-capacity 1 \
  --max-capacity 10 \
  --region us-east-2
```

### Load Balancer
For production, consider adding an Application Load Balancer:

```bash
aws elbv2 create-load-balancer \
  --name real-state-alb \
  --subnets subnet-12345678 subnet-87654321 \
  --security-groups sg-12345678 \
  --region us-east-2
```

## 📞 Support

For deployment issues:
1. Check CloudWatch logs first
2. Review ECS service events
3. Verify AWS resources are properly configured
4. Contact the DevOps team 