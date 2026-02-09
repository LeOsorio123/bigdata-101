# mrjob Exercises

Practice your mrjob skills with these hands-on exercises. Start with Level 1 and progress through the levels.

## Level 1: Basic Jobs

### Exercise 1.1: Character Counter
**Difficulty**: Easy  
**Goal**: Count frequency of each character (case-insensitive)

Create `mr_char_count.py` that:
- Counts each letter (a-z only, ignore numbers and punctuation)
- Converts to lowercase
- Outputs sorted by frequency

**Test**: `python mr_char_count.py ../../../datasets/mapreduce/sample_text.txt`

**Expected output format**: `("a", 150), ("e", 200), ...`

<details>
<summary>Hint</summary>

```python
def mapper(self, _, line):
    for char in line.lower():
        if char.isalpha():
            yield (char, 1)
```
</details>

---

### Exercise 1.2: Line Length Statistics
**Difficulty**: Easy  
**Goal**: Calculate statistics about line lengths

Create `mr_line_stats.py` that outputs:
- Total lines
- Average line length
- Longest line length
- Shortest line length

**Test**: `python mr_line_stats.py ../../../datasets/book/*.txt`

<details>
<summary>Hint</summary>

Use a single key to collect all line lengths, then calculate stats in reducer:
```python
def mapper(self, _, line):
    yield ("stats", len(line))

def reducer(self, key, lengths):
    lengths_list = list(lengths)
    # Calculate min, max, avg, count
```
</details>

---

### Exercise 1.3: Email Domain Extractor
**Difficulty**: Medium  
**Goal**: Extract and count email domains

Create `mr_email_domains.py` that:
- Finds email addresses in text (pattern: `word@domain.com`)
- Extracts the domain part
- Counts emails per domain

**Test data**: Create a file with emails like:
```
Contact us at support@example.com or sales@example.com
For help, email help@company.org
```

<details>
<summary>Hint</summary>

```python
import re
EMAIL_PATTERN = r'\b[\w.-]+@([\w.-]+\.\w+)\b'

def mapper(self, _, line):
    for match in re.finditer(EMAIL_PATTERN, line):
        domain = match.group(1)
        yield (domain, 1)
```
</details>

---

## Level 2: Multi-Step Jobs

### Exercise 2.1: Word Length Average
**Difficulty**: Medium  
**Goal**: Calculate average word length for each word frequency category

Create `mr_word_length_avg.py` with two steps:
1. Count word frequencies
2. Calculate average word length for each frequency

**Output**: Words that appear once have avg length X, words that appear twice have avg length Y, etc.

<details>
<summary>Hint</summary>

Step 1: Count each word  
Step 2: Group by count and calculate average length of words with that count
</details>

---

### Exercise 2.2: Bigram Finder
**Difficulty**: Medium  
**Goal**: Find most common word pairs (bigrams)

Create `mr_bigrams.py` that:
- Extracts consecutive word pairs
- Counts their frequency
- Returns top 20 bigrams

**Example**: "the quick brown fox" → ("the quick", 1), ("quick brown", 1), ("brown fox", 1)

**Test**: `python mr_bigrams.py ../../../datasets/book/*.txt`

<details>
<summary>Hint</summary>

```python
def mapper(self, _, line):
    words = line.split()
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        yield (bigram, 1)
```
</details>

---

### Exercise 2.3: Palindrome Finder
**Difficulty**: Medium  
**Goal**: Find all palindrome words and their frequencies

Create `mr_palindromes.py` that:
- Identifies palindrome words (reads same forwards and backwards)
- Counts their occurrences
- Sorts by frequency

**Examples**: "radar", "level", "noon"

<details>
<summary>Hint</summary>

```python
def is_palindrome(word):
    return word == word[::-1] and len(word) > 2
```
</details>

---

## Level 3: Real-World Applications

### Exercise 3.1: CSV Sales Report
**Difficulty**: Medium  
**Goal**: Process CSV sales data

Create `mr_csv_sales.py` that processes CSV format:
```csv
date,product,category,amount,quantity
2026-01-15,Laptop,Electronics,1200,1
2026-01-15,Mouse,Electronics,25,2
```

Calculate:
- Total revenue per category
- Average transaction amount per category
- Number of transactions per category

<details>
<summary>Hint</summary>

```python
import csv
from io import StringIO

def mapper(self, _, line):
    if line.startswith('date'):  # Skip header
        return
    reader = csv.reader(StringIO(line))
    for row in reader:
        date, product, category, amount, quantity = row
        yield (category, float(amount))
```
</details>

