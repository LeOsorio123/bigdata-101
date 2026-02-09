# mrjob Module - Complete Index

## 📚 Start Here

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Quick 15-minute introduction | 15 min | Everyone |
| [README.md](README.md) | Complete module overview | 10 min | Everyone |
| [MODULE_SUMMARY.md](MODULE_SUMMARY.md) | Detailed summary and statistics | 5 min | Instructors |

## 🔧 Setup & Reference

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Installation and troubleshooting | Before starting |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Cheat sheet for common patterns | While coding |
| [EXERCISES.md](EXERCISES.md) | Practice problems | After each level |

## 📖 Learning Levels

### Level 1: Basics (30-40 minutes)
**Directory**: `01-basics/`

| File | Description | Concepts | Run Command |
|------|-------------|----------|-------------|
| [README.md](01-basics/README.md) | Level overview and concepts | MRJob structure, runners | - |
| [mr_word_count.py](01-basics/mr_word_count.py) | Classic word frequency counter | Basic mapper/reducer | `python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt` |
| [mr_word_frequency.py](01-basics/mr_word_frequency.py) | Count chars, words, lines | Multiple key types | `python mr_word_frequency.py ../../../datasets/mapreduce/sample_text.txt` |
| [mr_temperature.py](01-basics/mr_temperature.py) | Average temperature by city | JSON parsing, averages | `python mr_temperature.py temperatures.json` |
| [temperatures.json](01-basics/temperatures.json) | Sample temperature data | - | - |

**Key Concepts**: MRJob class, mapper/reducer methods, yield vs return, runners

---

### Level 2: Multi-Step Jobs (30-40 minutes)
**Directory**: `02-multistep/`

| File | Description | Steps | Run Command |
|------|-------------|-------|-------------|
| [README.md](02-multistep/README.md) | Multi-step patterns | MRStep, combiners | - |
| [mr_most_common_word.py](02-multistep/mr_most_common_word.py) | Find most frequent word | 2 steps | `python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt` |
| [mr_top_words.py](02-multistep/mr_top_words.py) | Top N most common words | 2 steps | `python mr_top_words.py ../../../datasets/book/*.txt` |
| [mr_word_length_distribution.py](02-multistep/mr_word_length_distribution.py) | Word length analysis | 3 steps | `python mr_word_length_distribution.py ../../../datasets/book/*.txt` |

**Key Concepts**: MRStep, combiners, chaining operations, custom arguments

---

### Level 3: Real-World Applications (40-60 minutes)
**Directory**: `03-applications/`

| File | Description | Use Case | Run Command |
|------|-------------|----------|-------------|
| [README.md](03-applications/README.md) | Real-world patterns | Production patterns | - |
| [mr_log_analyzer.py](03-applications/mr_log_analyzer.py) | Server log analysis | DevOps, monitoring | `python mr_log_analyzer.py sample_logs.txt` |
| [mr_sales_analytics.py](03-applications/mr_sales_analytics.py) | Business intelligence | Sales, revenue | `python mr_sales_analytics.py sales_data.json` |
| [mr_inverted_index.py](03-applications/mr_inverted_index.py) | Search engine index | Information retrieval | `python mr_inverted_index.py ../../../datasets/mapreduce/*.txt` |
| [mr_session_analysis.py](03-applications/mr_session_analysis.py) | User behavior analysis | Web analytics | `python mr_session_analysis.py clickstream.json` |
| [sample_logs.txt](03-applications/sample_logs.txt) | Apache/Nginx logs | - | - |
| [sales_data.json](03-applications/sales_data.json) | Sales transactions | - | - |
| [clickstream.json](03-applications/clickstream.json) | User events | - | - |

**Key Concepts**: JSON/CSV parsing, regex, error handling, business logic, protocols

---

## 🎯 By Learning Goal

### I want to understand mrjob basics
1. Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. Complete [01-basics/](01-basics/)
3. Try exercises 1.1-1.3 in [EXERCISES.md](EXERCISES.md)

### I want to build complex pipelines
1. Complete Level 1 first
2. Study [02-multistep/README.md](02-multistep/README.md)
3. Run all examples in [02-multistep/](02-multistep/)
4. Try exercises 2.1-2.3 in [EXERCISES.md](EXERCISES.md)

### I want to solve real-world problems
1. Complete Levels 1 and 2 first
2. Study [03-applications/README.md](03-applications/README.md)
3. Run all examples in [03-applications/](03-applications/)
4. Try exercises 3.1-3.4 in [EXERCISES.md](EXERCISES.md)

### I need a quick reference
- Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for syntax and patterns
- Check [README.md](README.md) for runner options
- See [INSTALLATION.md](INSTALLATION.md) for troubleshooting

---

## 📊 By Data Format

### Text Files
- [mr_word_count.py](01-basics/mr_word_count.py)
- [mr_word_frequency.py](01-basics/mr_word_frequency.py)
- [mr_most_common_word.py](02-multistep/mr_most_common_word.py)
- [mr_top_words.py](02-multistep/mr_top_words.py)
- [mr_inverted_index.py](03-applications/mr_inverted_index.py)

### JSON
- [mr_temperature.py](01-basics/mr_temperature.py)
- [mr_sales_analytics.py](03-applications/mr_sales_analytics.py)
- [mr_session_analysis.py](03-applications/mr_session_analysis.py)

### Log Files
- [mr_log_analyzer.py](03-applications/mr_log_analyzer.py)

---

## 🎓 By Difficulty

### Beginner
- [mr_word_count.py](01-basics/mr_word_count.py) ⭐
- [mr_word_frequency.py](01-basics/mr_word_frequency.py) ⭐
- Exercises 1.1, 1.2 ⭐

