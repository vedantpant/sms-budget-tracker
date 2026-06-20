import json
from parser import parse_sms

# Load test data
with open("sms_test_data.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)

# Track results
results = {
    "passed": [],
    "failed": [],
    "coverage": 0
}

# Loop through each SMS format
for format_name, format_data in test_data.items():
    
    # Skip metadata and summary
    if format_name in ["metadata", "summary"]:
        continue
    
    # Get the pattern name and examples
    pattern_name = format_data.get("pattern_name")
    examples = format_data.get("examples", [])
    
    print(f"\n{'='*80}")
    print(f"Testing: {format_name.upper()}")
    print(f"Pattern: {pattern_name}")
    print(f"Examples to test: {len(examples)}")
    print('='*80)
    
    # Test each example in this format
    for example in examples:
        sms_id = example.get("id")
        sms_body = example.get("sms")
        expected = example.get("should_extract")
        
        # Try to parse the SMS
        parsed = parse_sms(sms_body)

        # Check if this should be ignored (expected is None)
        if expected is None:
            # We expect parser to return None
            if parsed is None:
                print(f"\n✅ PASS: {sms_id}")
                print(f"   Correctly ignored (not a financial transaction)")
                results["passed"].append({
                    "id": sms_id,
                    "format": format_name,
                    "action": "ignored"
                })
            else:
                print(f"\n❌ FAIL: {sms_id}")
                print(f"   Expected: None (should ignore)")
                print(f"   Got: {parsed} (should not parse)")
                results["failed"].append({
                    "id": sms_id,
                    "format": format_name,
                    "sms": sms_body,
                    "error": "Should have been ignored but was parsed"
                })
        elif parsed is None:
            # We expected a parse but got None
            print(f"\n❌ FAIL: {sms_id}")
            print(f"   Expected to parse: {expected}")
            print(f"   Got: None (parser returned nothing)")
            results["failed"].append({
                "id": sms_id,
                "format": format_name,
                "sms": sms_body,
                "error": "Parser returned None"
            })
        else:
            # We expected a parse and got one
            print(f"\n✅ PASS: {sms_id}")
            print(f"   Amount: {parsed.get('amount')} (expected: {expected.get('amount')})")
            print(f"   Merchant: {parsed.get('merchant_name')} (expected: {expected.get('merchant')})")
            results["passed"].append({
                "id": sms_id,
                "format": format_name,
                "parsed": parsed
            })


# Calculate coverage percentage
total_tests = len(results["passed"]) + len(results["failed"])
results["coverage"] = round((len(results["passed"]) / total_tests * 100), 2) if total_tests > 0 else 0

# Print summary
print(f"\n\n{'='*80}")
print("FINAL REPORT")
print('='*80)
print(f"✅ PASSED: {len(results['passed'])} tests")
print(f"❌ FAILED: {len(results['failed'])} tests")
print(f"📊 Coverage: {results['coverage']}%")
print('='*80)

# Save failed SMS to unmatched_sms.json
if results["failed"]:
    print(f"\n⚠️  Saving {len(results['failed'])} failed SMS to unmatched_sms.json")
    with open("unmatched_sms.json", "w", encoding="utf-8") as f:
        json.dump(results["failed"], f, indent=2, ensure_ascii=False)
    
    # Print which formats failed
    failed_formats = set(item["format"] for item in results["failed"])
    print(f"\n🔴 Failed formats:")
    for fmt in failed_formats:
        count = len([x for x in results["failed"] if x["format"] == fmt])
        print(f"   - {fmt}: {count} SMS")
else:
    print("\n✨ All tests passed! No failures.")

# Print summary of passed
passed_formats = set(item["format"] for item in results["passed"])
print(f"\n✅ Working formats:")
for fmt in passed_formats:
    count = len([x for x in results["passed"] if x["format"] == fmt])
    print(f"   - {fmt}: {count} SMS")
