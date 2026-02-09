"""
Temperature Analysis - Calculate average temperature by city.

This solves the same problem as the pure Python exercise but using mrjob.
Demonstrates handling structured data (JSON) in MapReduce.

Usage:
    python mr_temperature.py temperatures.json
    
Input format (JSON per line):
    {"city": "Medellin", "temperature": 22, "date": "2026-01-01"}
"""

from mrjob.job import MRJob
import json


class MRTemperature(MRJob):
    """
    MapReduce job that calculates average temperature by city.
    
    Input: JSON lines with city and temperature data
    Output: (city, average_temperature) pairs
    """
    
    def mapper(self, _, line):
        """
        Extracts (city, temperature) pairs from JSON data.
        
        Args:
            _: Key (ignored)
            line: JSON string with temperature data
        
        Yields:
            (city, temperature) pairs
        """
        try:
            data = json.loads(line)
            city = data['city']
            temperature = data['temperature']
            yield (city, temperature)
        except (json.JSONDecodeError, KeyError) as e:
            # Skip malformed lines
            pass
    
    def reducer(self, city, temperatures):
        """
        Calculates average temperature for each city.
        
        Args:
            city: City name
            temperatures: Iterator of temperature values
        
        Yields:
            (city, average_temperature)
        """
        # Convert iterator to list to calculate average
        temps_list = list(temperatures)
        average = sum(temps_list) / len(temps_list)
        
        yield (city, round(average, 1))


if __name__ == '__main__':
    MRTemperature.run()
