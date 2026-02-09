"""
WordCount - Classic MapReduce example with mrjob.

Counts the frequency of each word in text files.
This is the mrjob equivalent of the pure Python wordcount.py example.

Usage:
    python mr_word_count.py input.txt
    python mr_word_count.py -r local input.txt
    python mr_word_count.py file1.txt file2.txt
"""

from mrjob.job import MRJob
import re


class MRWordCount(MRJob):
    """
    MapReduce job that counts word frequency.
    
    Input: Text files (one line per input to mapper)
    Output: (word, count) pairs sorted by word
    """
    
    def mapper(self, _, line):
        """
        Transforms each line into (word, 1) pairs.
        
        Args:
            _: Key (ignored, usually None or line number)
            line: One line of text from input file
        
        Yields:
            Tuples (word, 1) for each word in the line
        """
        # Remove punctuation and convert to lowercase
        words = re.findall(r'\w+', line.lower())
        
        for word in words:
            yield (word, 1)
    
    def reducer(self, word, counts):
        """
        Sums all counts for each word.
        
        Args:
            word: The word (key)
            counts: Iterator of counts (all are 1 from mapper)
        
        Yields:
            Tuple (word, total_count)
        """
        yield (word, sum(counts))


if __name__ == '__main__':
    # This line is REQUIRED for mrjob to work
    # It handles command-line arguments and execution
    MRWordCount.run()
