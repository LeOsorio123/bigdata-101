"""
Word Metrics - Count multiple text metrics simultaneously.

Demonstrates emitting multiple key types from the same mapper,
similar to counting chars, words, and lines at once.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mapreduce_framework import mapreduce


def mapper(line):
    """
    Emits multiple metrics for each line.
    
    Args:
        line: Text line
    
    Yields:
        ("chars", char_count)
        ("words", word_count)
        ("lines", 1)
        ("longest_word", max_word_length)
    """
    yield ("chars", len(line))
    yield ("words", len(line.split()))
    yield ("lines", 1)
    
    # Track longest word length
    words = line.split()
    if words:
        longest = max(len(w.strip('.,!?;:"()[]{}')) for w in words)
        yield ("longest_word", longest)


def reducer(key, values):
    """
    Aggregates metrics differently based on key type.
    
    Args:
        key: Metric name
        values: List of values
    
    Returns:
        Aggregated result (sum for most, max for longest_word)
    """
    if key == "longest_word":
        return max(values)
    return sum(values)


if __name__ == "__main__":
    text = [
        "MapReduce is a programming model for distributed computing",
        "It processes large volumes of data in parallel",
        "The Map phase transforms data into key-value pairs",
        "The Shuffle phase groups values by key",
        "The Reduce phase aggregates the grouped values",
        "MapReduce was popularized by Google in 2004",
        "Hadoop is the most well-known implementation",
        "Today PySpark offers a more modern alternative",
    ]
    
    print("Input text:")
    for line in text:
        print(f"  {line}")
    
    # Execute MapReduce
    results = mapreduce(text, mapper, reducer)
    
    # Show results
    print("\n" + "=" * 40)
    print("Text Metrics")
    print("=" * 40)
    print(f"  Lines:        {results.get('lines', 0)}")
    print(f"  Words:        {results.get('words', 0)}")
    print(f"  Characters:   {results.get('chars', 0)}")
    print(f"  Longest word: {results.get('longest_word', 0)} chars")
    
    if results.get('lines', 0) > 0:
        avg_words = results['words'] / results['lines']
        avg_chars = results['chars'] / results['lines']
        print(f"\n  Avg words/line: {avg_words:.1f}")
        print(f"  Avg chars/line: {avg_chars:.1f}")
