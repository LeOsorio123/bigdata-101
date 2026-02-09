# Exercises - MapReduce with Pure Python

Practice your MapReduce skills with these progressive exercises.

## Level 1: Basics

### Exercise 1.1: Character Counter
**Difficulty**: Easy
**Goal**: Count the frequency of each letter (letters only, case-insensitive)

```python
text = [
    "MapReduce is a programming model",
    "for processing large data sets",
]
```

**Expected output**: `{'a': 5, 'c': 2, 'd': 3, 'e': 4, ...}`

<details>
<summary>Hint</summary>

```python
def mapper(line):
    for char in line.lower():
        if char.isalpha():
            yield (char, 1)
```
</details>

---

### Exercise 1.2: Long Words
**Difficulty**: Easy
**Goal**: Count only words longer than 5 characters

Modify WordCount to filter out short words.

**Expected output**: Only words like "mapreduce", "programming", "processes", etc.

<details>
<summary>Hint</summary>

```python
def mapper(line):
    for word in line.lower().split():
        word = word.strip('.,!?')
        if len(word) > 5:
            yield (word, 1)
```
</details>

---

### Exercise 1.3: Average Sales per Product
**Difficulty**: Easy
**Goal**: Calculate the average sale amount per product

```python
sales = [
    {'product': 'Laptop', 'amount': 1200},
    {'product': 'Mouse', 'amount': 25},
    {'product': 'Laptop', 'amount': 1100},
    {'product': 'Mouse', 'amount': 30},
    {'product': 'Laptop', 'amount': 1250},
    {'product': 'Keyboard', 'amount': 75},
    {'product': 'Keyboard', 'amount': 80},
]
```

**Expected output**:
```
Laptop: 1183.3
Mouse: 27.5
Keyboard: 77.5
```

<details>
<summary>Hint</summary>

The mapper is the same as in sales.py. Modify the reducer:
```python
def reducer(product, amounts):
    return round(sum(amounts) / len(amounts), 1)
```
</details>

---

### Exercise 1.4: Temperature Statistics
**Difficulty**: Medium
**Goal**: Calculate min, max, and average temperature per city

Use the data from `examples/temperatures.py` but modify the reducer to return a dictionary with all three metrics.

**Expected output**:
```
Medellin: {'min': 22, 'max': 24, 'avg': 23.0}
Bogota: {'min': 13, 'max': 15, 'avg': 14.0}
```

<details>
<summary>Hint</summary>

```python
def reducer(city, temperatures):
    return {
        'min': min(temperatures),
        'max': max(temperatures),
        'avg': round(sum(temperatures) / len(temperatures), 1)
    }
```
</details>

---

### Exercise 1.5: Count by Category
**Difficulty**: Medium
**Goal**: Count how many sales per category AND calculate the total

```python
sales = [
    {'product': 'Laptop', 'category': 'Electronics', 'amount': 1200},
    {'product': 'Mouse', 'category': 'Electronics', 'amount': 25},
    {'product': 'Desk', 'category': 'Furniture', 'amount': 600},
    {'product': 'Chair', 'category': 'Furniture', 'amount': 350},
    {'product': 'Monitor', 'category': 'Electronics', 'amount': 450},
]
```

**Expected output**:
```
Electronics: {'count': 3, 'total': 1675, 'avg': 558.3}
Furniture: {'count': 2, 'total': 950, 'avg': 475.0}
```

<details>
<summary>Hint</summary>

```python
def mapper(sale):
    yield (sale['category'], sale['amount'])

def reducer(category, amounts):
    return {
        'count': len(amounts),
        'total': sum(amounts),
        'avg': round(sum(amounts) / len(amounts), 1)
    }
```
</details>

---

## Level 2: File Processing

### Exercise 2.1: Word Length Distribution
**Difficulty**: Medium
**Goal**: Count how many words there are of each length

Process `datasets/mapreduce/sample_text.txt` and count how many words have 1 letter, 2 letters, 3 letters, etc.

**Expected output**:
```
1: 5 words
2: 12 words
3: 25 words
...
```

<details>
<summary>Hint</summary>

```python
def mapper(line):
    for word in line.split():
        word = word.strip('.,!?')
        if word:
            yield (len(word), 1)

def reducer(length, counts):
    return sum(counts)
```
</details>

---

### Exercise 2.2: Unique Words per File
**Difficulty**: Medium
**Goal**: Determine how many unique words each file contains

Process the `datasets/mapreduce/` directory and show how many unique words each file has.

**Expected output**:
```
sample_text.txt: 85 unique words
sample_bigdata.txt: 120 unique words
```

<details>
<summary>Hint</summary>

```python
def mapper(file_data):
    filename, line = file_data
    for word in line.lower().split():
        word = word.strip('.,!?')
        if word:
            yield (filename, word)

def reducer(filename, words):
    return len(set(words))
```
</details>

