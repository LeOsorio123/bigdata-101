# MapReduce with mrjob

## Overview

Learn to write Hadoop-compatible MapReduce jobs using mrjob, a Python library that lets you write MapReduce code that can run locally or on real Hadoop clusters.

## What is mrjob?

mrjob is a Python library developed by Yelp that allows you to:
- Write MapReduce jobs in pure Python
- Test locally on your machine
- Run on Hadoop clusters without code changes
- Deploy to cloud platforms (AWS EMR, Google Dataproc)

**Key advantage**: Write once, run anywhere (local → Hadoop → cloud)

## Prerequisites

- **Python 3.8 to 3.12** (mrjob is not compatible with Python 3.13+ due to removed `pipes` module)
- Completed the Pure Python module (`01-pure-python/`)
- Basic understanding of MapReduce concepts

> **Important**: If you have Python 3.13+, you'll need to install Python 3.12 or earlier. You can check your version with `python3 --version`.

## Installation

### 1. Create a virtual environment

```bash
# Navigate to the module directory
cd modules/01-mapreduce/02-mrjob

# Create the virtual environment
python3 -m venv .venv

# Activate it
# macOS / Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify the installation

```bash
python -c "import mrjob; print(f'mrjob {mrjob.__version__} installed successfully')"
```

> Remember to activate the virtual environment (`source .venv/bin/activate`) every time you open a new terminal before running the examples.

## Learning Path

### Level 1: Basics (`01-basics/`)
**Goal**: Understand mrjob syntax and run simple jobs locally

**Time**: 30-40 minutes

Learn the fundamentals:
- [`mr_word_count.py`](01-basics/mr_word_count.py) - Classic WordCount in mrjob
- [`mr_word_frequency.py`](01-basics/mr_word_frequency.py) - Count chars, words, and lines
- [`mr_temperature.py`](01-basics/mr_temperature.py) - Average temperature by city

**What you'll learn**: MRJob class structure, mapper/reducer methods, running jobs

**How to run**:
```bash
cd 01-basics

# Run with inline runner (single process, default)
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt

# Run with local runner (simulates Hadoop with multiple processes)
python mr_word_count.py -r local ../../../datasets/mapreduce/sample_text.txt

