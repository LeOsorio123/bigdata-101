# Level 1: MapReduce Basics

## Overview

Learn the fundamental concepts of MapReduce with simple, self-contained examples.

## Files

### Core Framework
- **[`mapreduce_framework.py`](mapreduce_framework.py)** - The foundation
  - Implements the complete MapReduce workflow
  - Map phase: Transform data into key-value pairs
  - Shuffle/Sort phase: Group values by key
  - Reduce phase: Aggregate values for each key
  - Utility functions for displaying results

### Examples

1. **[`wordcount.py`](wordcount.py)** - The "Hello World" of MapReduce
   - Counts word frequency in text
   - Data is inline (no files needed)
   - Perfect first example to understand the flow
   - Run: `python wordcount.py`

2. **[`examples/sales.py`](examples/sales.py)** - Business Analytics
   - Analyzes sales data by product
   - Works with structured data (dictionaries)
   - Shows MapReduce for business use cases
   - Run: `python examples/sales.py`

3. **[`examples/logs.py`](examples/logs.py)** - System Monitoring
   - Counts log entries by severity level
   - Common real-world application
   - Demonstrates filtering and counting
   - Run: `python examples/logs.py`

4. **[`examples/temperatures.py`](examples/temperatures.py)** - Average Calculation
   - Calculates average temperature by city
   - Shows a reducer that computes averages (not just sums)
   - Works with structured data (dictionaries)
   - Run: `python examples/temperatures.py`

5. **[`examples/word_metrics.py`](examples/word_metrics.py)** - Multi-Metric Analysis
   - Counts chars, words, lines, and longest word simultaneously
   - Shows how to emit multiple key types from one mapper
   - Demonstrates different aggregation strategies per key
   - Run: `python examples/word_metrics.py`

## Key Concepts

**Map Function**
- Takes input data
- Emits (key, value) pairs
- Example: `("apple", 1)` for each word

**Shuffle/Sort**
- Groups all values with the same key
- Example: `"apple" -> [1, 1, 1]`

**Reduce Function**
- Aggregates values for each key
- Example: `sum([1, 1, 1]) = 3`

## Try It

```bash
# Run all examples
python wordcount.py
python examples/sales.py
python examples/logs.py
python examples/temperatures.py
python examples/word_metrics.py
```

## Next Level

Once comfortable with these basics, move to **Level 2** to learn file processing.
