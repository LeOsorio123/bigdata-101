# Level 1: mrjob Basics

## Overview

Learn the fundamental syntax and structure of mrjob by converting the examples you already know from pure Python.

## Files

### Core Examples

1. **[`mr_word_count.py`](mr_word_count.py)** - Classic WordCount
   - Your first mrjob program
   - Counts word frequency in text files
   - Shows basic mapper/reducer structure
   - Run: `python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt`

2. **[`mr_word_frequency.py`](mr_word_frequency.py)** - Multi-metric counting
   - Counts characters, words, and lines simultaneously
   - Shows how to emit multiple key types
   - Run: `python mr_word_frequency.py ../../../datasets/mapreduce/sample_text.txt`

3. **[`mr_temperature.py`](mr_temperature.py)** - Average temperature by city
   - Solves the exercise from pure Python module
   - Shows handling structured data (JSON)
   - Demonstrates average calculation in MapReduce
   - Run: `python mr_temperature.py temperatures.json`

## Key Concepts

### MRJob Class Structure

Every mrjob program follows this pattern:

```python
from mrjob.job import MRJob

class MyJob(MRJob):
    
    def mapper(self, _, line):
        # Process input line
        yield key, value
    
    def reducer(self, key, values):
        # Aggregate values
        yield key, result

if __name__ == '__main__':
    MyJob.run()  # REQUIRED!
```

### Mapper Method

```python
def mapper(self, key, value):
    # key: usually None or line number (ignored)
    # value: one line of input text
    
    # Process the line
    # Yield as many (key, value) pairs as needed
    yield new_key, new_value
```

### Reducer Method

```python
def reducer(self, key, values):
    # key: a key from mapper output
    # values: iterator of all values for this key
    
    # Aggregate the values
    # Yield final (key, result) pairs
    yield key, aggregated_result
```

### Running Jobs

```bash
# Basic run (inline runner - single process)
python my_job.py input.txt

# Output to file
python my_job.py input.txt > output.txt

# Multiple input files
python my_job.py file1.txt file2.txt file3.txt

# Using wildcards
python my_job.py data/*.txt

# Local runner (simulates Hadoop)
python my_job.py -r local input.txt

# Verbose output (for debugging)
python my_job.py -v input.txt
```

## Comparison with Pure Python

### Pure Python Version
```python
def mapper(line):
    for word in line.split():
        yield (word, 1)

def reducer(key, values):
    return sum(values)

results = mapreduce(data, mapper, reducer)
```

### mrjob Version
```python
class MRWordCount(MRJob):
    
    def mapper(self, _, line):
        for word in line.split():
            yield (word, 1)
    
    def reducer(self, key, values):
        yield key, sum(values)

if __name__ == '__main__':
    MRWordCount.run()
```

**Key differences**:
- mrjob uses a class instead of functions
- Methods take `self` as first parameter
- Mapper receives `(key, value)` - first arg usually ignored
- Reducer must `yield` results (not `return`)
- Must call `.run()` at the end

## Try It

```bash
# 1. Word count on sample text
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt

# 2. Count metrics on a book
python mr_word_frequency.py ../../../datasets/book/*.txt

# 3. Temperature analysis
python mr_temperature.py temperatures.json

# 4. Try with local runner (simulates Hadoop)
python mr_word_count.py -r local ../../../datasets/mapreduce/sample_text.txt

# 5. Process all text files in a directory
python mr_word_count.py ../../../datasets/mapreduce/*.txt
```

## Exercises

1. **Modify mr_word_count.py**:
   - Count only words longer than 5 characters
   - Convert all words to lowercase before counting
   - Filter out common words (the, a, an, is, etc.)

2. **Create mr_line_length.py**:
   - Count how many lines have each length
   - Output: `(line_length, count)`

3. **Create mr_letter_frequency.py**:
   - Count frequency of each letter (ignore case)
   - Only count alphabetic characters

4. **Extend mr_temperature.py**:
   - Also calculate min and max temperature per city
   - Hint: Yield tuples like `(city, (temp, temp, temp))`

## Common Mistakes

1. **Forgetting the run() call**
   ```python
   # ❌ Wrong - job won't run
   if __name__ == '__main__':
       pass
   
   # ✅ Correct
   if __name__ == '__main__':
       MRWordCount.run()
   ```

2. **Using return instead of yield in reducer**
   ```python
   # ❌ Wrong
   def reducer(self, key, values):
       return key, sum(values)
   
   # ✅ Correct
   def reducer(self, key, values):
       yield key, sum(values)
   ```

3. **Not handling the iterator in reducer**
   ```python
   # ❌ Wrong - values is an iterator, can only be consumed once
   def reducer(self, key, values):
       count = len(values)  # This won't work!
       total = sum(values)
   
   # ✅ Correct - convert to list if you need multiple passes
   def reducer(self, key, values):
       values_list = list(values)
       count = len(values_list)
       total = sum(values_list)
   ```

## Debugging Tips

1. **Use verbose mode**: `python my_job.py -v input.txt`
2. **Test with small input first**: Create a tiny test file
3. **Print to stderr for debugging**: 
   ```python
   import sys
   sys.stderr.write(f"Debug: {variable}\n")
   ```
4. **Use inline runner**: Default runner is easiest to debug
5. **Check your input format**: Make sure your data matches what mapper expects

## Next Level

Once you're comfortable with basic mrjob syntax, move to **Level 2** to learn multi-step jobs and advanced patterns.
