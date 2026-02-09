"""
Log Analyzer - Analyze server logs with MapReduce.

Parses Apache/Nginx log files and generates statistics:
- Request counts by status code
- Most accessed endpoints
- Traffic by IP address

Input format (Apache Common Log Format):
192.168.1.1 - - [01/Jan/2026:10:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234

Usage:
    python mr_log_analyzer.py server.log
    python mr_log_analyzer.py --analysis=status server.log
    python mr_log_analyzer.py --analysis=endpoint server.log
    python mr_log_analyzer.py --analysis=ip server.log
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
import re


class MRLogAnalyzer(MRJob):
    """
    Analyze server logs to extract insights.
    
    Input: Apache/Nginx log files
    Output: Statistics based on analysis type
    """
    
    # Regex pattern for Apache Common Log Format
    LOG_PATTERN = re.compile(
        r'(\S+) '  # IP address
        r'\S+ \S+ '  # identd and userid (ignored)
        r'\[(.*?)\] '  # timestamp
        r'"(\S+) '  # HTTP method
        r'(\S+) '  # endpoint/path
        r'(\S+)" '  # protocol
        r'(\d+) '  # status code
        r'(\d+)'  # response size
    )
    
    def configure_args(self):
        """Add custom command-line arguments."""
        super(MRLogAnalyzer, self).configure_args()
        self.add_passthru_arg(
            '--analysis',
            default='status',
            choices=['status', 'endpoint', 'ip', 'error'],
            help='Type of analysis to perform'
        )
    
    def steps(self):
        """Define job steps."""
        return [
            MRStep(mapper=self.mapper_parse_logs,
                   combiner=self.combiner_count,
                   reducer=self.reducer_count),
            MRStep(reducer=self.reducer_sort_results)
        ]
    
    # ===== STEP 1: Parse and count =====
    
    def mapper_parse_logs(self, _, line):
        """
        Parse log lines and extract relevant information.
        
        Args:
            _: Key (ignored)
            line: Log line
        
        Yields:
            (key, 1) based on analysis type
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return  # Skip malformed lines
        
        ip, timestamp, method, endpoint, protocol, status, size = match.groups()
        
        analysis_type = self.options.analysis
        
        if analysis_type == 'status':
            # Count by status code
            yield (f"Status {status}", 1)
        
        elif analysis_type == 'endpoint':
            # Count by endpoint
            yield (endpoint, 1)
        
        elif analysis_type == 'ip':
            # Count by IP address
            yield (ip, 1)
        
        elif analysis_type == 'error':
            # Count only errors (4xx and 5xx)
            if status.startswith('4') or status.startswith('5'):
                yield (f"{status} {endpoint}", 1)
    
    def combiner_count(self, key, counts):
        """
        Partial counting on mapper nodes.
        
        Args:
            key: The key being counted
            counts: Iterator of counts
        
        Yields:
            (key, partial_sum)
        """
        yield (key, sum(counts))
    
    def reducer_count(self, key, counts):
        """
        Sum all counts for each key.
        
        Args:
            key: The key being counted
            counts: Iterator of counts
        
        Yields:
            (None, (count, key)) for sorting in next step
        """
        total = sum(counts)
        # Emit with None key to send all to same reducer for sorting
        yield None, (total, key)
    
    # ===== STEP 2: Sort results =====
    
    def reducer_sort_results(self, _, count_key_pairs):
        """
        Sort results by count (descending).
        
        Args:
            _: Key (None)
            count_key_pairs: Iterator of (count, key) tuples
        
        Yields:
            (key, count) sorted by count
        """
        # Sort by count (descending) and output
        sorted_results = sorted(count_key_pairs, reverse=True)
        
        for count, key in sorted_results:
            yield (key, count)


if __name__ == '__main__':
    MRLogAnalyzer.run()