---

### Exercise 2.3: Inverted Index
**Difficulty**: Hard
**Goal**: Create an inverted index (word → list of files)

Process multiple files and for each word, list which files contain it.

**Expected output**:
```
mapreduce: [sample_text.txt, sample_bigdata.txt]
hadoop: [sample_bigdata.txt]
data: [sample_text.txt, sample_bigdata.txt]
```

<details>
<summary>Hint</summary>

```python
def mapper(file_data):
    filename, line = file_data
    for word in line.lower().split():
        word = word.strip('.,!?')
        if word:
            yield (word, filename)

def reducer(word, filenames):
    return sorted(set(filenames))
```
</details>

---

## Level 3: Advanced Challenges

### Exercise 3.1: Top-N Words
**Difficulty**: Medium
**Goal**: Find the N most frequent words

Implement a function that uses MapReduce to count words and then selects the top N.

```python
def top_n_words(text, n=10):
    results = mapreduce(text, mapper, reducer)
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return sorted_results[:n]
```

---

### Exercise 3.2: Bigram Analysis
**Difficulty**: Hard
**Goal**: Find the most common consecutive word pairs

```python
text = ["the quick brown fox", "the quick red dog"]
# Bigrams: ("the quick", 2), ("quick brown", 1), ("brown fox", 1), ...
```

<details>
<summary>Hint</summary>

```python
def mapper(line):
    words = line.lower().split()
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        yield (bigram, 1)
```
</details>

---

### Exercise 3.3: Web Session Analysis
**Difficulty**: Hard
**Goal**: Analyze user sessions from clickstream data

```python
events = [
    {'user': 'U1', 'page': '/home', 'time': '10:00'},
    {'user': 'U1', 'page': '/products', 'time': '10:02'},
    {'user': 'U2', 'page': '/home', 'time': '10:01'},
    {'user': 'U1', 'page': '/cart', 'time': '10:05'},
    {'user': 'U2', 'page': '/about', 'time': '10:03'},
]
```

Calculate per user:
- Number of pages visited
- List of unique pages

<details>
<summary>Hint</summary>

```python
def mapper(event):
    yield (event['user'], event['page'])

def reducer(user, pages):
    return {
        'page_views': len(pages),
        'unique_pages': list(set(pages))
    }
```
</details>

---

### Exercise 3.4: Anomaly Detector
**Difficulty**: Hard
**Goal**: Detect outliers in sensor data

```python
readings = [
    {'sensor': 'S1', 'value': 22.5},
    {'sensor': 'S1', 'value': 23.0},
    {'sensor': 'S1', 'value': 99.9},  # ← Anomaly
    {'sensor': 'S2', 'value': 15.0},
    {'sensor': 'S2', 'value': 14.8},
]
```

For each sensor, calculate the average and flag values that are more than 2 standard deviations away.

<details>
<summary>Hint</summary>

```python
import math

def reducer(sensor, values):
    avg = sum(values) / len(values)
    variance = sum((v - avg) ** 2 for v in values) / len(values)
    std_dev = math.sqrt(variance)
    
    anomalies = [v for v in values if abs(v - avg) > 2 * std_dev]
    
    return {
        'avg': round(avg, 2),
        'std_dev': round(std_dev, 2),
        'anomalies': anomalies
    }
```
</details>

---

## Performance Exercises (Level 3)

### Exercise P.1: Sequential vs Parallel
**Difficulty**: Medium
**Goal**: Compare execution times

1. Process `datasets/book/*.txt` with the basic framework (`mapreduce_framework.py`)
2. Process the same file with `parallel_mapreduce.py`
3. Compare the times

```python
import time

start = time.time()
results = mapreduce(data, mapper, reducer)
elapsed = time.time() - start
print(f"Sequential: {elapsed:.3f}s")
```

---

### Exercise P.2: Block Size Effect
**Difficulty**: Medium
**Goal**: Observe how block size affects performance

Modify `distributed_mapreduce.py` to test with different block sizes:
- 4KB (4096 bytes)
- 16KB (16384 bytes)
- 64KB (65536 bytes)

Record: number of blocks created and total execution time.

---

## Solutions

Solutions for Level 1 exercises are available in `../../../exercises/01-mapreduce-python/`.

For the remaining exercises, try solving them on your own first. If you get stuck:
1. Review the examples in `01-basics/examples/`
2. Check the [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. Use the debugging tips from the main README

## Evaluation Criteria

For each exercise:
- ✅ Code runs without errors
- ✅ Produces the expected output
- ✅ Uses mapper and reducer correctly
- ✅ Has documentation (docstrings)
- ✅ Handles edge cases (empty data, etc.)
