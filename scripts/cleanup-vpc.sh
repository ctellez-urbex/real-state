#!/bin/bash

# Script to clean up VPC resources created for external database connectivity
# Since we're no longer using VPC for Lambda, these resources can be safely deleted

set -e

echo "🧹 VPC Cleanup Script"
echo "===================="

# Load environment variables
if [ -f .env ]; then
    source .env
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure'"
    exit 1
fi

echo "🔍 Current VPC resources to delete:"
echo "   Security Group: ${VPC_SECURITY_GROUP_ID}"
echo "   Subnet 1: ${VPC_SUBNET_ID_1}"
echo "   Subnet 2: ${VPC_SUBNET_ID_2}"
echo ""

# Get VPC ID from one of the subnets
echo "🔍 Finding VPC ID..."
VPC_ID=$(aws ec2 describe-subnets --subnet-ids ${VPC_SUBNET_ID_1} --query 'Subnets[0].VpcId' --output text 2>/dev/null || echo "")

if [ -z "$VPC_ID" ] || [ "$VPC_ID" = "None" ]; then
    echo "❌ Could not find VPC ID. Resources may already be deleted."
    exit 1
fi

echo "📋 VPC ID found: ${VPC_ID}"

# Function to safely delete resource
safe_delete() {
    local resource_type=$1
    local resource_id=$2
    local delete_command=$3

    echo "🗑️  Deleting ${resource_type}: ${resource_id}"

    if eval $delete_command > /dev/null 2>&1; then
        echo "   ✅ ${resource_type} deleted successfully"
    else
        echo "   ⚠️  ${resource_type} may already be deleted or in use"
    fi
}

echo ""
echo "🚀 Starting deletion process..."
echo ""

# 1. Delete Security Group
safe_delete "Security Group" "${VPC_SECURITY_GROUP_ID}" \
    "aws ec2 delete-security-group --group-id ${VPC_SECURITY_GROUP_ID}"

# 2. Delete Subnets
safe_delete "Subnet 1" "${VPC_SUBNET_ID_1}" \
    "aws ec2 delete-subnet --subnet-id ${VPC_SUBNET_ID_1}"

safe_delete "Subnet 2" "${VPC_SUBNET_ID_2}" \
    "aws ec2 delete-subnet --subnet-id ${VPC_SUBNET_ID_2}"

# 3. Find and delete Route Table (if custom)
echo "🔍 Finding custom route tables..."
ROUTE_TABLES=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=${VPC_ID}" --query 'RouteTables[?Associations[0].Main==`false`].RouteTableId' --output text)

if [ -n "$ROUTE_TABLES" ] && [ "$ROUTE_TABLES" != "None" ]; then
    for RT_ID in $ROUTE_TABLES; do
        # First, disassociate route table from subnets
        echo "🔍 Checking route table associations for ${RT_ID}..."
        ASSOCIATIONS=$(aws ec2 describe-route-tables --route-table-ids ${RT_ID} --query 'RouteTables[0].Associations[?Main==`false`].RouteTableAssociationId' --output text)

        if [ -n "$ASSOCIATIONS" ] && [ "$ASSOCIATIONS" != "None" ]; then
            for ASSOC_ID in $ASSOCIATIONS; do
                safe_delete "Route Table Association" "${ASSOC_ID}" \
                    "aws ec2 disassociate-route-table --association-id ${ASSOC_ID}"
            done
        fi

        safe_delete "Route Table" "${RT_ID}" \
            "aws ec2 delete-route-table --route-table-id ${RT_ID}"
    done
else
    echo "   ℹ️  No custom route tables found"
fi

# 4. Find and delete Internet Gateway
echo "🔍 Finding Internet Gateway..."
IGW_ID=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=${VPC_ID}" --query 'InternetGateways[0].InternetGatewayId' --output text 2>/dev/null || echo "")

if [ -n "$IGW_ID" ] && [ "$IGW_ID" != "None" ]; then
    # Detach Internet Gateway first
    safe_delete "Internet Gateway (detach)" "${IGW_ID}" \
        "aws ec2 detach-internet-gateway --internet-gateway-id ${IGW_ID} --vpc-id ${VPC_ID}"

    safe_delete "Internet Gateway" "${IGW_ID}" \
        "aws ec2 delete-internet-gateway --internet-gateway-id ${IGW_ID}"
else
    echo "   ℹ️  No Internet Gateway found"
fi

# 5. Delete VPC
echo "🔍 Waiting a moment for resources to be fully deleted..."
sleep 5

safe_delete "VPC" "${VPC_ID}" \
    "aws ec2 delete-vpc --vpc-id ${VPC_ID}"

echo ""
echo "✅ VPC cleanup completed!"
echo ""
echo "💡 Next steps:"
echo "   1. Remove VPC variables from .env file"
echo "   2. Update env.example to remove VPC variables"
echo "   3. Your Lambda will continue working without VPC"
echo ""
echo "💰 Cost savings: No NAT Gateway charges (~$45/month saved)"
