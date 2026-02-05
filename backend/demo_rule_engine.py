"""
LanguageTool Rule Engine Demo

Demonstrates actual error detection results from LanguageTool.
"""

from pipeline.rule_engine import RuleEngine, ErrorType, Severity


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def print_errors(text: str, errors: list):
    """Print errors in a formatted way."""
    print(f"📝 Original Text: {text}")
    print(f"🔍 Errors Found: {len(errors)}")

    if not errors:
        print("✅ No errors detected!")
        return

    for i, error in enumerate(errors, 1):
        print(f"\n  Error #{i}:")
        print(f"    Type: {error.error_type.value} ({error.error_subtype or 'N/A'})")
        print(f"    Severity: {error.severity.value}")
        print(f"    Original: '{error.original_span}'")
        print(f"    Corrected: '{error.corrected_span}'")
        print(f"    Position: {error.start_index}-{error.end_index}")
        print(f"    Suggestions: {error.suggestions[:3]}")
        print(f"    Explanation: {error.explanation}")
        print(f"    Confidence: {error.confidence:.2f}")


def main():
    """Run LanguageTool demos."""
    print("=" * 80)
    print("🚀 LanguageTool Rule Engine Demo")
    print("=" * 80)

    engine = RuleEngine()

    # Test 1: Subject-Verb Agreement
    print_separator()
    print("TEST 1: Subject-Verb Agreement Error")
    print_separator()
    text1 = "She don't like pizza."
    errors1 = engine.check(text1)
    print_errors(text1, errors1)

    # Test 2: Tense Error
    print_separator()
    print("TEST 2: Tense/Agreement Error")
    print_separator()
    text2 = "He have been working here since 2020."
    errors2 = engine.check(text2)
    print_errors(text2, errors2)

    # Test 3: Article Error
    print_separator()
    print("TEST 3: Article Usage Error")
    print_separator()
    text3 = "I need a advice."
    errors3 = engine.check(text3)
    print_errors(text3, errors3)

    # Test 4: Multiple Errors
    print_separator()
    print("TEST 4: Multiple Errors")
    print_separator()
    text4 = "She dont like pizza and he dont like bananas."
    errors4 = engine.check(text4)
    print_errors(text4, errors4)

    # Test 5: Spelling Error
    print_separator()
    print("TEST 5: Spelling Errors")
    print_separator()
    text5 = "I recieved your mesage yesterday."
    errors5 = engine.check(text5)
    print_errors(text5, errors5)

    # Test 6: Correct Text
    print_separator()
    print("TEST 6: Correct Text (No Errors)")
    print_separator()
    text6 = "She likes apples and bananas."
    errors6 = engine.check(text6)
    print_errors(text6, errors6)

    # Test 7: Business Email
    print_separator()
    print("TEST 7: Business Email")
    print_separator()
    text7 = "Dear Sir, I am writing to inform you that we has received your request."
    errors7 = engine.check(text7)
    print_errors(text7, errors7)

    # Test 8: Casual Text
    print_separator()
    print("TEST 8: Casual Conversation")
    print_separator()
    text8 = "Hey! Whats up? I didnt see you yesterday."
    errors8 = engine.check(text8)
    print_errors(text8, errors8)

    # Test 9: Technical Writing
    print_separator()
    print("TEST 9: Technical Writing")
    print_separator()
    text9 = "The algorithms performs better when the datasets is larger."
    errors9 = engine.check(text9)
    print_errors(text9, errors9)

    # Test 10: Error Filtering Demo
    print_separator()
    print("TEST 10: Error Filtering Demo")
    print_separator()
    text10 = "She dont like apples and I recieved it yesterday."
    all_errors = engine.check(text10)
    print_errors(text10, all_errors)

    print("\n\n📊 Filtering by Error Type (Grammar only):")
    grammar_errors = engine.filter_errors(
        all_errors,
        error_types=[ErrorType.GRAMMAR, ErrorType.TENSE]
    )
    for error in grammar_errors:
        print(f"  - {error.error_type.value}: '{error.original_span}' → '{error.corrected_span}'")

    print("\n📊 Filtering by Error Type (Spelling only):")
    spelling_errors = engine.filter_errors(
        all_errors,
        error_types=[ErrorType.SPELLING]
    )
    for error in spelling_errors:
        print(f"  - {error.error_type.value}: '{error.original_span}' → '{error.corrected_span}'")

    print("\n📊 Filtering by Severity (HIGH only):")
    high_severity = engine.filter_errors(
        all_errors,
        min_severity=Severity.HIGH
    )
    for error in high_severity:
        print(f"  - {error.severity.value}: '{error.original_span}' → '{error.corrected_span}'")

    # Summary
    print_separator()
    print("📈 SUMMARY")
    print_separator()
    total_tests = 10
    total_errors_detected = sum([
        len(errors1), len(errors2), len(errors3), len(errors4), len(errors5),
        len(errors6), len(errors7), len(errors8), len(errors9), len(all_errors)
    ])
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Errors Detected: {total_errors_detected}")
    print(f"Average Errors per Test: {total_errors_detected / total_tests:.1f}")
    print("\n✅ Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
