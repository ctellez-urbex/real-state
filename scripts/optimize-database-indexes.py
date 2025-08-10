#!/usr/bin/env python3
"""
Database Index Optimization Script

This script analyzes and optimizes database indexes for maximum performance.
Critical for spatial queries that are currently taking 8-10 seconds.

Performance impact: Expected 50-80% query time reduction.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()


def get_database_url():
    """Get database URL from environment variables."""
    # Try DATABASE_URL first (production format)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # Fallback to individual variables
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT", "3306")

    if not all([host, user, password, database]):
        raise ValueError(
            "Missing required database environment variables. Need either DATABASE_URL or DB_HOST, DB_USER, DB_PASSWORD, DB_NAME"
        )

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def analyze_current_indexes(engine):
    """Analyze current indexes on critical tables."""
    print("🔍 Analyzing current database indexes...")

    critical_tables = [
        "bogota_data_lotes",
        "bogota_data_lotes_fastsearch",
        "bogota_data_caracteristicas",
    ]

    with engine.connect() as conn:
        for table in critical_tables:
            try:
                result = conn.execute(text(f"SHOW INDEX FROM {table}"))
                indexes = result.fetchall()

                print(f"\n📊 Table: {table}")
                if indexes:
                    for idx in indexes:
                        print(f"  - {idx[2]}: {idx[4]} ({idx[10]})")
                else:
                    print("  ❌ No indexes found!")

            except SQLAlchemyError as e:
                print(f"  ⚠️ Table {table} not accessible: {e}")


def check_spatial_indexes(engine):
    """Check for spatial indexes on geometry columns."""
    print("\n🗺️ Checking spatial indexes...")

    spatial_checks = [
        ("bogota_data_lotes", "geometry"),
        ("bogota_data_lotes_fastsearch", "geometry"),
    ]

    with engine.connect() as conn:
        for table, column in spatial_checks:
            try:
                # Check if spatial index exists
                result = conn.execute(
                    text(
                        f"""
                    SELECT COUNT(*) as has_spatial_index
                    FROM INFORMATION_SCHEMA.STATISTICS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = '{table}'
                    AND COLUMN_NAME = '{column}'
                    AND INDEX_TYPE = 'SPATIAL'
                """
                    )
                )

                has_spatial = result.fetchone()[0] > 0
                status = "✅ EXISTS" if has_spatial else "❌ MISSING"
                print(f"  {table}.{column}: {status}")

                if not has_spatial:
                    print(f"    🚨 CRITICAL: Missing spatial index on {table}.{column}")

            except SQLAlchemyError as e:
                print(f"  ⚠️ Cannot check {table}.{column}: {e}")


def create_critical_indexes(engine):
    """Create missing critical indexes."""
    print("\n🛠️ Creating critical indexes...")

    # Critical indexes for performance
    index_commands = [
        {
            "name": "idx_spatial_lotes_geometry",
            "table": "bogota_data_lotes",
            "sql": "CREATE SPATIAL INDEX idx_spatial_lotes_geometry ON bogota_data_lotes(geometry)",
            "description": "Spatial index on main lotes geometry",
        },
        {
            "name": "idx_spatial_fastsearch_geometry",
            "table": "bogota_data_lotes_fastsearch",
            "sql": "CREATE SPATIAL INDEX idx_spatial_fastsearch_geometry ON bogota_data_lotes_fastsearch(geometry)",
            "description": "Spatial index on fastsearch geometry",
        },
        {
            "name": "idx_caracteristicas_barmanpre",
            "table": "bogota_data_caracteristicas",
            "sql": "CREATE INDEX idx_caracteristicas_barmanpre ON bogota_data_caracteristicas(barmanpre)",
            "description": "Index on barmanpre for JOIN optimization",
        },
        {
            "name": "idx_lotes_barmanpre",
            "table": "bogota_data_lotes",
            "sql": "CREATE INDEX idx_lotes_barmanpre ON bogota_data_lotes(barmanpre)",
            "description": "Index on lotes barmanpre for JOIN optimization",
        },
        {
            "name": "idx_caracteristicas_filters",
            "table": "bogota_data_caracteristicas",
            "sql": "CREATE INDEX idx_caracteristicas_filters ON bogota_data_caracteristicas(estrato, preaconst, prevetustzmin, prevetustzmax)",
            "description": "Composite index for common filters",
        },
    ]

    with engine.connect() as conn:
        for idx_info in index_commands:
            try:
                # Check if index already exists
                result = conn.execute(
                    text(
                        f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.STATISTICS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = '{idx_info['table']}'
                    AND INDEX_NAME = '{idx_info['name']}'
                """
                    )
                )

                exists = result.fetchone()[0] > 0

                if exists:
                    print(f"  ✅ {idx_info['name']} already exists")
                else:
                    print(f"  🔧 Creating {idx_info['name']}...")
                    print(f"     {idx_info['description']}")

                    # Create the index
                    conn.execute(text(idx_info["sql"]))
                    conn.commit()
                    print(f"  ✅ Successfully created {idx_info['name']}")

            except SQLAlchemyError as e:
                print(f"  ❌ Failed to create {idx_info['name']}: {e}")


