# mrjob Quick Reference

## Basic Job Template

```python
from mrjob.job import MRJob

class MyJob(MRJob):
    
    def mapper(self, _, line):
        # Process each line
        yield key, value
    
    def reducer(self, key, values):
        # Aggregate values
        yield key, result

if __name__ == '__main__':
    MyJob.run()
```

## Multi-Step Job Template

```python
from mrjob.job import MRJob
from mrjob.step import MRStep

class MyMultiStepJob(MRJob):
    
    def steps(self):
        return [
            MRStep(mapper=self.mapper_1,
                   combiner=self.combiner_1,
                   reducer=self.reducer_1),
            MRStep(mapper=self.mapper_2,
                   reducer=self.reducer_2)
        ]
    
    def mapper_1(self, _, line):
        yield key, value
    
    def combiner_1(self, key, values):
        yield key, partial_result
    
    def reducer_1(self, key, values):
        yield key, result
    
    def mapper_2(self, key, value):
        yield new_key, value
    
    def reducer_2(self, key, values):
        yield key, final_result

if __name__ == '__main__':
    MyMultiStepJob.run()
```

## Command Line Usage

```bash
# Basic run
python job.py input.txt

# Specify runner
python job.py -r inline input.txt      # Single process (default)
python job.py -r local input.txt       # Multiple processes
python job.py -r hadoop input.txt      # Hadoop cluster
python job.py -r emr input.txt         # AWS EMR

# Multiple inputs
python job.py file1.txt file2.txt file3.txt
python job.py data/*.txt

# Output to file
python job.py input.txt > output.txt

# Verbose mode
python job.py -v input.txt

# Keep temp files
python job.py --no-cleanup input.txt

# Custom configuration
python job.py --conf-path my_config.conf input.txt

# Pass custom arguments
python job.py --my-arg=value input.txt
```

## Common Patterns

### Word Count
```python
def mapper(self, _, line):
    for word in line.split():
        yield word.lower(), 1

def reducer(self, word, counts):
    yield word, sum(counts)
```

### Count with Combiner
```python
def mapper(self, _, line):
    for word in line.split():
        yield word, 1

def combiner(self, word, counts):
    yield word, sum(counts)

def reducer(self, word, counts):
    yield word, sum(counts)
```

### Average Calculation
```python
def mapper(self, _, line):
    category, value = line.split(',')
    yield category, (float(value), 1)

def combiner(self, category, value_count_pairs):
    total_value = 0
    total_count = 0
    for value, count in value_count_pairs:
        total_value += value
        total_count += count
    yield category, (total_value, total_count)

def reducer(self, category, value_count_pairs):
    total_value = 0
    total_count = 0
    for value, count in value_count_pairs:
        total_value += value
        total_count += count
    yield category, total_value / total_count
```

### Find Maximum
```python
# Step 1: Count
def mapper_count(self, _, line):
    for word in line.split():
        yield word, 1

def reducer_count(self, word, counts):
    yield None, (sum(counts), word)

# Step 2: Find max
def reducer_find_max(self, _, count_word_pairs):
    yield max(count_word_pairs)
```

### Top N
```python
def reducer_top_n(self, _, count_word_pairs):
    top_n = sorted(count_word_pairs, reverse=True)[:10]
    for count, word in top_n:
        yield count, word
```

## Data Format Handling

### JSON
```python
import json

def mapper(self, _, line):
    try:
        data = json.loads(line)
        yield data['key'], data['value']
    except json.JSONDecodeError:
        pass
```

### CSV
```python
import csv
from io import StringIO

def mapper(self, _, line):
    reader = csv.reader(StringIO(line))
    for row in reader:
        yield row[0], row[1]
```

### Regex Parsing
```python
import re

PATTERN = re.compile(r'(\S+) (\d+)')

def mapper(self, _, line):
    match = PATTERN.match(line)
    if match:
        key, value = match.groups()
        yield key, int(value)
```

## Custom Arguments

