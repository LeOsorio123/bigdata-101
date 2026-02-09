# MapReduce with Pure Python

## Overview

Learn MapReduce from the ground up with pure Python implementations. This module is organized in three progressive levels, each building on the previous one.

## Quick Links

- **New here?** Start with [GETTING_STARTED.md](GETTING_STARTED.md)
- **Need syntax help?** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Want to practice?** Try [EXERCISES.md](EXERCISES.md)
- **Teaching this?** Read [INSTRUCTOR_NOTES.md](INSTRUCTOR_NOTES.md)

## Prerequisites

- Python 3.8 or higher
- Basic understanding of Python (functions, lists, dictionaries)
- Text editor or IDE
- Terminal/command line access

## Learning Path

### Level 1: Basics (`01-basics/`)
**Goal**: Understand core MapReduce concepts with simple examples

**Time**: 20-30 minutes

Start here to learn the fundamentals:
- [`mapreduce_framework.py`](01-basics/mapreduce_framework.py) - Core MapReduce implementation
- [`wordcount.py`](01-basics/wordcount.py) - Classic WordCount with inline data
- [`examples/sales.py`](01-basics/examples/sales.py) - Business data analysis
- [`examples/logs.py`](01-basics/examples/logs.py) - Log file analysis
- [`examples/temperatures.py`](01-basics/examples/temperatures.py) - Average temperature by city
- [`examples/word_metrics.py`](01-basics/examples/word_metrics.py) - Multi-metric text analysis

**What you'll learn**: Map function, Reduce function, Shuffle/Sort phase

**Exercises**:
1. Run each example and understand the output
2. Modify the mapper in `wordcount.py` to count only words longer than 5 characters
3. Create a new example that calculates average sales per product (hint: modify the reducer)
4. See [EXERCISES.md](EXERCISES.md) for more structured exercises with hints and solutions

```bash
cd 01-basics
python3 wordcount.py
python3 examples/sales.py
python3 examples/logs.py
python3 examples/temperatures.py
python3 examples/word_metrics.py
```

---

### Level 2: File Processing (`02-file-processing/`)
**Goal**: Process real files and handle multiple data sources

**Time**: 15-20 minutes

Learn to work with actual files:
- [`wordcount_file.py`](02-file-processing/wordcount_file.py) - Process single text file
- [`wordcount_multifile.py`](02-file-processing/wordcount_multifile.py) - Process multiple files

**What you'll learn**: File I/O, batch processing, aggregating multiple sources

**Exercises**:
1. Process the sample datasets
2. Create your own text file and process it
3. Modify `wordcount_multifile.py` to show which file has the most unique words

```bash
cd 02-file-processing

# Process single file
python3 wordcount_file.py ../../../../datasets/mapreduce/sample_text.txt

# Process all files in datasets directory
python3 wordcount_multifile.py ../../../../datasets/mapreduce/

# Create and process your own file
echo "Your custom text here for MapReduce processing" > mytest.txt
python3 wordcount_file.py mytest.txt
```

---

### Level 3: Distributed Simulation (`03-distributed-simulation/`)
**Goal**: Understand distributed systems and parallel processing

**Time**: 30-40 minutes

Simulate Hadoop-style distributed processing:
- [`simulated_hdfs.py`](03-distributed-simulation/simulated_hdfs.py) - HDFS simulation (blocks, replication)
- [`parallel_mapreduce.py`](03-distributed-simulation/parallel_mapreduce.py) - Parallel Map and Reduce tasks
- [`distributed_mapreduce.py`](03-distributed-simulation/distributed_mapreduce.py) - Complete distributed system

**What you'll learn**: Data blocks, replication, parallel processing, data locality

**Exercises**:
1. Run each simulation and observe the output
2. Change block size in `simulated_hdfs.py` to 256 bytes and see how it affects block count
3. Modify `parallel_mapreduce.py` to use 8 mappers and 4 reducers, compare execution times
4. Examine the `hdfs_storage` directory created by the simulations

```bash
cd 03-distributed-simulation

# 1. HDFS simulation - see how files are split into blocks
python3 simulated_hdfs.py
# Look at the created hdfs_storage directory to see blocks

# 2. Parallel processing - see real multiprocessing in action
python3 parallel_mapreduce.py
# Note the execution times for each phase

# 3. Complete system - HDFS + Parallel MapReduce
python3 distributed_mapreduce.py
# This combines everything you've learned
```

---

## Complete Learning Guide

### Day 1: Fundamentals (1-2 hours)

