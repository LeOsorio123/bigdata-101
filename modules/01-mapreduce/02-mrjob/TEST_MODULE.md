# Module Testing Guide

This guide helps verify that all examples in the mrjob module work correctly.

## Prerequisites

```bash
# Install mrjob
pip install mrjob

# Navigate to module directory
cd modules/01-mapreduce/02-mrjob
```

## Quick Test (5 minutes)

Run this single command to verify basic functionality:

```bash
cd 01-basics
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt
```

**Expected**: Should output word counts without errors.

## Complete Test Suite

### Level 1: Basics

```bash
cd 01-basics

# Test 1: Word Count
echo "Testing mr_word_count.py..."
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt > /tmp/test1.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# Test 2: Word Frequency
echo "Testing mr_word_frequency.py..."
python mr_word_frequency.py ../../../datasets/mapreduce/sample_text.txt > /tmp/test2.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# Test 3: Temperature
echo "Testing mr_temperature.py..."
python mr_temperature.py temperatures.json > /tmp/test3.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

cd ..
```

### Level 2: Multi-Step

```bash
cd 02-multistep

# Test 4: Most Common Word
echo "Testing mr_most_common_word.py..."
python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt > /tmp/test4.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# Test 5: Top Words
echo "Testing mr_top_words.py..."
python mr_top_words.py ../../../datasets/mapreduce/sample_text.txt > /tmp/test5.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# Test 6: Word Length Distribution
echo "Testing mr_word_length_distribution.py..."
python mr_word_length_distribution.py ../../../datasets/mapreduce/sample_text.txt > /tmp/test6.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

cd ..
```

### Level 3: Applications

```bash
cd 03-applications

# Test 7: Log Analyzer
echo "Testing mr_log_analyzer.py..."
python mr_log_analyzer.py sample_logs.txt > /tmp/test7.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# Test 8: Sales Analytics
echo "Testing mr_sales_analytics.py..."
python mr_sales_analytics.py sales_data.json > /tmp/test8.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# Test 9: Inverted Index
echo "Testing mr_inverted_index.py..."
python mr_inverted_index.py ../../../datasets/mapreduce/sample_text.txt > /tmp/test9.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

# Test 10: Session Analysis
echo "Testing mr_session_analysis.py..."
python mr_session_analysis.py clickstream.json > /tmp/test10.txt
if [ $? -eq 0 ]; then echo "✅ PASS"; else echo "❌ FAIL"; fi

cd ..
```

## Automated Test Script

Save this as `run_tests.sh`:

```bash
#!/bin/bash

echo "================================"
echo "mrjob Module Test Suite"
echo "================================"
echo ""

PASS=0
FAIL=0

# Function to run test
run_test() {
    local name=$1
    local cmd=$2
    
    echo -n "Testing $name... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo "✅ PASS"
        ((PASS++))
    else
        echo "❌ FAIL"
        ((FAIL++))
    fi
}

# Level 1 Tests
echo "Level 1: Basics"
echo "---------------"
cd 01-basics
run_test "mr_word_count" "python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt"
run_test "mr_word_frequency" "python mr_word_frequency.py ../../../datasets/mapreduce/sample_text.txt"
run_test "mr_temperature" "python mr_temperature.py temperatures.json"
cd ..
echo ""

# Level 2 Tests
echo "Level 2: Multi-Step"
echo "-------------------"
cd 02-multistep
run_test "mr_most_common_word" "python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt"
run_test "mr_top_words" "python mr_top_words.py ../../../datasets/mapreduce/sample_text.txt"
run_test "mr_word_length_distribution" "python mr_word_length_distribution.py ../../../datasets/mapreduce/sample_text.txt"
cd ..
echo ""

# Level 3 Tests
echo "Level 3: Applications"
echo "---------------------"
cd 03-applications
run_test "mr_log_analyzer" "python mr_log_analyzer.py sample_logs.txt"
run_test "mr_sales_analytics" "python mr_sales_analytics.py sales_data.json"
run_test "mr_inverted_index" "python mr_inverted_index.py ../../../datasets/mapreduce/sample_text.txt"
run_test "mr_session_analysis" "python mr_session_analysis.py clickstream.json"
cd ..
echo ""

# Summary
echo "================================"
echo "Test Summary"
echo "================================"
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Total:  $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Check the output above."
    exit 1
fi
```

