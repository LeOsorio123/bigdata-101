"""
Most Common Word - Two-step MapReduce job.

Finds the single most frequently occurring word in text files.
Demonstrates the basic pattern for multi-step jobs.

Step 1: Count word frequencies (like WordCount)
Step 2: Find the word with maximum count

Usage:
    python mr_most_common_word.py input.txt
    python mr_most_common_word.py ../../../datasets/book/*.txt
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
import re


class MRMostCommonWord(MRJob):
    """
    Two-step job to find the most common word.
    
    Input: Text files
    Output: (count, word) for the most frequent word
    """
    
    def steps(self):
        """
        Define the two steps of this job.
        
        Returns:
            List of MRStep objects
        """
        return [
            MRStep(mapper=self.mapper_get_words,
                   combiner=self.combiner_count_words,
                   reducer=self.reducer_count_words),
            MRStep(reducer=self.reducer_find_max_word)
        ]
    
    # ===== STEP 1: Count word frequencies =====
    
    def mapper_get_words(self, _, line):
        """
        Extract words from each line.
        
        Args:
            _: Key (ignored)
            line: Text line
        
        Yields:
            (word, 1) for each word
        """
        words = re.findall(r'\w+', line.lower())
        for word in words:
            yield (word, 1)
    
    def combiner_count_words(self, word, counts):
        """
        Optimization: Sum counts on mapper nodes.
        
        Args:
            word: The word
            counts: Iterator of counts (1s)
        
        Yields:
            (word, partial_sum)
        """
        yield (word, sum(counts))
    
    def reducer_count_words(self, word, counts):
        """
        Sum all counts for each word and prepare for step 2.
        
        Args:
            word: The word
            counts: Iterator of counts
        
        Yields:
            (None, (count, word)) - All go to same reducer in step 2
        """
        total = sum(counts)
        # Emit with None as key so all pairs go to same reducer
        # Put count first so max() works correctly
        yield None, (total, word)
    
    # ===== STEP 2: Find maximum =====
    
    def reducer_find_max_word(self, _, word_count_pairs):
        """
        Find the word with maximum count.
        
        Args:
            _: Key (None)
            word_count_pairs: Iterator of (count, word) tuples
        
        Yields:
            (count, word) for the most frequent word
        """
        # max() compares tuples element by element
        # Since count is first, it finds the highest count
        yield max(word_count_pairs)


if __name__ == '__main__':
    MRMostCommonWord.run()
