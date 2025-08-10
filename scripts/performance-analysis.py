#!/usr/bin/env python3
"""
Performance Analysis Script for Search Endpoint

This script analyzes the performance of the search/general endpoint and provides
optimization recommendations.
"""

import json
import statistics
import time
from typing import Any, Dict, List

import requests


class PerformanceAnalyzer:
    """Analyze and optimize API performance."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str = "urbex-test-key-vjtyZHsCM2VpR_iGptzRxw",
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.endpoint = f"{base_url}/api/v1/search/general"
        self.headers = {"Content-Type": "application/json", "x-api-key": api_key}

    def run_performance_test(
        self, test_payloads: List[Dict], iterations: int = 5
    ) -> Dict[str, Any]:
        """Run performance tests with multiple payloads."""

        print("🚀 Starting Performance Analysis")
        print("=" * 50)

        results = {}

        for i, payload in enumerate(test_payloads):
            print(f"\n📊 Test Case {i+1}: {payload.get('description', 'Unnamed test')}")
            print("-" * 30)

            times = []
            errors = 0

            for iteration in range(iterations):
                try:
                    start_time = time.time()
                    response = requests.post(
                        self.endpoint,
                        headers=self.headers,
                        json=payload["data"],
                        timeout=30,
                    )
                    end_time = time.time()

                    response_time = (
                        end_time - start_time
                    ) * 1000  # Convert to milliseconds
                    times.append(response_time)

                    if response.status_code == 200:
                        response_data = response.json()
                        result_count = len(response_data.get("data", []))
                        print(
                            f"   Iteration {iteration+1}: {response_time:.2f}ms ({result_count} results)"
                        )
                    else:
                        print(
                            f"   Iteration {iteration+1}: ERROR {response.status_code}"
                        )
                        errors += 1

                except Exception as e:
                    print(f"   Iteration {iteration+1}: EXCEPTION {str(e)}")
                    errors += 1

            if times:
                results[f"test_case_{i+1}"] = {
                    "description": payload.get("description", "Unnamed test"),
                    "avg_time_ms": statistics.mean(times),
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                    "median_time_ms": statistics.median(times),
                    "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
                    "errors": errors,
                    "success_rate": ((iterations - errors) / iterations) * 100,
                }

        return results

    def analyze_bottlenecks(self) -> Dict[str, str]:
        """Analyze potential bottlenecks."""

        bottlenecks = {
            "database_queries": "CRITICAL - Likely multiple unoptimized queries",
            "geometry_processing": "HIGH - Complex polygon operations",
            "data_transformation": "MEDIUM - Multiple data transformations",
            "network_latency": "LOW - Local database should be fast",
            "memory_usage": "MEDIUM - Loading large result sets",
        }

        return bottlenecks

    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations."""

        recommendations = [
            "🔍 Database Optimizations:",
            "   - Add spatial indexes on geometry columns",
            "   - Optimize polygon intersection queries",
            "   - Use LIMIT in database queries, not Python filtering",
            "   - Consider connection pooling",
            "",
            "⚡ Query Optimizations:",
            "   - Combine multiple queries into joins",
            "   - Use EXISTS instead of COUNT where possible",
            "   - Add indexes on filter columns (estrato, prevetustz, etc.)",
            "",
            "🏗️ Architecture Optimizations:",
            "   - Implement Redis caching for frequent queries",
            "   - Use async database operations",
            "   - Implement pagination properly",
            "   - Consider database read replicas",
            "",
            "📊 Data Processing:",
            "   - Stream large result sets instead of loading all",
            "   - Use database-level data transformations",
            "   - Implement response compression",
            "",
            "🚀 Infrastructure:",
            "   - Enable database query cache",
            "   - Use CDN for static responses",
            "   - Implement API response caching",
        ]

        return recommendations


def main():
    """Run performance analysis."""

    # Test payloads with different complexity levels
    test_payloads = [
        {
            "description": "Simple polygon search",
            "data": {
                "polygon": "POLYGON ((-74.052562 4.690891, -74.052765 4.689811, -74.051499 4.689608, -74.051285 4.690773, -74.052562 4.690891))"
            },
        },
        {
            "description": "Complex search with all filters",
            "data": {
                "tipoinmueble": ["Todos"],
                "areamin": 0,
                "areamax": 0,
                "antiguedadmin": 0,
                "antiguedadmax": 2025,
                "estratomin": 0,
                "estratomax": 0,
                "polygon": "POLYGON ((-74.052562 4.690891, -74.052765 4.689811, -74.051499 4.689608, -74.051285 4.690773, -74.052562 4.690891))",
            },
        },
    ]

    analyzer = PerformanceAnalyzer()

    # Run performance tests
    results = analyzer.run_performance_test(test_payloads, iterations=3)

    # Display results
    print("\n" + "=" * 50)
    print("📈 PERFORMANCE ANALYSIS RESULTS")
    print("=" * 50)

    for test_name, test_result in results.items():
        print(f"\n🔬 {test_result['description']}")
        print(f"   Average Response Time: {test_result['avg_time_ms']:.2f}ms")
        print(
            f"   Min/Max: {test_result['min_time_ms']:.2f}ms / {test_result['max_time_ms']:.2f}ms"
        )
        print(f"   Success Rate: {test_result['success_rate']:.1f}%")

        # Performance rating
        avg_time = test_result["avg_time_ms"]
        if avg_time < 100:
            rating = "🟢 EXCELLENT"
        elif avg_time < 500:
            rating = "🟡 GOOD"
        elif avg_time < 2000:
            rating = "🟠 NEEDS IMPROVEMENT"
        else:
            rating = "🔴 CRITICAL - NEEDS OPTIMIZATION"

        print(f"   Performance Rating: {rating}")

    # Analyze bottlenecks
    print(f"\n🔍 BOTTLENECK ANALYSIS")
    print("-" * 30)
    bottlenecks = analyzer.analyze_bottlenecks()
    for bottleneck, severity in bottlenecks.items():
        print(f"   {bottleneck}: {severity}")

    # Show recommendations
    print(f"\n💡 OPTIMIZATION RECOMMENDATIONS")
    print("-" * 40)
    recommendations = analyzer.get_optimization_recommendations()
    for rec in recommendations:
        print(rec)

    print(f"\n✅ Analysis completed!")


if __name__ == "__main__":
    main()