**Step 1**: Read and understand the framework
```bash
cd 01-basics
# Open mapreduce_framework.py in your editor
# Read the code and comments carefully
```

**Step 2**: Run basic examples
```bash
python3 wordcount.py
# Observe: input text → map phase → shuffle → reduce → results
```

**Step 3**: Experiment with modifications
- Change the text in `wordcount.py`
- Add more products in `sales.py`
- Add different log levels in `logs.py`

**Step 4**: Complete exercises
- Try the exercises listed in Level 1 above

### Day 2: File Processing (1 hour)

**Step 1**: Process sample files
```bash
cd ../02-file-processing
python3 wordcount_file.py ../../../../datasets/mapreduce/sample_text.txt
```

**Step 2**: Create your own dataset
```bash
# Create a file about your favorite topic
echo "MapReduce is powerful for Big Data processing" > topic.txt
echo "Big Data requires distributed computing systems" >> topic.txt
python3 wordcount_file.py topic.txt
```

**Step 3**: Process multiple files
```bash
python3 wordcount_multifile.py ../../../../datasets/mapreduce/
```

### Day 3: Distributed Systems (1-2 hours)

**Step 1**: Understand HDFS
```bash
cd ../03-distributed-simulation
python3 simulated_hdfs.py

# Explore the created directory structure
ls -la hdfs_storage/
ls -la hdfs_storage/node_0/
ls -la hdfs_storage/node_1/
ls -la hdfs_storage/node_2/
```

**Step 2**: See parallel processing
```bash
python3 parallel_mapreduce.py
# Pay attention to:
# - How data is split across map tasks
# - Execution time for each phase
# - How keys are partitioned for reduce tasks
```

**Step 3**: Run the complete system
```bash
python3 distributed_mapreduce.py
# This shows the full workflow:
# 1. Upload to HDFS (blocks created)
# 2. Read blocks from nodes
# 3. Parallel map processing
# 4. Shuffle and sort
# 5. Parallel reduce processing
```

## Key Concepts to Master

### Map Phase
- Takes input data
- Transforms into (key, value) pairs
- Example: `"hello world"` → `[("hello", 1), ("world", 1)]`

### Shuffle/Sort Phase
- Groups values by key
- Example: `[("hello", 1), ("hello", 1)]` → `{"hello": [1, 1]}`

### Reduce Phase
- Aggregates values for each key
- Example: `{"hello": [1, 1]}` → `{"hello": 2}`

### Parallelism
- Multiple map tasks process different data chunks simultaneously
- Multiple reduce tasks process different key partitions simultaneously
- Speeds up processing of large datasets

### Data Locality
- Process data where it's stored (avoid network transfer)
- HDFS replicates blocks across nodes
- Map tasks run on nodes that have the data

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'mapreduce_framework'`
- **Solution**: Make sure you're running scripts from the correct directory

**Problem**: `FileNotFoundError` when processing files
- **Solution**: Check the path to your data files, use absolute paths if needed

**Problem**: Multiprocessing seems slow
- **Solution**: This is normal for small datasets. Parallel processing shines with large data (10,000+ records)

**Problem**: `hdfs_storage` directory already exists
- **Solution**: Delete it before running again: `rm -rf hdfs_storage sample_data`

## Self-Assessment Questions

After completing this module, you should be able to answer:

1. What are the three main phases of MapReduce?
2. Why is the shuffle/sort phase necessary?
3. How does HDFS provide fault tolerance?
4. What is data locality and why is it important?
5. When would you use more map tasks vs more reduce tasks?
6. How does block size affect the number of map tasks?

## Next Steps

After mastering pure Python MapReduce:
1. **`../02-mrjob/`** - Write Hadoop-compatible MapReduce code that runs on real clusters
2. **`../03-pyspark/`** - Use Apache Spark for production-ready Big Data processing

## Additional Challenges

**Challenge 1**: Word Length Analysis
- Create a MapReduce job that counts words by length (1-letter words, 2-letter words, etc.)

**Challenge 2**: Top-K Words
- Modify the reducer to return only the top 10 most frequent words

**Challenge 3**: Inverted Index
- Create a MapReduce job that builds an inverted index (word → list of files containing it)

**Challenge 4**: Performance Comparison
- Compare execution time of sequential vs parallel processing with different dataset sizes

## Resources

- Sample datasets: `../../../../datasets/mapreduce/`
- Create your own datasets for practice
- Experiment with different mapper and reducer functions
- Try processing different types of data (CSV, JSON, logs)
