# Getting Started - MapReduce with Pure Python

A quick guide to get up and running with MapReduce in 10 minutes.

## Requirements

- Python 3.8 or higher
- Text editor or IDE
- Terminal / command line

No external libraries needed. Everything runs with standard Python.

## Step 1: Understand the Framework (3 minutes)

The file `01-basics/mapreduce_framework.py` implements the 3 phases of MapReduce:

```python
from mapreduce_framework import mapreduce, print_results

# 1. MAP: Transforms data into (key, value) pairs
# 2. SHUFFLE: Groups values by key
# 3. REDUCE: Aggregates values for each key

results = mapreduce(data, mapper_function, reducer_function)
```

**Data flow:**
```
Input Data
    ↓
[MAP] → (key, value) pairs
    ↓
[SHUFFLE] → Values grouped by key
    ↓
[REDUCE] → Final result per key
```

## Step 2: Your First Example (3 minutes)

```bash
cd modules/01-mapreduce/01-pure-python/01-basics

# Run WordCount
python3 wordcount.py
```

You should see something like:
```
mapreduce: 3
the: 3
data: 2
phase: 2
...
```

## Step 3: Explore More Examples (4 minutes)

```bash
# Sales analysis
python3 examples/sales.py

# Log analysis
python3 examples/logs.py

# Average temperatures
python3 examples/temperatures.py

# Text metrics
python3 examples/word_metrics.py
```

## Step 4: Process Real Files

```bash
cd ../02-file-processing

# Process a single file
python3 wordcount_file.py ../../../../datasets/mapreduce/sample_text.txt

# Process multiple files
python3 wordcount_multifile.py ../../../../datasets/mapreduce/
```

## Step 5: Distributed Simulation

```bash
cd ../03-distributed-simulation

# Simulate HDFS
python3 simulated_hdfs.py

# Parallel processing
python3 parallel_mapreduce.py ../../../../datasets/book/The\ story\ of\ the\ universe.txt

# Complete system
python3 distributed_mapreduce.py ../../../../datasets/book/The\ story\ of\ the\ universe.txt
```

## Anatomy of a MapReduce Job

Every job needs two functions:

### Mapper
Transforms each element into (key, value) pairs:

```python
def mapper(item):
    # Process the item
    yield (key, value)
```

### Reducer
Aggregates all values for a given key:

```python
def reducer(key, values):
    # Aggregate the values
    return result
```

### Complete Example

```python
from mapreduce_framework import mapreduce, print_results

# Data
sales = [
    {'product': 'Laptop', 'amount': 1200},
    {'product': 'Mouse', 'amount': 25},
    {'product': 'Laptop', 'amount': 1100},
]

# Mapper: extract (product, amount)
def mapper(sale):
    yield (sale['product'], sale['amount'])

# Reducer: sum amounts
def reducer(product, amounts):
    return sum(amounts)

# Execute
results = mapreduce(sales, mapper, reducer)
print_results(results, "Sales by Product")
```

## Common Errors

**"ModuleNotFoundError: No module named 'mapreduce_framework'"**
→ Run from the correct directory (`01-basics/`)

**"FileNotFoundError"**
→ Check the path to your data file

**Mapper produces no results**
→ Make sure you're using `yield`, not `return`

## What's Next?

1. Complete all Level 1 examples
2. Try the exercises in [EXERCISES.md](EXERCISES.md)
3. Move on to Level 2 (file processing)
4. Explore Level 3 (distributed simulation)
5. Continue to the mrjob module (`../02-mrjob/`)

## Resources

- [README.md](README.md) - Full module documentation
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference
- [EXERCISES.md](EXERCISES.md) - Practice exercises
- Datasets: `../../../datasets/mapreduce/`