Make it executable and run:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## Manual Verification

### Test Output Correctness

#### Test 1: Word Count
```bash
cd 01-basics
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt | head -5
```

**Expected**: Should show word counts like:
```
"mapreduce"	X
"data"	Y
...
```

#### Test 2: Temperature
```bash
python mr_temperature.py temperatures.json
```

**Expected**: Should show averages:
```
"Bogota"	14.0
"Cali"	29.0
"Medellin"	23.0
...
```

#### Test 3: Most Common Word
```bash
cd ../02-multistep
python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt
```

**Expected**: Should show single word with highest count:
```
COUNT	"word"
```

## Test with Different Runners

```bash
cd 01-basics

# Inline runner (default)
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt

# Local runner
python mr_word_count.py -r local ../../../datasets/mapreduce/sample_text.txt

# Both should produce same results
```

## Performance Test

Test with larger dataset:

```bash
cd 01-basics

# Time inline runner
time python mr_word_count.py ../../../datasets/book/*.txt > /tmp/inline.txt

# Time local runner
time python mr_word_count.py -r local ../../../datasets/book/*.txt > /tmp/local.txt

# Compare outputs (should be identical)
diff /tmp/inline.txt /tmp/local.txt
```

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'mrjob'"
**Solution**: 
```bash
pip install mrjob
```

### Issue: "FileNotFoundError"
**Solution**: 
```bash
# Make sure you're in the right directory
pwd
# Should be in modules/01-mapreduce/02-mrjob/
```

### Issue: No output
**Solution**: 
```bash
# Run with verbose mode to see errors
python mr_word_count.py -v input.txt
```

### Issue: "Permission denied"
**Solution**: 
```bash
# Make sure test script is executable
chmod +x run_tests.sh
```

## Continuous Integration

For automated testing in CI/CD:

```yaml
# .github/workflows/test-mrjob.yml
name: Test mrjob Module

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install mrjob
    
    - name: Run tests
      run: |
        cd modules/01-mapreduce/02-mrjob
        chmod +x run_tests.sh
        ./run_tests.sh
```

## Test Coverage

| Level | Examples | Tested | Coverage |
|-------|----------|--------|----------|
| 1 - Basics | 3 | 3 | 100% |
| 2 - Multi-Step | 3 | 3 | 100% |
| 3 - Applications | 4 | 4 | 100% |
| **Total** | **10** | **10** | **100%** |

## Regression Testing

After making changes, run full test suite:

```bash
# Quick test (1 minute)
cd 01-basics
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt

# Full test (5 minutes)
cd ..
./run_tests.sh

# Performance test (10 minutes)
# Test with large datasets
cd 01-basics
time python mr_word_count.py ../../../datasets/book/*.txt
```

## Test Checklist

Before releasing module:

- [ ] All examples run without errors
- [ ] Output is correct for each example
- [ ] Works with inline runner
- [ ] Works with local runner
- [ ] All data files present
- [ ] Documentation is accurate
- [ ] No broken links in README files
- [ ] Installation instructions work
- [ ] Examples work on fresh Python environment

## Reporting Issues

If tests fail:

1. Note which test failed
2. Run with verbose mode: `python script.py -v input.txt`
3. Check Python version: `python --version`
4. Check mrjob version: `python -c "import mrjob; print(mrjob.__version__)"`
5. Check file paths are correct
6. Report issue with full error message

---

**Last Updated**: February 2026  
**Test Suite Version**: 1.0
