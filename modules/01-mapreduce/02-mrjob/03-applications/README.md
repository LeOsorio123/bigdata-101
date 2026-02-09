# Level 3: Real-World Applications

## Overview

Apply mrjob to practical business and data analysis problems. Learn to handle complex data formats, implement business logic, and solve real-world challenges.

## Files

### Applications

1. **[`mr_log_analyzer.py`](mr_log_analyzer.py)** - Server log analysis
   - Parse Apache/Nginx log format
   - Count requests by status code, IP, and endpoint
   - Identify errors and suspicious activity
   - Run: `python mr_log_analyzer.py sample_logs.txt`

2. **[`mr_sales_analytics.py`](mr_sales_analytics.py)** - Business intelligence
   - Analyze sales data from JSON
   - Calculate revenue by product, category, and region
   - Find best-selling products
   - Run: `python mr_sales_analytics.py sales_data.json`

3. **[`mr_inverted_index.py`](mr_inverted_index.py)** - Search engine indexing
   - Build inverted index (word → list of documents)
   - Foundation for search engines
   - Shows handling of complex output structures
   - Run: `python mr_inverted_index.py ../../../datasets/mapreduce/*.txt`

4. **[`mr_session_analysis.py`](mr_session_analysis.py)** - User behavior analysis
   - Analyze user sessions from clickstream data
   - Calculate session duration and page views
   - Identify user patterns
   - Run: `python mr_session_analysis.py clickstream.json`

## Key Concepts

### Handling Different Data Formats

#### JSON Lines
```python
import json

def mapper(self, _, line):
    try:
        data = json.loads(line)
        # Process JSON data
        yield data['key'], data['value']
    except json.JSONDecodeError:
        pass  # Skip malformed lines
```

#### CSV Data
```python
import csv
from io import StringIO

def mapper(self, _, line):
    reader = csv.reader(StringIO(line))
    for row in reader:
        # Process CSV row
        yield row[0], row[1]
```

#### Log Files (Regex Parsing)
```python
import re

LOG_PATTERN = r'(\S+) - - \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+)'

def mapper(self, _, line):
    match = re.match(LOG_PATTERN, line)
    if match:
        ip, timestamp, method, path, protocol, status, size = match.groups()
        yield status, 1
```

### Complex Aggregations

#### Multiple Metrics
```python
def reducer(self, key, values):
    values_list = list(values)
    yield key, {
        'count': len(values_list),
        'sum': sum(values_list),
        'avg': sum(values_list) / len(values_list),
        'min': min(values_list),
        'max': max(values_list)
    }
```

#### Grouping and Nesting
```python
def reducer(self, category, products):
    product_list = list(products)
    yield category, {
        'products': product_list,
        'count': len(product_list),
        'total': sum(p['price'] for p in product_list)
    }
```

### Error Handling

```python
def mapper(self, _, line):
    try:
        # Parse and process data
        data = json.loads(line)
        yield data['key'], data['value']
    except json.JSONDecodeError as e:
        # Log to stderr (doesn't affect output)
        import sys
        sys.stderr.write(f"JSON error: {e}\n")
    except KeyError as e:
        # Handle missing fields
        sys.stderr.write(f"Missing field: {e}\n")
    except Exception as e:
        # Catch-all for unexpected errors
        sys.stderr.write(f"Unexpected error: {e}\n")
```

## Real-World Patterns

### Pattern 1: Log Analysis Pipeline

```python
# Step 1: Parse and filter
def mapper_parse(self, _, line):
    log_entry = parse_log(line)
    if log_entry['status'] >= 400:  # Errors only
        yield log_entry['endpoint'], 1

# Step 2: Count errors by endpoint
def reducer_count(self, endpoint, counts):
    yield None, (sum(counts), endpoint)

# Step 3: Find top error endpoints
def reducer_top_errors(self, _, endpoint_counts):
    top = sorted(endpoint_counts, reverse=True)[:10]
    for count, endpoint in top:
        yield endpoint, count
```

### Pattern 2: Business Analytics

```python
# Step 1: Extract sales by product
def mapper_sales(self, _, line):
    sale = json.loads(line)
    yield sale['product_id'], sale['amount']

# Step 2: Calculate product revenue
def reducer_revenue(self, product_id, amounts):
    total = sum(amounts)
    yield 'revenue', (total, product_id)

# Step 3: Rank products
def reducer_rank(self, _, product_revenues):
    ranked = sorted(product_revenues, reverse=True)
    for rank, (revenue, product_id) in enumerate(ranked, 1):
        yield rank, {'product': product_id, 'revenue': revenue}
```

### Pattern 3: Inverted Index

```python
# Step 1: Extract word-document pairs
def mapper_words(self, filename, line):
    for word in line.split():
        yield word.lower(), filename

# Step 2: Group documents by word
def reducer_index(self, word, filenames):
    # Remove duplicates and sort
    docs = sorted(set(filenames))
    yield word, docs
```

## Try It

