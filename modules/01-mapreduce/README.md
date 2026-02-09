# MapReduce - Fundamentals

## Introduction

MapReduce is a programming model for processing large volumes of data in a distributed manner. The paradigm is based on two main operations:

- **Map**: Transforms input data into key-value pairs
- **Reduce**: Groups and processes values associated with the same key

## Learning Approaches

This module covers three approaches to learn MapReduce locally:

### 1. Pure Python (Fundamentals)
- Implementation from scratch using native Python functions
- Goal: Understand the concept without external dependencies
- Ideal for: Understanding theory and data flow
- Location: `01-pure-python/`

### 2. mrjob (Hadoop Simulation)
- Library that simulates Hadoop behavior locally
- Goal: Write Hadoop-compatible code
- Ideal for: Transition to production environments
- Location: `02-mrjob/`
- **Status**: ✅ Complete - Ready to use!

### 3. PySpark (Professional Tool)
- Modern framework based on MapReduce with optimizations
- Goal: Use industry-standard tools
- Ideal for: Real applications and advanced analysis
- Location: `03-pyspark/`

## Recommended Progression

1. Start with pure Python to understand concepts
2. Practice with mrjob to see realistic implementations
3. Apply knowledge with PySpark for professional cases

## Requirements

- Python 3.8+
- pip for package installation
- Code editor or Jupyter Notebook