# Process multiple files
python mr_word_count.py ../../../datasets/mapreduce/*.txt
```

---

### Level 2: Multi-Step Jobs (`02-multistep/`)
**Goal**: Create complex jobs with multiple MapReduce steps

**Time**: 30-40 minutes

Learn advanced patterns:
- [`mr_most_common_word.py`](02-multistep/mr_most_common_word.py) - Find the most frequent word
- [`mr_top_words.py`](02-multistep/mr_top_words.py) - Top N most common words
- [`mr_word_length_distribution.py`](02-multistep/mr_word_length_distribution.py) - Analyze word lengths

**What you'll learn**: Multi-step jobs, combiners for optimization, secondary sorting

**How to run**:
```bash
cd 02-multistep

# Find most common word
python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt

# Get top 10 words
python mr_top_words.py ../../../datasets/mapreduce/sample_text.txt

# Analyze word length distribution
python mr_word_length_distribution.py ../../../datasets/book/*.txt
```

---

### Level 3: Real-World Applications (`03-applications/`)
**Goal**: Apply mrjob to practical business and data analysis problems

**Time**: 40-60 minutes

Practical examples:
- [`mr_log_analyzer.py`](03-applications/mr_log_analyzer.py) - Analyze server logs
- [`mr_sales_analytics.py`](03-applications/mr_sales_analytics.py) - Business intelligence
- [`mr_inverted_index.py`](03-applications/mr_inverted_index.py) - Build search index

**What you'll learn**: JSON/CSV parsing, complex data structures, real-world patterns

**How to run**:
```bash
cd 03-applications

# Analyze logs (you'll need to create sample log data)
python mr_log_analyzer.py sample_logs.txt

# Sales analytics
python mr_sales_analytics.py sales_data.json

# Build inverted index
python mr_inverted_index.py ../../../datasets/mapreduce/*.txt
```

---

## Key Differences from Pure Python

| Aspect | Pure Python | mrjob |
|--------|-------------|-------|
| **Class structure** | Functions | Class inheriting from MRJob |
| **Method names** | `mapper()`, `reducer()` | Same, but as class methods |
| **Input/Output** | In-memory lists | Files (stdin/stdout) |
| **Execution** | Direct function calls | Command-line with runners |
| **Hadoop compatibility** | No | Yes |
| **Scalability** | Single machine | Can run on clusters |

## mrjob Runners

mrjob provides different "runners" to execute your jobs:

1. **inline** (default): Single Python process, easiest debugging
2. **local**: Multiple processes, simulates Hadoop locally
3. **hadoop**: Runs on your Hadoop cluster
4. **emr**: Runs on Amazon Elastic MapReduce
5. **dataproc**: Runs on Google Cloud Dataproc

```bash
# Inline (default)
python my_job.py input.txt

# Local (simulated Hadoop)
python my_job.py -r local input.txt

# Hadoop cluster
python my_job.py -r hadoop hdfs://path/to/input.txt

# AWS EMR
python my_job.py -r emr s3://bucket/input.txt
```

## Basic Job Structure

```python
from mrjob.job import MRJob

class MyJob(MRJob):
    
    def mapper(self, _, line):
        # Process each line
        # Yield (key, value) pairs
        pass
    
    def reducer(self, key, values):
        # Aggregate values for each key
        # Yield (key, result) pairs
        pass

if __name__ == '__main__':
    MyJob.run()  # This line is REQUIRED
```

## Common Patterns

### Pattern 1: Simple Aggregation
```python
def mapper(self, _, line):
    yield "count", 1

def reducer(self, key, values):
    yield key, sum(values)
```

### Pattern 2: Grouping by Key
```python
def mapper(self, _, line):
    category, value = line.split(',')
    yield category, int(value)

def reducer(self, key, values):
    yield key, sum(values)
```

### Pattern 3: Using Combiner (Optimization)
```python
def mapper(self, _, line):
    for word in line.split():
        yield word, 1

def combiner(self, word, counts):
    # Runs on mapper nodes before shuffle
    yield word, sum(counts)

def reducer(self, word, counts):
    yield word, sum(counts)
```

## Tips and Best Practices

1. **Always include the run() call**: `if __name__ == '__main__': MyJob.run()`
2. **Test locally first**: Use inline runner before deploying to clusters
3. **Use combiners**: They reduce network traffic and improve performance
4. **Handle errors gracefully**: Bad input data will crash your job
5. **Keep state minimal**: Mappers and reducers should be stateless when possible
6. **Use protocols for complex data**: mrjob supports JSON, pickle, and custom protocols

## Debugging

```bash
# Verbose output
python my_job.py -v input.txt

# Keep temp files for inspection
python my_job.py --no-cleanup input.txt

# Step through with inline runner
python my_job.py -r inline input.txt
```

## Configuration

Create `~/.mrjob.conf` for persistent settings:

```yaml
runners:
  local:
    # Use more processes for local testing
    num_cores: 4
  emr:
    # AWS settings
    aws_region: us-west-2
    instance_type: m5.xlarge
```

## Exercises

After completing the levels, try these challenges:

1. **Word Co-occurrence**: Find which words appear together frequently
2. **User Session Analysis**: Analyze user behavior from web logs
3. **Data Quality Check**: Find missing or invalid data in large datasets
4. **Time Series Aggregation**: Aggregate metrics by time windows

## Comparison with Pure Python

You've already learned MapReduce with pure Python. Here's how mrjob compares:

**Advantages of mrjob**:
- ✅ Hadoop-compatible (can run on real clusters)
- ✅ Built-in file handling and streaming
- ✅ Multiple runner options
- ✅ Production-ready
- ✅ Handles large files efficiently

**When to use Pure Python**:
- Learning and understanding concepts
- Small datasets that fit in memory
- Quick prototyping
- No Hadoop infrastructure available

**When to use mrjob**:
- Need to scale to Hadoop/cloud
- Processing files larger than memory
- Production data pipelines
- Team already uses Hadoop ecosystem

## Next Steps

After mastering mrjob:
1. **`../03-pyspark/`** - Learn Apache Spark for even more powerful Big Data processing
2. **Deploy to cloud** - Try running your jobs on AWS EMR or Google Dataproc
3. **Optimize performance** - Learn about partitioning, combiners, and custom protocols

## Resources

- [Official mrjob documentation](https://mrjob.readthedocs.io/)
- Sample datasets: `../../../datasets/mapreduce/`
- Pure Python comparison: `../01-pure-python/`

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'mrjob'`
- **Solution**: Install mrjob: `pip install mrjob`

**Problem**: Job runs but produces no output
- **Solution**: Check that you're yielding results in both mapper and reducer

**Problem**: "No such file or directory" error
- **Solution**: Use absolute paths or run from the correct directory

**Problem**: Job is very slow with local runner
- **Solution**: This is normal - local runner simulates Hadoop overhead. Use inline for testing.
