#!/usr/bin/env python3
"""
Endpoint Comparison Tool

Compares the data results between different endpoint versions to ensure
they return consistent and correct information.
"""

import json
import time
from typing import Any, Dict, List

import requests


def make_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Make a request to an endpoint and return the response."""
    url = f"http://localhost:8000/api/v1/search/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": "urbex-test-key-vjtyZHsCM2VpR_iGptzRxw",
    }

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        execution_time = (time.time() - start_time) * 1000
        result = response.json()

        return {
            "success": True,
            "data": result,
            "execution_time_ms": execution_time,
            "status_code": response.status_code,
        }
    except requests.RequestException as e:
        execution_time = (time.time() - start_time) * 1000
        return {
            "success": False,
            "error": str(e),
            "execution_time_ms": execution_time,
            "status_code": getattr(e.response, "status_code", None)
            if hasattr(e, "response")
            else None,
        }


def compare_property_data(
    data1: List[Dict], data2: List[Dict], endpoint1: str, endpoint2: str
) -> Dict[str, Any]:
    """Compare property data between two endpoints."""
    comparison = {
        "total_count_match": len(data1) == len(data2),
        "count_endpoint1": len(data1),
        "count_endpoint2": len(data2),
        "barmanpre_sets_match": False,
        "field_consistency": {},
        "data_quality": {},
    }

    if not data1 and not data2:
        comparison["barmanpre_sets_match"] = True
        return comparison

    # Extract barmanpre codes
    barmanpre1 = {item.get("barmanpre") for item in data1 if item.get("barmanpre")}
    barmanpre2 = {item.get("barmanpre") for item in data2 if item.get("barmanpre")}

    comparison["barmanpre_sets_match"] = barmanpre1 == barmanpre2
    comparison["barmanpre_only_in_endpoint1"] = list(barmanpre1 - barmanpre2)
    comparison["barmanpre_only_in_endpoint2"] = list(barmanpre2 - barmanpre1)

    # Compare common barmanpre entries
    common_barmanpre = barmanpre1 & barmanpre2

    if common_barmanpre:
        # Create lookup dictionaries
        lookup1 = {
            item["barmanpre"]: item
            for item in data1
            if item.get("barmanpre") in common_barmanpre
        }
        lookup2 = {
            item["barmanpre"]: item
            for item in data2
            if item.get("barmanpre") in common_barmanpre
        }

        # Check field consistency for common entries
        field_mismatches = {}

        for barmanpre in common_barmanpre:
            if barmanpre in lookup1 and barmanpre in lookup2:
                item1 = lookup1[barmanpre]
                item2 = lookup2[barmanpre]

                # Compare all fields
                for field in set(item1.keys()) | set(item2.keys()):
                    val1 = item1.get(field)
                    val2 = item2.get(field)

                    if val1 != val2:
                        if field not in field_mismatches:
                            field_mismatches[field] = []
                        field_mismatches[field].append(
                            {
                                "barmanpre": barmanpre,
                                f"{endpoint1}_value": val1,
                                f"{endpoint2}_value": val2,
                            }
                        )

        comparison["field_consistency"] = field_mismatches
        comparison["common_entries_count"] = len(common_barmanpre)

    return comparison


def analyze_data_quality(data: List[Dict], endpoint: str) -> Dict[str, Any]:
    """Analyze data quality for an endpoint."""
    if not data:
        return {"total_properties": 0, "quality_issues": []}

    quality_issues = []
    field_stats = {}

    for item in data:
        # Check for missing critical fields
        if not item.get("barmanpre"):
            quality_issues.append("Missing barmanpre")

        # Check for null geometry
        if item.get("wkt") is None:
            quality_issues.append(
                f"Missing geometry for {item.get('barmanpre', 'unknown')}"
            )

        # Collect field statistics
        for field, value in item.items():
            if field not in field_stats:
                field_stats[field] = {"non_null": 0, "null": 0, "total": 0}

            field_stats[field]["total"] += 1
            if value is not None and value != "":
                field_stats[field]["non_null"] += 1
            else:
                field_stats[field]["null"] += 1

    return {
        "total_properties": len(data),
        "quality_issues": quality_issues,
        "field_completeness": {
            field: f"{stats['non_null']}/{stats['total']} ({(stats['non_null']/stats['total']*100):.1f}%)"
            for field, stats in field_stats.items()
        },
    }


def main():
    """Main comparison function."""
    print("🔍 Endpoint Results Comparison Tool")
    print("=" * 50)

    # Test payload
    test_payload = {
        "tipoinmueble": ["Todos"],
        "areamin": 0,
        "areamax": 0,
        "antiguedadmin": 0,
        "antiguedadmax": 2025,
        "estratomin": 0,
        "estratomax": 0,
        "limit": 20,
        "polygon": "POLYGON ((-74.052562 4.690891, -74.052765 4.689811, -74.051499 4.689608, -74.051285 4.690773, -74.052562 4.690891))",
    }

    # Endpoints to compare
    endpoints = ["general", "optimized", "ultra", "final"]

    print(f"🧪 Testing with payload:")
    print(f"  - Limit: {test_payload['limit']}")
    print(f"  - Polygon: {test_payload['polygon'][:50]}...")
    print()

    # Collect results from all endpoints
    results = {}

    for endpoint in endpoints:
        print(f"📡 Testing endpoint: /api/v1/search/{endpoint}")
        result = make_request(endpoint, test_payload)
        results[endpoint] = result

        if result["success"]:
            data = result["data"]
            print(
                f"  ✅ Success: {data.get('total', 0)} properties in {result['execution_time_ms']:.2f}ms"
            )
        else:
            print(f"  ❌ Failed: {result['error']}")
        print()

    # Performance comparison
    print("⚡ Performance Comparison:")
    print("-" * 30)
    successful_results = {k: v for k, v in results.items() if v["success"]}

    if successful_results:
        sorted_by_speed = sorted(
            successful_results.items(), key=lambda x: x[1]["execution_time_ms"]
        )

        for i, (endpoint, result) in enumerate(sorted_by_speed):
            speed_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📊"
            print(f"  {speed_icon} {endpoint}: {result['execution_time_ms']:.2f}ms")

    print()

    # Data consistency comparison
    print("📊 Data Consistency Analysis:")
    print("-" * 35)

    successful_endpoints = [k for k, v in results.items() if v["success"]]

    if len(successful_endpoints) >= 2:
        # Compare each endpoint with the first successful one (baseline)
        baseline = successful_endpoints[0]
        baseline_data = results[baseline]["data"].get("data", [])

        print(f"📋 Using '{baseline}' as baseline ({len(baseline_data)} properties)")
        print()

        for endpoint in successful_endpoints[1:]:
            endpoint_data = results[endpoint]["data"].get("data", [])

            print(f"🔄 Comparing '{baseline}' vs '{endpoint}':")

            comparison = compare_property_data(
                baseline_data, endpoint_data, baseline, endpoint
            )

            # Results summary
            if comparison["total_count_match"]:
                print(
                    f"  ✅ Total count match: {comparison['count_endpoint1']} properties"
                )
            else:
                print(
                    f"  ⚠️ Count mismatch: {comparison['count_endpoint1']} vs {comparison['count_endpoint2']}"
                )

            if comparison["barmanpre_sets_match"]:
                print(f"  ✅ Same properties returned (barmanpre match)")
            else:
                print(f"  ❌ Different properties returned:")
                if comparison["barmanpre_only_in_endpoint1"]:
                    print(
                        f"    - Only in {baseline}: {comparison['barmanpre_only_in_endpoint1'][:3]}..."
                    )
                if comparison["barmanpre_only_in_endpoint2"]:
                    print(
                        f"    - Only in {endpoint}: {comparison['barmanpre_only_in_endpoint2'][:3]}..."
                    )

            # Field consistency
            if comparison["field_consistency"]:
                print(f"  ⚠️ Field inconsistencies found:")
                for field, mismatches in list(comparison["field_consistency"].items())[
                    :3
                ]:
                    print(f"    - {field}: {len(mismatches)} differences")
            else:
                print(f"  ✅ All fields consistent for common properties")

            print()

    # Data quality analysis
    print("🔍 Data Quality Analysis:")
    print("-" * 28)

    for endpoint in successful_endpoints:
        endpoint_data = results[endpoint]["data"].get("data", [])
        quality = analyze_data_quality(endpoint_data, endpoint)

        print(f"📈 {endpoint} endpoint:")
        print(f"  - Total properties: {quality['total_properties']}")
        print(f"  - Quality issues: {len(quality['quality_issues'])}")

        # Show key field completeness
        key_fields = ["barmanpre", "preaconst", "estrato", "wkt"]
        for field in key_fields:
            if field in quality["field_completeness"]:
                print(f"  - {field}: {quality['field_completeness'][field]}")
        print()

    # Final recommendation
    print("🎯 Recommendation:")
    print("-" * 18)

    if successful_results:
        fastest_endpoint = min(
            successful_results.items(), key=lambda x: x[1]["execution_time_ms"]
        )
        print(
            f"💡 Fastest endpoint: '{fastest_endpoint[0]}' ({fastest_endpoint[1]['execution_time_ms']:.2f}ms)"
        )

        # Check if all endpoints return the same data
        if len(successful_endpoints) >= 2:
            all_consistent = True
            baseline_data = results[successful_endpoints[0]]["data"].get("data", [])

            for endpoint in successful_endpoints[1:]:
                endpoint_data = results[endpoint]["data"].get("data", [])
                comparison = compare_property_data(
                    baseline_data, endpoint_data, successful_endpoints[0], endpoint
                )
                if not comparison["barmanpre_sets_match"]:
                    all_consistent = False
                    break

            if all_consistent:
                print(f"✅ All endpoints return consistent data")
                print(
                    f"🚀 RECOMMENDATION: Use '{fastest_endpoint[0]}' endpoint for production"
                )
            else:
                print(f"⚠️ Data inconsistencies detected between endpoints")
                print(
                    f"🔍 RECOMMENDATION: Investigate data differences before production"
                )


if __name__ == "__main__":
    main()
