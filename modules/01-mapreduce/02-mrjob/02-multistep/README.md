# Level 2: Multi-Step Jobs

## Overview

Learn to create complex MapReduce jobs with multiple steps. Many real-world problems require chaining multiple MapReduce operations together.

## Why Multiple Steps?

Some problems can't be solved in a single Map-Reduce cycle:

- **Finding the maximum**: Need to count first, then find max
- **Sorting by value**: Need to aggregate first, then sort
- **Top-N problems**: Need to count, then select top items
- **Complex transformations**: Need intermediate processing

## Files

### Examples

1. **[`mr_most_common_word.py`](mr_most_common_word.py)** - Find the single most frequent word
   - **Step 1**: Count word frequencies (like WordCount)
   - **Step 2**: Find the word with maximum count
   - Shows basic two-step pattern
   - Run: `python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt`

2. **[`mr_top_words.py`](mr_top_words.py)** - Find top N most common words
   - **Step 1**: Count word frequencies
   - **Step 2**: Sort by count and select top N
   - Shows how to pass parameters to jobs
   - Run: `python mr_top_words.py ../../../datasets/book/*.txt`

3. **[`mr_word_length_distribution.py`](mr_word_length_distribution.py)** - Analyze word length patterns
   - **Step 1**: Map words to their lengths
   - **Step 2**: Count words of each length
   - **Step 3**: Sort by length
   - Shows three-step jobs
   - Run: `python mr_word_length_distribution.py ../../../datasets/book/*.txt`

## Key Concepts

### Defining Multiple Steps

Override the `steps()` method to return a list of `MRStep` objects:

```python
from mrjob.job import MRJob
from mrjob.step import MRStep

class MyMultiStepJob(MRJob):
    
    def steps(self):
        return [
            MRStep(mapper=self.mapper_1,
                   reducer=self.reducer_1),
            MRStep(mapper=self.mapper_2,
                   reducer=self.reducer_2)
        ]
    
    def mapper_1(self, _, line):
        # First step mapper
        pass
    
    def reducer_1(self, key, values):
        # First step reducer
        pass
    
    def mapper_2(self, key, value):
        # Second step mapper
        # Note: receives output from reducer_1
        pass
    
    def reducer_2(self, key, values):
        # Second step reducer
        pass
```

### Data Flow in Multi-Step Jobs

```
Input File
    ↓
[Step 1 Mapper] → [Step 1 Reducer]
    ↓
[Step 2 Mapper] → [Step 2 Reducer]
    ↓
[Step 3 Mapper] → [Step 3 Reducer]
    ↓
Output
```

**Important**: The output of one step becomes the input to the next step!

### Using Combiners

Combiners optimize performance by doing partial aggregation on mapper nodes:

```python
def steps(self):
    return [
        MRStep(mapper=self.mapper,
               combiner=self.combiner,  # Runs on mapper nodes
               reducer=self.reducer)
    ]

def combiner(self, key, values):
    # Partial aggregation (same logic as reducer often)
    yield key, sum(values)
```

**When to use combiners**:
- ✅ Associative operations (sum, count, min, max)
- ✅ When reducer logic can be applied partially
- ✅ To reduce network traffic
- ❌ Not for operations requiring all values (average, median)

## Common Multi-Step Patterns

### Pattern 1: Count then Find Max

```python
def steps(self):
    return [
        MRStep(mapper=self.mapper_count,
               reducer=self.reducer_count),
        MRStep(reducer=self.reducer_find_max)
    ]

def mapper_count(self, _, line):
    for word in line.split():
        yield word, 1

def reducer_count(self, word, counts):
    yield None, (sum(counts), word)  # Emit to same key

def reducer_find_max(self, _, word_count_pairs):
    yield max(word_count_pairs)  # Find maximum
```

### Pattern 2: Count then Sort

```python
def steps(self):
    return [
        MRStep(mapper=self.mapper_count,
               reducer=self.reducer_count),
        MRStep(mapper=self.mapper_swap,
               reducer=self.reducer_identity)
    ]

def reducer_count(self, word, counts):
    yield word, sum(counts)

def mapper_swap(self, word, count):
    # Swap key and value to sort by count
    yield count, word

def reducer_identity(self, count, words):
    for word in words:
        yield count, word
```

### Pattern 3: Filter then Aggregate

```python
def steps(self):
    return [
        MRStep(mapper=self.mapper_filter,
               reducer=self.reducer_aggregate),
        MRStep(reducer=self.reducer_summarize)
    ]
```

## Try It

```bash
cd 02-multistep

# Find most common word
python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt

# Get top 10 words
python mr_top_words.py ../../../datasets/book/*.txt

# Analyze word lengths
python mr_word_length_distribution.py ../../../datasets/book/*.txt

# Use local runner for larger files
python mr_top_words.py -r local ../../../datasets/book/*.txt

# Verbose mode to see each step
python mr_most_common_word.py -v ../../../datasets/mapreduce/sample_text.txt
```

## Exercises

1. **Top N by Category**:
   - Create a job that finds top 5 products by sales in each category
   - Hint: Use category as key in final step

2. **Word Pairs**:
   - Find the most common word pairs (bigrams)
   - Step 1: Extract pairs, Step 2: Count, Step 3: Find top pairs

3. **Average of Averages**:
   - Calculate average temperature by city, then overall average
   - Step 1: City averages, Step 2: Overall average

4. **Percentile Calculation**:
   - Find the 90th percentile word length
   - Step 1: Count lengths, Step 2: Calculate percentile

## Debugging Multi-Step Jobs

1. **Test each step independently**: Comment out later steps first
2. **Use verbose mode**: `python my_job.py -v input.txt`
3. **Check intermediate output**: Use `--no-cleanup` to inspect temp files
4. **Print to stderr**: Debug without affecting output
   ```python
   import sys
   sys.stderr.write(f"Debug step 2: {key} = {value}\n")
   ```

## Performance Tips

1. **Use combiners**: Reduce data shuffled between steps
2. **Minimize data between steps**: Only pass what's needed
3. **Consider step order**: Sometimes reordering steps improves performance
4. **Avoid unnecessary steps**: Can you solve it in fewer steps?

## Common Mistakes

1. **Wrong data format between steps**:
   ```python
   # ❌ Step 1 outputs (word, count)
   # ❌ Step 2 expects (count, word)
   # Solution: Add mapper to transform between steps
   ```

2. **Forgetting that values is an iterator**:
   ```python
   # ❌ Can't iterate twice
   def reducer(self, key, values):
       count = len(values)  # Consumes iterator
       total = sum(values)  # Empty now!
   
   # ✅ Convert to list first
   def reducer(self, key, values):
       values_list = list(values)
       count = len(values_list)
       total = sum(values_list)
   ```

3. **Using combiner for non-associative operations**:
   ```python
   # ❌ Average doesn't work with combiner
   def combiner(self, key, values):
       vals = list(values)
       yield key, sum(vals) / len(vals)  # Wrong!
   
   # ✅ Pass (sum, count) tuples instead
   def mapper(self, _, line):
       yield key, (value, 1)
   
   def combiner(self, key, value_count_pairs):
       pairs = list(value_count_pairs)
       total_sum = sum(v for v, c in pairs)
       total_count = sum(c for v, c in pairs)
       yield key, (total_sum, total_count)
   ```

## Next Level

Once you're comfortable with multi-step jobs, move to **Level 3** to see real-world applications with complex data formats and business logic.
