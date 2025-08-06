#!/usr/bin/env python3
"""
Script to create initial migration for Bogotá database tables.
"""

import os
import sys
import subprocess

def create_initial_migration():
    """Create initial migration for all Bogotá tables."""
    
    print("Creating initial migration for Bogotá database tables...")
    
    try:
        # Generate the initial migration
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", 
            "-m", "Initial migration for Bogotá real estate tables"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Initial migration created successfully!")
            print("Migration output:")
            print(result.stdout)
        else:
            print("❌ Error creating migration:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def run_migration():
    """Run the migration to create tables."""
    
    print("\nRunning migration to create tables...")
    
    try:
        # Run the migration
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration applied successfully!")
            print("Migration output:")
            print(result.stdout)
        else:
            print("❌ Error applying migration:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Bogotá Real Estate Database Migration Tool")
    print("=" * 50)
    
    # Create initial migration
    if create_initial_migration():
        # Ask user if they want to run the migration
        response = input("\nDo you want to apply the migration now? (y/n): ")
        if response.lower() in ['y', 'yes']:
            run_migration()
        else:
            print("Migration created but not applied. Run 'alembic upgrade head' to apply it.")
    else:
        print("Failed to create migration.") 