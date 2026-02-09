"""
Inverted Index - Build a search engine index.

Creates an inverted index mapping words to documents.
This is the foundation of search engines like Google.

Output format: word -> [doc1, doc2, doc3, ...]

Usage:
    python mr_inverted_index.py file1.txt file2.txt file3.txt
    python mr_inverted_index.py ../../../datasets/mapreduce/*.txt
"""

from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
import re
import os


class MRInvertedIndex(MRJob):
    """
    Build an inverted index from text files.
    
    Input: Multiple text files
    Output: (word, [list of documents]) pairs
    """
    
    # Use JSON for output to handle lists
    OUTPUT_PROTOCOL = JSONValueProtocol
    
    def mapper(self, _, line):
        """
        Extract words and associate with document.
        
        Args:
            _: Key (ignored)
            line: Text line
        
        Yields:
            (word, document_name) pairs
        """
        # Get the input file name from environment
        # mrjob sets this when processing files
        import os
        filename = os.environ.get('mapreduce_map_input_file', 'unknown')
        
        # Extract just the filename without path
        doc_name = os.path.basename(filename)
        
        # Extract words (alphanumeric only)
        words = re.findall(r'\w+', line.lower())
        
        for word in words:
            # Filter out very short words
            if len(word) > 2:
                yield (word, doc_name)
    
    def reducer(self, word, documents):
        """
        Collect all documents containing each word.
        
        Args:
            word: The word
            documents: Iterator of document names
        
        Yields:
            (word, sorted_unique_documents)
        """
        # Get unique documents and sort them
        unique_docs = sorted(set(documents))
        
        # Output word and list of documents
        yield (word, unique_docs)


if __name__ == '__main__':
    MRInvertedIndex.run()
