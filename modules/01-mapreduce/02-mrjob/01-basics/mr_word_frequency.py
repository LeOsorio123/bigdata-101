"""
Word Frequency - Multi-metric counting with mrjob.

Counts characters, words, and lines in text files simultaneously.
Shows how to emit multiple different keys from the same mapper.

Usage:
    python mr_word_frequency.py input.txt
    python mr_word_frequency.py ../../../datasets/book/*.txt
"""

from mrjob.job import MRJob


class MRWordFrequency(MRJob):
    """
    MapReduce job that counts multiple text metrics.
    
    Input: Text files
    Output: Three metrics - chars, words, lines
    """
    
    def mapper(self, _, line):
        """
        Emits counts for characters, words, and lines.
        
        Args:
            _: Key (ignored)
            line: One line of text
        
        Yields:
            ("chars", character_count)
            ("words", word_count)
            ("lines", 1)
        """
        # Count characters in the line
        yield ("chars", len(line))
        
        # Count words in the line
        yield ("words", len(line.split()))
        
        # Count this line
        yield ("lines", 1)
    
    def reducer(self, key, values):
        """
        Sums all values for each metric.
        
        Args:
            key: Metric name ("chars", "words", or "lines")
            values: Iterator of counts
        
        Yields:
            (metric_name, total_count)
        """
        yield (key, sum(values))


if __name__ == '__main__':
    MRWordFrequency.run()