```bash
cd 03-applications

# Create sample log file
cat > sample_logs.txt << 'EOF'
192.168.1.1 - - [01/Jan/2026:10:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234
192.168.1.2 - - [01/Jan/2026:10:00:01 +0000] "POST /api/login HTTP/1.1" 401 567
192.168.1.1 - - [01/Jan/2026:10:00:02 +0000] "GET /api/products HTTP/1.1" 200 2345
192.168.1.3 - - [01/Jan/2026:10:00:03 +0000] "GET /api/users HTTP/1.1" 500 123
EOF

# Analyze logs
python mr_log_analyzer.py sample_logs.txt

# Build inverted index
python mr_inverted_index.py ../../../datasets/mapreduce/*.txt

# Sales analytics (create sample data first)
python mr_sales_analytics.py sales_data.json
```

## Exercises

1. **Customer Lifetime Value**:
   - Calculate total spending per customer
   - Identify top customers
   - Segment customers by spending level

2. **A/B Test Analysis**:
   - Compare conversion rates between test groups
   - Calculate statistical significance
   - Identify winning variant

3. **Fraud Detection**:
   - Identify suspicious patterns in transaction data
   - Flag accounts with unusual activity
   - Calculate risk scores

4. **Recommendation System**:
   - Build user-item interaction matrix
   - Find similar users or items
   - Generate recommendations

## Performance Optimization

### 1. Use Combiners Effectively
```python
def combiner(self, key, values):
    # Reduce data before shuffle
    yield key, sum(values)
```

### 2. Filter Early
```python
def mapper(self, _, line):
    data = parse(line)
    if data['date'] >= '2026-01-01':  # Filter in mapper
        yield data['key'], data['value']
```

### 3. Minimize Data Transfer
```python
# ❌ Bad: Sending full records
def mapper(self, _, line):
    record = json.loads(line)
    yield record['category'], record  # Sends entire record

# ✅ Good: Send only what's needed
def mapper(self, _, line):
    record = json.loads(line)
    yield record['category'], record['amount']  # Only amount
```

### 4. Use Appropriate Data Structures
```python
# For unique values
def reducer(self, key, values):
    unique = set(values)
    yield key, len(unique)

# For counting
from collections import Counter
def reducer(self, key, values):
    counts = Counter(values)
    yield key, dict(counts)
```

## Production Considerations

### 1. Input Validation
```python
def mapper(self, _, line):
    if not line or line.startswith('#'):  # Skip empty/comments
        return
    
    try:
        data = json.loads(line)
        if 'required_field' not in data:
            return
        yield data['key'], data['value']
    except:
        return  # Skip bad data
```

### 2. Output Formatting
```python
def reducer(self, key, values):
    result = process(values)
    # Output as JSON for downstream processing
    import json
    yield key, json.dumps(result)
```

### 3. Monitoring and Logging
```python
import sys

def mapper(self, _, line):
    self.increment_counter('input', 'lines_processed', 1)
    
    try:
        # Process line
        yield key, value
        self.increment_counter('output', 'records_emitted', 1)
    except Exception as e:
        self.increment_counter('errors', 'parse_errors', 1)
        sys.stderr.write(f"Error: {e}\n")
```

## Common Challenges and Solutions

### Challenge 1: Memory Issues with Large Values
```python
# ❌ Problem: Loading all values into memory
def reducer(self, key, values):
    all_values = list(values)  # Could be huge!
    return process_all(all_values)

# ✅ Solution: Stream processing
def reducer(self, key, values):
    total = 0
    count = 0
    for value in values:  # Process one at a time
        total += value
        count += 1
    yield key, total / count
```

### Challenge 2: Skewed Data Distribution
```python
# Problem: One key has millions of values
# Solution: Use combiner and consider salting

def mapper(self, _, line):
    key, value = parse(line)
    # Add random salt to distribute load
    import random
    salt = random.randint(0, 9)
    yield f"{key}_{salt}", value

def reducer(self, salted_key, values):
    # Process partial results
    key = salted_key.rsplit('_', 1)[0]
    yield key, sum(values)
```

### Challenge 3: Complex Joins
```python
# Joining two datasets
def mapper(self, _, line):
    if line.startswith('USER:'):
        user_id, name = parse_user(line)
        yield user_id, ('user', name)
    elif line.startswith('ORDER:'):
        user_id, amount = parse_order(line)
        yield user_id, ('order', amount)

def reducer(self, user_id, records):
    user_name = None
    orders = []
    
    for record_type, data in records:
        if record_type == 'user':
            user_name = data
        else:
            orders.append(data)
    
    if user_name:
        yield user_name, sum(orders)
```

## Next Steps

After mastering mrjob applications:
1. **Deploy to Hadoop**: Run jobs on a real Hadoop cluster
2. **Cloud deployment**: Use AWS EMR or Google Dataproc
3. **Learn PySpark**: Move to `../03-pyspark/` for more advanced processing
4. **Optimize further**: Study partitioning, custom input formats, and protocols

## Resources

- [mrjob documentation](https://mrjob.readthedocs.io/)
- Sample datasets: `../../../datasets/`
- Create your own datasets for practice
- Experiment with different data formats and business logic
