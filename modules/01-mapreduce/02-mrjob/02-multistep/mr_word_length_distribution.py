"""
Word Length Distribution - Three-step analysis.

Analyzes the distribution of word lengths in text files.
Shows how to chain three MapReduce steps together.

Step 1: Extract words and their lengths
Step 2: Count how many words have each length
Step 3: Sort by length for readable output

Usage:
    python mr_word_length_distribution.py input.txt
    python mr_word_length_distribution.py ../../../datasets/book/*.txt
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
import re


class MRWordLengthDistribution(MRJob):
    """
    Three-step job to analyze word length distribution.
    
    Input: Text files
    Output: (length, count) pairs showing how many words of each length
    """
    
    def steps(self):
        """
        Define the three steps of this job.
        
        Returns:
            List of MRStep objects
        """
        return [
            MRStep(mapper=self.mapper_get_word_lengths,
                   combiner=self.combiner_count_lengths,
                   reducer=self.reducer_count_lengths),
            MRStep(mapper=self.mapper_prepare_sort,
                   reducer=self.reducer_sort_by_length)
        ]
    
    # ===== STEP 1: Map words to lengths and count =====
    
    def mapper_get_word_lengths(self, _, line):
        """
        Extract words and emit their lengths.
        
        Args:
            _: Key (ignored)
            line: Text line
        
        Yields:
            (word_length, 1) for each word
        """
        words = re.findall(r'\w+', line.lower())
        for word in words:
            word_length = len(word)
            yield (word_length, 1)
    
    def combiner_count_lengths(self, length, counts):
        """
        Optimization: Partial counting on mapper nodes.
        
        Args:
            length: Word length
            counts: Iterator of counts (1s)
        
        Yields:
            (length, partial_count)
        """
        yield (length, sum(counts))
    
    def reducer_count_lengths(self, length, counts):
        """
        Sum all counts for each word length.
        
        Args:
            length: Word length
            counts: Iterator of counts
        
        Yields:
            (length, total_count)
        """
        yield (length, sum(counts))
    
    # ===== STEP 2: Sort by length =====
    
    def mapper_prepare_sort(self, length, count):
        """
        Prepare data for sorting (already in correct format).
        
        Args:
            length: Word length
            count: Number of words with this length
        
        Yields:
            (length, count) - mrjob will sort by key automatically
        """
        # mrjob automatically sorts by key between mapper and reducer
        # So we just pass through the data
        yield (length, count)
    
    def reducer_sort_by_length(self, length, counts):
        """
        Output sorted results.
        
        Args:
            length: Word length (sorted)
            counts: Iterator of counts (should be just one)
        
        Yields:
            (length, count) in sorted order
        """
        # There should only be one count per length at this point
        for count in counts:
            yield (length, count)


if __name__ == '__main__':
    MRWordLengthDistribution.run()
