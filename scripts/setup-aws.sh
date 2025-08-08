#!/bin/bash

echo "🔧 AWS Credentials Setup for Urbex API"
echo "======================================"

echo ""
echo "📋 Please follow these steps to configure AWS credentials:"
echo ""
echo "1. Go to AWS Console → IAM → Users → Your User"
echo "2. Security credentials → Create access key"
echo "3. Save the Access Key ID and Secret Access Key"
echo ""

read -p "Do you have your AWS credentials ready? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🔑 Configuring AWS credentials..."
    aws configure

    echo ""
    echo "✅ Testing AWS credentials..."
    aws sts get-caller-identity

    echo ""
    echo "🚀 Ready to deploy! Run: serverless deploy --stage prod"
else
    echo ""
    echo "❌ Please get your AWS credentials first and run this script again."
    echo ""
    echo "📚 Helpful links:"
    echo "- AWS IAM Console: https://console.aws.amazon.com/iam/"
    echo "- AWS CLI Setup: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html"
fi