### Intermediate
- [mr_temperature.py](01-basics/mr_temperature.py) ⭐⭐
- [mr_most_common_word.py](02-multistep/mr_most_common_word.py) ⭐⭐
- [mr_top_words.py](02-multistep/mr_top_words.py) ⭐⭐
- [mr_log_analyzer.py](03-applications/mr_log_analyzer.py) ⭐⭐
- Exercises 1.3, 2.1, 2.2, 3.1, 3.2 ⭐⭐

### Advanced
- [mr_word_length_distribution.py](02-multistep/mr_word_length_distribution.py) ⭐⭐⭐
- [mr_sales_analytics.py](03-applications/mr_sales_analytics.py) ⭐⭐⭐
- [mr_inverted_index.py](03-applications/mr_inverted_index.py) ⭐⭐⭐
- [mr_session_analysis.py](03-applications/mr_session_analysis.py) ⭐⭐⭐
- Exercises 2.3, 3.3, 3.4, Challenges ⭐⭐⭐

---

## 🔍 By Concept

### Basic MapReduce
- [mr_word_count.py](01-basics/mr_word_count.py) - Mapper, reducer
- [mr_word_frequency.py](01-basics/mr_word_frequency.py) - Multiple keys
- [mr_temperature.py](01-basics/mr_temperature.py) - Averages

### Multi-Step Processing
- [mr_most_common_word.py](02-multistep/mr_most_common_word.py) - Two steps
- [mr_word_length_distribution.py](02-multistep/mr_word_length_distribution.py) - Three steps

### Optimization
- [mr_most_common_word.py](02-multistep/mr_most_common_word.py) - Combiners
- [mr_top_words.py](02-multistep/mr_top_words.py) - Combiners

### Data Parsing
- [mr_temperature.py](01-basics/mr_temperature.py) - JSON
- [mr_log_analyzer.py](03-applications/mr_log_analyzer.py) - Regex
- [mr_sales_analytics.py](03-applications/mr_sales_analytics.py) - JSON

### Custom Arguments
- [mr_top_words.py](02-multistep/mr_top_words.py) - --top-n
- [mr_log_analyzer.py](03-applications/mr_log_analyzer.py) - --analysis
- [mr_sales_analytics.py](03-applications/mr_sales_analytics.py) - --metric

### Output Protocols
- [mr_inverted_index.py](03-applications/mr_inverted_index.py) - JSONValueProtocol
- [mr_sales_analytics.py](03-applications/mr_sales_analytics.py) - JSONValueProtocol

---

## 🚀 Quick Commands

### Run Examples
```bash
# Level 1
cd 01-basics
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt
python mr_word_frequency.py ../../../datasets/mapreduce/sample_text.txt
python mr_temperature.py temperatures.json

# Level 2
cd ../02-multistep
python mr_most_common_word.py ../../../datasets/mapreduce/sample_text.txt
python mr_top_words.py ../../../datasets/book/*.txt
python mr_word_length_distribution.py ../../../datasets/book/*.txt

# Level 3
cd ../03-applications
python mr_log_analyzer.py sample_logs.txt
python mr_sales_analytics.py sales_data.json
python mr_inverted_index.py ../../../datasets/mapreduce/*.txt
python mr_session_analysis.py clickstream.json
```

### Different Runners
```bash
# Inline (default)
python mr_word_count.py input.txt

# Local (simulates Hadoop)
python mr_word_count.py -r local input.txt

# Verbose
python mr_word_count.py -v input.txt
```

---

## 📈 Learning Progress Tracker

Track your progress through the module:

### Documentation
- [ ] Read GETTING_STARTED.md
- [ ] Read INSTALLATION.md
- [ ] Skim QUICK_REFERENCE.md
- [ ] Read README.md

### Level 1: Basics
- [ ] Read 01-basics/README.md
- [ ] Run mr_word_count.py
- [ ] Run mr_word_frequency.py
- [ ] Run mr_temperature.py
- [ ] Complete Exercise 1.1
- [ ] Complete Exercise 1.2
- [ ] Complete Exercise 1.3

### Level 2: Multi-Step
- [ ] Read 02-multistep/README.md
- [ ] Run mr_most_common_word.py
- [ ] Run mr_top_words.py
- [ ] Run mr_word_length_distribution.py
- [ ] Complete Exercise 2.1
- [ ] Complete Exercise 2.2
- [ ] Complete Exercise 2.3

### Level 3: Applications
- [ ] Read 03-applications/README.md
- [ ] Run mr_log_analyzer.py
- [ ] Run mr_sales_analytics.py
- [ ] Run mr_inverted_index.py
- [ ] Run mr_session_analysis.py
- [ ] Complete Exercise 3.1
- [ ] Complete Exercise 3.2
- [ ] Complete Exercise 3.3
- [ ] Complete Exercise 3.4

### Mastery
- [ ] Complete Challenge 1
- [ ] Complete Challenge 2
- [ ] Complete Challenge 3
- [ ] Build your own application

---

## 🎯 Quick Navigation

**New to mrjob?** → [GETTING_STARTED.md](GETTING_STARTED.md)  
**Need to install?** → [INSTALLATION.md](INSTALLATION.md)  
**Looking for syntax?** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)  
**Want to practice?** → [EXERCISES.md](EXERCISES.md)  
**Need overview?** → [README.md](README.md)  
**Want statistics?** → [MODULE_SUMMARY.md](MODULE_SUMMARY.md)

---

**Total Files**: 20+  
**Total Examples**: 10  
**Total Exercises**: 13  
**Estimated Time**: 3-4 hours

Happy learning! 🎓
