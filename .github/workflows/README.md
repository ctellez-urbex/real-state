# GitHub Actions Workflows

This directory contains the CI/CD workflows for the Real State Search API.

## 📋 Available Workflows

### 1. `deploy.yml` - Main Deployment Pipeline

**Triggers:**
- Push to `developer` branch
- Pull requests to `developer` branch

**Jobs:**

#### Test Job
- **Purpose**: Run comprehensive tests
- **Services**: MySQL 8.0 for testing
- **Coverage**: Generates coverage reports
- **Artifacts**: Uploads coverage to Codecov

#### Deploy Job
- **Purpose**: Deploy to AWS ECS
- **Trigger**: Only on push to `developer` branch
- **Steps**:
  1. Configure AWS credentials
  2. Login to Amazon ECR
  3. Build and push Docker image
  4. Deploy to ECS Fargate
  5. Notify deployment status

#### Security Scan Job
- **Purpose**: Security vulnerability scanning
- **Tools**: Bandit (Python security) and Safety (dependency check)
- **Artifacts**: Security reports

## 🔧 Configuration

### Required Secrets
Configure these secrets in your GitHub repository:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### Environment Variables
The workflow uses these environment variables:

```yaml
env:
  AWS_REGION: us-east-2
  PYTHON_VERSION: '3.12'
```

## 🚀 Deployment Process

### 1. Code Push
When code is pushed to the `developer` branch:

1. **Tests Run**: All tests execute with MySQL service
2. **Coverage Generated**: Test coverage report created
3. **Security Scan**: Vulnerability check performed
4. **Deployment**: If tests pass, deploy to AWS

### 2. Pull Request
When a PR is created against `developer`:

1. **Tests Run**: All tests execute
2. **Coverage Generated**: Coverage report created
3. **Security Scan**: Vulnerability check performed
4. **No Deployment**: Deployment only happens on merge

## 📊 Monitoring

### Workflow Status
- Check workflow runs in GitHub Actions tab
- Monitor test results and coverage
- Review security scan reports

### Deployment Status
- ECS service status in AWS Console
- CloudWatch logs for application monitoring
- Health check endpoint monitoring

## 🔧 Customization

### Adding New Jobs
To add new jobs to the workflow:

```yaml
new-job:
  runs-on: ubuntu-latest
  needs: test  # Dependencies
  steps:
    - name: New Step
      run: echo "New job"
```

### Modifying Triggers
To change when workflows run:

```yaml
on:
  push:
    branches: [ main, developer ]  # Add more branches
  pull_request:
    branches: [ main, developer ]
```

### Environment-Specific Deployments
To deploy to different environments:

```yaml
deploy-staging:
  if: github.ref == 'refs/heads/staging'
  # Staging deployment steps

deploy-production:
  if: github.ref == 'refs/heads/main'
  # Production deployment steps
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Tests Fail
- Check MySQL service is running
- Verify environment variables are set
- Review test logs for specific errors

#### 2. Deployment Fails
- Verify AWS credentials are correct
- Check ECR repository exists
- Ensure ECS cluster and service are configured

#### 3. Security Scan Issues
- Review Bandit and Safety reports
- Update dependencies if needed
- Address security vulnerabilities

### Debug Commands
```bash
# Check workflow status
gh run list

# View workflow logs
gh run view --log

# Rerun failed workflow
gh run rerun <run-id>
```

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://docs.pytest.org/)

## 🤝 Contributing

When modifying workflows:

1. Test changes in a fork first
2. Update documentation
3. Follow the existing patterns
4. Add appropriate comments
5. Test all scenarios 