```python
def configure_args(self):
    super(MyJob, self).configure_args()
    self.add_passthru_arg(
        '--my-arg',
        type=int,
        default=10,
        help='My custom argument'
    )

def mapper(self, _, line):
    # Access argument
    threshold = self.options.my_arg
    # Use it
    if value > threshold:
        yield key, value
```

## Protocols

### JSON Output
```python
from mrjob.protocol import JSONValueProtocol

class MyJob(MRJob):
    OUTPUT_PROTOCOL = JSONValueProtocol
    
    def reducer(self, key, values):
        yield key, {'count': sum(values), 'items': list(values)}
```

### JSON Input and Output
```python
from mrjob.protocol import JSONProtocol

class MyJob(MRJob):
    INPUT_PROTOCOL = JSONProtocol
    OUTPUT_PROTOCOL = JSONProtocol
```

## Counters

```python
def mapper(self, _, line):
    self.increment_counter('group', 'counter_name', 1)
    yield key, value
```

## Error Handling

```python
import sys

def mapper(self, _, line):
    try:
        # Process line
        yield key, value
    except ValueError as e:
        # Log to stderr
        sys.stderr.write(f"Error: {e}\n")
        self.increment_counter('errors', 'parse_errors', 1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        self.increment_counter('errors', 'unexpected', 1)
```

## Initialization and Cleanup

```python
def mapper_init(self):
    # Called once before mapper starts
    self.cache = {}

def mapper(self, _, line):
    # Use self.cache
    yield key, value

def mapper_final(self):
    # Called once after mapper finishes
    # Emit any remaining data
    for key, value in self.cache.items():
        yield key, value
```

## Configuration File

`~/.mrjob.conf`:

```yaml
runners:
  local:
    num_cores: 4
    local_tmp_dir: /tmp/mrjob
  
  emr:
    aws_region: us-west-2
    instance_type: m5.xlarge
    num_core_instances: 2
```

## Debugging Tips

```python
# Print to stderr (doesn't affect output)
import sys
sys.stderr.write(f"Debug: {variable}\n")

# Use verbose mode
# python job.py -v input.txt

# Keep temp files
# python job.py --no-cleanup input.txt

# Test mapper/reducer separately
if __name__ == '__main__':
    job = MyJob()
    
    # Test mapper
    for key, value in job.mapper(None, "test line"):
        print(f"Mapper output: {key} -> {value}")
    
    # Test reducer
    for key, value in job.reducer("test_key", [1, 2, 3]):
        print(f"Reducer output: {key} -> {value}")
```

## Performance Tips

1. **Use combiners** for associative operations (sum, count, min, max)
2. **Filter early** in mapper to reduce data transfer
3. **Minimize data between steps** - only pass what's needed
4. **Use appropriate data structures** (sets for unique values, Counter for counting)
5. **Avoid loading all values into memory** - stream when possible

## Common Mistakes

### ❌ Wrong: Return instead of yield
```python
def reducer(self, key, values):
    return key, sum(values)  # Wrong!
```

### ✅ Correct: Use yield
```python
def reducer(self, key, values):
    yield key, sum(values)  # Correct
```

### ❌ Wrong: Consuming iterator twice
```python
def reducer(self, key, values):
    count = len(values)  # Consumes iterator
    total = sum(values)  # Empty now!
```

### ✅ Correct: Convert to list first
```python
def reducer(self, key, values):
    values_list = list(values)
    count = len(values_list)
    total = sum(values_list)
```

### ❌ Wrong: Forgetting run() call
```python
if __name__ == '__main__':
    pass  # Job won't run!
```

### ✅ Correct: Call run()
```python
if __name__ == '__main__':
    MyJob.run()  # Required!
```

## Useful Imports

```python
from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONProtocol, JSONValueProtocol
import json
import re
import csv
from io import StringIO
from collections import Counter, defaultdict
from itertools import combinations
import sys
```

## Resources

- **Documentation**: https://mrjob.readthedocs.io/
- **GitHub**: https://github.com/Yelp/mrjob
- **Examples**: See `01-basics/`, `02-multistep/`, `03-applications/`