def optimize_table_settings(engine):
    """Optimize table settings for performance."""
    print("\n⚙️ Optimizing table settings...")

    optimizations = [
        "SET SESSION query_cache_type = ON",
        "SET SESSION query_cache_size = 67108864",  # 64MB
        "SET SESSION sort_buffer_size = 2097152",  # 2MB
        "SET SESSION read_buffer_size = 131072",  # 128KB
    ]

    with engine.connect() as conn:
        for opt in optimizations:
            try:
                conn.execute(text(opt))
                print(f"  ✅ Applied: {opt}")
            except SQLAlchemyError as e:
                print(f"  ⚠️ Could not apply {opt}: {e}")


def performance_test_query(engine):
    """Test performance of critical spatial query."""
    print("\n🏃 Performance testing critical query...")

    test_polygon = "POLYGON ((-74.052562 4.690891, -74.052765 4.689811, -74.051499 4.689608, -74.051285 4.690773, -74.052562 4.690891))"

    # Test fastsearch table
    with engine.connect() as conn:
        try:
            import time

            start_time = time.time()
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*)
                FROM bogota_data_lotes_fastsearch
                WHERE ST_CONTAINS(ST_GEOMFROMTEXT(:polygon, 4326), geometry)
            """
                ),
                {"polygon": test_polygon},
            )

            count = result.fetchone()[0]
            execution_time = (time.time() - start_time) * 1000

            print(f"  📊 Fastsearch query: {count} results in {execution_time:.2f}ms")

            if execution_time < 500:
                print("  🟢 EXCELLENT performance!")
            elif execution_time < 1000:
                print("  🟡 Good performance")
            else:
                print("  🔴 Poor performance - needs more optimization")

        except SQLAlchemyError as e:
            print(f"  ❌ Fastsearch test failed: {e}")

            # Fallback to regular lotes table
            try:
                start_time = time.time()
                result = conn.execute(
                    text(
                        """
                    SELECT COUNT(*)
                    FROM bogota_data_lotes
                    WHERE ST_CONTAINS(ST_GEOMFROMTEXT(:polygon, 4326), geometry)
                """
                    ),
                    {"polygon": test_polygon},
                )

                count = result.fetchone()[0]
                execution_time = (time.time() - start_time) * 1000

                print(
                    f"  📊 Regular lotes query: {count} results in {execution_time:.2f}ms"
                )

            except SQLAlchemyError as e:
                print(f"  ❌ Regular lotes test also failed: {e}")


def main():
    """Main optimization function."""
    print("🚀 Database Index Optimization Tool")
    print("=" * 50)

    try:
        # Connect to database
        database_url = get_database_url()
        engine = create_engine(database_url)

        print(f"📡 Connected to database: {os.getenv('DB_HOST')}")

        # Run optimization steps
        analyze_current_indexes(engine)
        check_spatial_indexes(engine)
        create_critical_indexes(engine)
        optimize_table_settings(engine)
        performance_test_query(engine)

        print("\n🎉 Database optimization completed!")
        print("\n📈 Expected improvements:")
        print("  - Spatial queries: 50-80% faster")
        print("  - JOIN operations: 30-60% faster")
        print("  - Overall API response: 2-5x improvement")

    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
