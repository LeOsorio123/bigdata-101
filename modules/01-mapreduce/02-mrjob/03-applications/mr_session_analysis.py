"""
Session Analysis - Analyze user behavior from clickstream data.

Analyzes user sessions to understand behavior patterns:
- Session duration per user
- Page views per session
- Most visited pages
- User engagement metrics

Input format (JSON per line):
{"user_id": "U001", "timestamp": "2026-01-15T10:30:00", 
 "page": "/home", "action": "view", "session_id": "S123"}

Usage:
    python mr_session_analysis.py clickstream.json
    python mr_session_analysis.py --analysis=user clickstream.json
    python mr_session_analysis.py --analysis=page clickstream.json
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
import json
from datetime import datetime


class MRSessionAnalysis(MRJob):
    """
    Analyze user sessions from clickstream data.
    
    Input: JSON lines with clickstream events
    Output: Session analytics
    """
    
    OUTPUT_PROTOCOL = JSONValueProtocol
    
    def configure_args(self):
        """Add custom command-line arguments."""
        super(MRSessionAnalysis, self).configure_args()
        self.add_passthru_arg(
            '--analysis',
            default='session',
            choices=['session', 'user', 'page'],
            help='Type of analysis to perform'
        )
    
    def steps(self):
        """Define job steps."""
        return [
            MRStep(mapper=self.mapper_parse_events,
                   reducer=self.reducer_analyze)
        ]
    
    def mapper_parse_events(self, _, line):
        """
        Parse clickstream events.
        
        Args:
            _: Key (ignored)
            line: JSON line with event data
        
        Yields:
            Different keys based on analysis type
        """
        try:
            event = json.loads(line)
            
            analysis = self.options.analysis
            
            if analysis == 'session':
                # Analyze by session
                session_id = event.get('session_id')
                timestamp = event.get('timestamp')
                yield (session_id, {
                    'timestamp': timestamp,
                    'page': event.get('page'),
                    'user_id': event.get('user_id')
                })
            
            elif analysis == 'user':
                # Analyze by user
                user_id = event.get('user_id')
                yield (user_id, {
                    'session_id': event.get('session_id'),
                    'page': event.get('page')
                })
            
            elif analysis == 'page':
                # Analyze by page
                page = event.get('page')
                yield (page, 1)
        
        except (json.JSONDecodeError, KeyError):
            pass
    
    def reducer_analyze(self, key, values):
        """
        Analyze events based on analysis type.
        
        Args:
            key: Session ID, User ID, or Page
            values: Iterator of event data
        
        Yields:
            (key, analytics)
        """
        analysis = self.options.analysis
        
        if analysis == 'session':
            # Session analytics
            events = list(values)
            
            if not events:
                return
            
            # Extract timestamps
            timestamps = [e['timestamp'] for e in events if 'timestamp' in e]
            
            analytics = {
                'page_views': len(events),
                'pages': list(set(e['page'] for e in events if 'page' in e)),
                'user_id': events[0].get('user_id') if events else None
            }
            
            # Calculate duration if we have timestamps
            if len(timestamps) > 1:
                try:
                    times = [datetime.fromisoformat(t.replace('Z', '+00:00')) 
                            for t in timestamps]
                    duration = (max(times) - min(times)).total_seconds()
                    analytics['duration_seconds'] = int(duration)
                except:
                    pass
            
            yield (key, analytics)
        
        elif analysis == 'user':
            # User analytics
            events = list(values)
            
            sessions = set(e['session_id'] for e in events if 'session_id' in e)
            pages = [e['page'] for e in events if 'page' in e]
            
            analytics = {
                'total_sessions': len(sessions),
                'total_page_views': len(pages),
                'unique_pages': len(set(pages)),
                'avg_pages_per_session': round(len(pages) / len(sessions), 2) if sessions else 0
            }
            
            yield (key, analytics)
        
        elif analysis == 'page':
            # Page analytics (simple count)
            count = sum(values)
            yield (key, {'views': count})


if __name__ == '__main__':
    MRSessionAnalysis.run()
