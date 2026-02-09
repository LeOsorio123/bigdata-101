# Getting Started with mrjob

Welcome! This guide will get you up and running with mrjob in 15 minutes.

## What You'll Learn

- Install mrjob (Python 3.8 - 3.12 required)
- Run your first MapReduce job
- Understand the basic structure
- Process real files

> **Note**: mrjob requires Python 3.8 - 3.12. It's not compatible with Python 3.13+ due to the removed `pipes` module.

## Step 1: Installation (2 minutes)

```bash
# Navigate to the module directory
cd modules/01-mapreduce/02-mrjob

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import mrjob; print('mrjob installed successfully!')"
```

If you get any errors, see [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting.

## Step 2: Your First Job (5 minutes)

Let's create a simple word counter. Create a file called `my_first_job.py`:

```python
from mrjob.job import MRJob

class MRWordCount(MRJob):
    
    def mapper(self, _, line):
        # Split line into words and count each one
        for word in line.split():
            yield word.lower(), 1
    
    def reducer(self, word, counts):
        # Sum up the counts for each word
        yield word, sum(counts)

if __name__ == '__main__':
    MRWordCount.run()
```

**What's happening here?**
- `mapper`: Takes each line, splits it into words, and emits `(word, 1)` for each word
- `reducer`: Takes all counts for each word and sums them up
- `MRWordCount.run()`: Required to make the job executable

## Step 3: Create Test Data (1 minute)

```bash
# Create a test file
cat > test.txt << 'EOF'
MapReduce is powerful
MapReduce is scalable
Python makes MapReduce easy
EOF
```

## Step 4: Run Your Job (2 minutes)

```bash
# Run the job
python my_first_job.py test.txt
```

**Expected output:**
```
"easy"	1
"is"	2
"makes"	1
"mapreduce"	3
"powerful"	1
"python"	1
"scalable"	1
```

🎉 **Congratulations!** You just ran your first MapReduce job!

## Step 5: Try Different Runners (3 minutes)

mrjob can run in different modes:

```bash
# Inline runner (default) - single process
python my_first_job.py test.txt

# Local runner - simulates Hadoop with multiple processes
python my_first_job.py -r local test.txt

# Verbose mode - see what's happening
python my_first_job.py -v test.txt
```

## Step 6: Process Real Data (2 minutes)

Let's process a real file from the datasets:

```bash
# Navigate to the mrjob directory
cd modules/01-mapreduce/02-mrjob/01-basics

# Run word count on sample text
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt

# Process multiple files
python mr_word_count.py ../../../datasets/mapreduce/*.txt

# Process a book
python mr_word_count.py ../../../datasets/book/*.txt
```

## Understanding the Output

mrjob outputs tab-separated key-value pairs:

```
"word"	count
"hello"	5
"world"	3
```

To save to a file:

```bash
python my_first_job.py test.txt > output.txt
```

## What's Next?

Now that you've run your first job, here's your learning path:

### 1. Learn the Basics (30 minutes)
Go to [`01-basics/`](01-basics/) and run all examples:

```bash
cd 01-basics

# Word count
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt

# Multi-metric counting
python mr_word_frequency.py ../../../datasets/mapreduce/sample_text.txt

# Temperature analysis
python mr_temperature.py temperatures.json
```

Read [`01-basics/README.md`](01-basics/README.md) for detailed explanations.

### 2. Multi-Step Jobs (30 minutes)
Go to [`02-multistep/`](02-multistep/) to learn advanced patterns:

```bash
cd 02-multistep

# Find most common word
python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt

# Top 10 words
python mr_top_words.py ../../../datasets/book/*.txt

# Word length distribution
python mr_word_length_distribution.py ../../../datasets/book/*.txt
```

Read [`02-multistep/README.md`](02-multistep/README.md) for multi-step patterns.

### 3. Real-World Applications (1 hour)
Go to [`03-applications/`](03-applications/) for practical examples:

```bash
cd 03-applications

# Analyze server logs
python mr_log_analyzer.py sample_logs.txt

# Sales analytics
python mr_sales_analytics.py sales_data.json

# Build search index
python mr_inverted_index.py ../../../datasets/mapreduce/*.txt
```

Read [`03-applications/README.md`](03-applications/README.md) for real-world patterns.

### 4. Practice with Exercises
Try the exercises in [`EXERCISES.md`](EXERCISES.md) to solidify your knowledge.

## Quick Tips

### Debugging
```bash
# Verbose output
python my_job.py -v input.txt

# Keep temp files for inspection
python my_job.py --no-cleanup input.txt
```

### Common Issues

**Problem**: No output
- Check that you're using `yield`, not `return`
- Make sure `MRWordCount.run()` is called

**Problem**: "ModuleNotFoundError"
- Install mrjob: `pip install mrjob`
- Check you're in the right Python environment

**Problem**: Job is slow
- Use inline runner for testing (default)
- Local runner simulates Hadoop overhead

## Comparison with Pure Python

You've already learned MapReduce with pure Python. Here's how mrjob compares:

| Pure Python | mrjob |
|-------------|-------|
| Functions | Class methods |
| In-memory lists | File streaming |
| Direct calls | Command-line execution |
| Single machine only | Can scale to clusters |

**Key difference**: mrjob is Hadoop-compatible, so the same code can run on your laptop or a 1000-node cluster!

## Resources

- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Common patterns and commands
- **Installation Help**: [INSTALLATION.md](INSTALLATION.md) - Detailed setup guide
- **Exercises**: [EXERCISES.md](EXERCISES.md) - Practice problems
- **Official Docs**: https://mrjob.readthedocs.io/

## Need Help?

1. Check the README files in each directory
2. Look at the example code - it's heavily commented
3. Use verbose mode: `python job.py -v input.txt`
4. Review [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common patterns

## Next Steps Checklist

- [ ] Install mrjob
- [ ] Run your first job
- [ ] Complete all examples in `01-basics/`
- [ ] Try multi-step jobs in `02-multistep/`
- [ ] Build real applications in `03-applications/`
- [ ] Complete exercises in `EXERCISES.md`
- [ ] Read about deploying to Hadoop/cloud

Happy MapReducing! 🚀

---

**Time to complete this guide**: ~15 minutes  
**Time to master mrjob**: ~3-4 hours (with all examples and exercises)