---

### Exercise 3.2: Error Rate Calculator
**Difficulty**: Medium  
**Goal**: Calculate error rates from logs

Create `mr_error_rate.py` that:
- Parses log files
- Calculates error rate (4xx and 5xx) per endpoint
- Identifies endpoints with >10% error rate

**Output**: `(endpoint, error_rate, total_requests)`

<details>
<summary>Hint</summary>

Emit two types of records:
```python
yield (endpoint, ('total', 1))
yield (endpoint, ('error', 1))  # if status >= 400
```

Then calculate percentage in reducer.
</details>

---

### Exercise 3.3: User Retention Analysis
**Difficulty**: Hard  
**Goal**: Calculate user retention from event data

Create `mr_retention.py` that:
- Processes user events with dates
- Identifies users active on Day 1
- Calculates how many returned on Day 7, Day 30

**Input format**:
```json
{"user_id": "U001", "date": "2026-01-01", "action": "login"}
{"user_id": "U001", "date": "2026-01-08", "action": "login"}
```

**Output**: Retention rates for Day 7 and Day 30

<details>
<summary>Hint</summary>

This requires multiple steps:
1. Collect all dates per user
2. Identify cohorts (users who started on same date)
3. Calculate retention for each cohort
</details>

---

### Exercise 3.4: Recommendation System
**Difficulty**: Hard  
**Goal**: Build simple product recommendations

Create `mr_recommendations.py` that:
- Processes purchase history
- Finds products frequently bought together
- Generates "customers who bought X also bought Y" recommendations

**Input format**:
```json
{"order_id": "O001", "user_id": "U001", "products": ["P001", "P002", "P003"]}
```

**Output**: Product pairs and their co-occurrence count

<details>
<summary>Hint</summary>

For each order, emit all product pairs:
```python
from itertools import combinations

products = ["P001", "P002", "P003"]
for pair in combinations(products, 2):
    yield (tuple(sorted(pair)), 1)
```
</details>

---

## Challenge Exercises

### Challenge 1: TF-IDF Calculator
**Difficulty**: Hard  
**Goal**: Calculate TF-IDF scores for words across documents

TF-IDF = Term Frequency × Inverse Document Frequency

This requires:
- Counting term frequency per document
- Counting document frequency per term
- Calculating final TF-IDF scores

**Use case**: Search engine ranking, document similarity

---

### Challenge 2: Graph Analysis
**Difficulty**: Hard  
**Goal**: Analyze a social network graph

**Input**: Edge list format
```
user1,user2
user1,user3
user2,user3
```

Calculate:
- Degree of each node (number of connections)
- Find nodes with highest degree (influencers)
- Count triangles (groups of 3 mutually connected users)

---

### Challenge 3: Time Series Aggregation
**Difficulty**: Hard  
**Goal**: Aggregate time series data into windows

**Input**: Timestamped metrics
```json
{"timestamp": "2026-01-15T10:30:45", "metric": "cpu", "value": 75.5}
```

Calculate:
- Average per metric per hour
- Min/max per metric per day
- Detect anomalies (values > 2 standard deviations from mean)

---

## Testing Your Solutions

### Unit Testing Pattern

```python
from io import StringIO
import sys

def test_mapper():
    job = MRWordCount()
    
    # Test mapper
    results = list(job.mapper(None, "hello world hello"))
    assert ("hello", 1) in results
    assert ("world", 1) in results
    assert len(results) == 3

def test_reducer():
    job = MRWordCount()
    
    # Test reducer
    results = list(job.reducer("hello", [1, 1, 1]))
    assert results == [("hello", 3)]
```

### Integration Testing

```bash
# Create test input
echo "test data" > test_input.txt

# Run job
python my_job.py test_input.txt > output.txt

# Verify output
cat output.txt
```

## Submission Guidelines

For each exercise:
1. Create the Python file with proper documentation
2. Test with provided datasets
3. Include example output in comments
4. Handle edge cases (empty input, malformed data)

## Solutions

Solutions are available in the `solutions/` directory, but try to solve them yourself first!

## Getting Help

- Review the examples in `01-basics/`, `02-multistep/`, and `03-applications/`
- Check the [mrjob documentation](https://mrjob.readthedocs.io/)
- Use verbose mode for debugging: `python my_job.py -v input.txt`
- Print to stderr for debugging: `sys.stderr.write(f"Debug: {value}\n")`

Good luck! 🚀
