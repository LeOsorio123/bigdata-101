# Pure Python MapReduce - Quick Reference

## Basic Framework

```python
from mapreduce_framework import mapreduce, print_results

results = mapreduce(data, mapper, reducer)
print_results(results, "Title", limit=10)
```

## Mapper Template

```python
def mapper(item):
    """Transforms an item into (key, value) pairs."""
    yield (key, value)
```

## Reducer Template

```python
def reducer(key, values):
    """Aggregates values for a key."""
    return result
```

## Common Patterns

### Count Occurrences
```python
def mapper(line):
    for word in line.split():
        yield (word, 1)

def reducer(key, values):
    return sum(values)
```

### Sum Values
```python
def mapper(record):
    yield (record['category'], record['amount'])

def reducer(key, values):
    return sum(values)
```

### Calculate Average
```python
def mapper(record):
    yield (record['city'], record['temperature'])

def reducer(key, values):
    return sum(values) / len(values)
```

### Find Maximum
```python
def mapper(record):
    yield (record['category'], record['value'])

def reducer(key, values):
    return max(values)
```

### Find Minimum
```python
def mapper(record):
    yield (record['category'], record['value'])

def reducer(key, values):
    return min(values)
```

### Count Unique Values
```python
def mapper(record):
    yield (record['category'], record['item'])

def reducer(key, values):
    return len(set(values))
```

### Multiple Metrics
```python
def mapper(record):
    yield ("total", record['amount'])
    yield ("count", 1)

def reducer(key, values):
    return sum(values)
```

### Full Statistics
```python
def mapper(record):
    yield (record['category'], record['value'])

def reducer(key, values):
    return {
        'count': len(values),
        'sum': sum(values),
        'avg': sum(values) / len(values),
        'min': min(values),
        'max': max(values)
    }
```

### Group and List
```python
def mapper(record):
    yield (record['department'], record['employee'])

def reducer(key, values):
    return list(set(values))
```

### Filter in Mapper
```python
def mapper(record):
    if record['status'] == 'ERROR':
        yield (record['source'], 1)
```

## File Reading

### Single File
```python
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

lines = read_file("data.txt")
results = mapreduce(lines, mapper, reducer)
```

### Multiple Files
```python
import os

def read_files(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append((filename, line.strip()))
    return data
```

## Running Examples

```bash
# Level 1: Basics
cd 01-basics
python3 wordcount.py
python3 examples/sales.py
python3 examples/logs.py
python3 examples/temperatures.py
python3 examples/word_metrics.py

# Level 2: File Processing
cd ../02-file-processing
python3 wordcount_file.py ../../../../datasets/mapreduce/sample_text.txt
python3 wordcount_multifile.py ../../../../datasets/mapreduce/

# Level 3: Distributed Simulation
cd ../03-distributed-simulation
python3 simulated_hdfs.py
python3 parallel_mapreduce.py ../../../../datasets/book/*.txt
python3 distributed_mapreduce.py ../../../../datasets/book/*.txt
```

## Key Differences

| Concept | Mapper | Reducer |
|---------|--------|---------|
| Input | One data item | One key + list of values |
| Output | `yield (key, value)` | `return result` |
| Cardinality | Can emit 0, 1, or N pairs | Returns exactly 1 result |
| Purpose | Transform and classify | Aggregate and summarize |

## MapReduce Phases

```
Data → [MAP] → (k,v) pairs → [SHUFFLE] → Groups {k: [v1,v2,...]} → [REDUCE] → Results
```

**Map**: Transforms each item into (key, value) pairs
**Shuffle**: Groups all values with the same key
**Reduce**: Processes each group to produce the final result

## Common Mistakes

### ❌ Using return in mapper
```python
def mapper(item):
    return (key, value)  # Won't work!
```

### ✅ Using yield in mapper
```python
def mapper(item):
    yield (key, value)  # Correct
```

### ❌ Yield in reducer
```python
def reducer(key, values):
    yield sum(values)  # Not needed
```

### ✅ Return in reducer
```python
def reducer(key, values):
    return sum(values)  # Correct
```

### ❌ Division by zero in average
```python
def reducer(key, values):
    return sum(values) / len(values)  # What if values is empty?
```

### ✅ Check before dividing
```python
def reducer(key, values):
    if not values:
        return 0
    return sum(values) / len(values)
```

## Debugging Tips

```python
# Print mapper output
for item in data:
    for pair in mapper(item):
        print(f"Mapper: {pair}")

# Verify shuffle manually
from collections import defaultdict
shuffled = defaultdict(list)
for item in data:
    for key, value in mapper(item):
        shuffled[key].append(value)
print(f"Shuffle: {dict(shuffled)}")

# Test reducer in isolation
result = reducer("test_key", [1, 2, 3])
print(f"Reducer: {result}")
```
