#!/bin/bash

# Script to generate DATABASE_URL for Real State Search API
# This script helps you create the correct database connection string

echo "🔧 DATABASE_URL Generator for Real State Search API"
echo "=================================================="
echo ""

# Function to generate DATABASE_URL
generate_database_url() {
    local db_type=$1
    local host=$2
    local port=$3
    local database=$4
    local username=$5
    local password=$6
    local ssl=$7
    
    local url="mysql+pymysql://${username}:${password}@${host}:${port}/${database}"
    
    if [ "$ssl" = "true" ]; then
        url="${url}?ssl_ca=rds-ca-2019-root.pem"
    fi
    
    echo "✅ Generated DATABASE_URL:"
    echo "${url}"
    echo ""
    echo "📋 Copy this to your GitHub Secrets as DATABASE_URL"
    echo ""
}

# Menu for different database types
echo "Select your database type:"
echo "1. AWS Aurora MySQL (Production)"
echo "2. AWS RDS MySQL (Production)"
echo "3. MySQL Local (Development)"
echo "4. Custom configuration"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🔧 AWS Aurora MySQL Configuration"
        echo "================================="
        echo ""
        read -p "Enter Aurora cluster endpoint (e.g., real-state-aurora-cluster.cluster-abc123def.us-east-2.rds.amazonaws.com): " host
        read -p "Enter database name (default: real_state_db): " database
        database=${database:-real_state_db}
        read -p "Enter username (default: real_state_user): " username
        username=${username:-real_state_user}
        read -s -p "Enter password: " password
        echo ""
        read -p "Use SSL? (y/n, default: y): " ssl_choice
        ssl_choice=${ssl_choice:-y}
        
        ssl="false"
        if [ "$ssl_choice" = "y" ] || [ "$ssl_choice" = "Y" ]; then
            ssl="true"
        fi
        
        generate_database_url "aurora" "$host" "3306" "$database" "$username" "$password" "$ssl"
        ;;
        
    2)
        echo ""
        echo "🔧 AWS RDS MySQL Configuration"
        echo "=============================="
        echo ""
        read -p "Enter RDS endpoint (e.g., real-state-rds.abc123def.us-east-2.rds.amazonaws.com): " host
        read -p "Enter database name (default: real_state_db): " database
        database=${database:-real_state_db}
        read -p "Enter username (default: real_state_user): " username
        username=${username:-real_state_user}
        read -s -p "Enter password: " password
        echo ""
        read -p "Use SSL? (y/n, default: y): " ssl_choice
        ssl_choice=${ssl_choice:-y}
        
        ssl="false"
        if [ "$ssl_choice" = "y" ] || [ "$ssl_choice" = "Y" ]; then
            ssl="true"
        fi
        
        generate_database_url "rds" "$host" "3306" "$database" "$username" "$password" "$ssl"
        ;;
        
    3)
        echo ""
        echo "🔧 MySQL Local Configuration"
        echo "============================"
        echo ""
        read -p "Enter host (default: localhost): " host
        host=${host:-localhost}
        read -p "Enter port (default: 3306): " port
        port=${port:-3306}
        read -p "Enter database name (default: real_state_db): " database
        database=${database:-real_state_db}
        read -p "Enter username (default: root): " username
        username=${username:-root}
        read -s -p "Enter password: " password
        echo ""
        
        generate_database_url "local" "$host" "$port" "$database" "$username" "$password" "false"
        ;;
        
    4)
        echo ""
        echo "🔧 Custom Configuration"
        echo "======================"
        echo ""
        read -p "Enter host: " host
        read -p "Enter port (default: 3306): " port
        port=${port:-3306}
        read -p "Enter database name: " database
        read -p "Enter username: " username
        read -s -p "Enter password: " password
        echo ""
        read -p "Use SSL? (y/n): " ssl_choice
        
        ssl="false"
        if [ "$ssl_choice" = "y" ] || [ "$ssl_choice" = "Y" ]; then
            ssl="true"
        fi
        
        generate_database_url "custom" "$host" "$port" "$database" "$username" "$password" "$ssl"
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo "📚 Additional Information:"
echo "=========================="
echo ""
echo "🔐 Security Recommendations:"
echo "   - Use strong passwords (12+ characters)"
echo "   - Enable SSL for production databases"
echo "   - Use IAM database authentication if possible"
echo "   - Restrict database access to Lambda VPC"
echo ""
echo "🌐 For AWS Aurora/RDS:"
echo "   - Ensure Lambda is in the same VPC as the database"
echo "   - Configure security groups to allow Lambda access"
echo "   - Use parameter groups for optimal performance"
echo ""
echo "📋 Next Steps:"
echo "   1. Copy the generated DATABASE_URL"
echo "   2. Add it to GitHub Secrets as DATABASE_URL"
echo "   3. Test the connection before deployment"
echo "" 