"""
Top N Words - Find the most common words.

Finds the top N most frequently occurring words in text files.
Shows how to configure job parameters and handle top-N problems.

Step 1: Count word frequencies
Step 2: Collect and sort to find top N

Usage:
    python mr_top_words.py input.txt
    python mr_top_words.py --top-n=20 ../../../datasets/book/*.txt
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
import re


class MRTopWords(MRJob):
    """
    Multi-step job to find top N most common words.
    
    Input: Text files
    Output: Top N (count, word) pairs sorted by frequency
    """
    
    def configure_args(self):
        """
        Add custom command-line arguments.
        """
        super(MRTopWords, self).configure_args()
        self.add_passthru_arg(
            '--top-n', type=int, default=10,
            help='Number of top words to return (default: 10)'
        )
    
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
            MRStep(reducer=self.reducer_find_top_words)
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
            # Filter out very short words
            if len(word) > 2:
                yield (word, 1)
    
    def combiner_count_words(self, word, counts):
        """
        Optimization: Sum counts on mapper nodes.
        
        Args:
            word: The word
            counts: Iterator of counts
        
        Yields:
            (word, partial_sum)
        """
        yield (word, sum(counts))
    
    def reducer_count_words(self, word, counts):
        """
        Sum all counts for each word.
        
        Args:
            word: The word
            counts: Iterator of counts
        
        Yields:
            (None, (count, word)) - All go to same reducer in step 2
        """
        total = sum(counts)
        # Emit with None as key so all pairs go to same reducer
        yield None, (total, word)
    
    # ===== STEP 2: Find top N =====
    
    def reducer_find_top_words(self, _, word_count_pairs):
        """
        Find the top N words by count.
        
        Args:
            _: Key (None)
            word_count_pairs: Iterator of (count, word) tuples
        
        Yields:
            (count, word) for each of the top N words
        """
        # Sort all pairs by count (descending) and take top N
        top_words = sorted(word_count_pairs, reverse=True)[:self.options.top_n]
        
        for count, word in top_words:
            yield (count, word)


if __name__ == '__main__':
    MRTopWords.run()
