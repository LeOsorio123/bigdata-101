"""
Temperature Analysis - Calculate average temperature by city.

Demonstrates MapReduce with structured data (dictionaries)
and a reducer that calculates averages instead of sums.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mapreduce_framework import mapreduce


def mapper(record):
    """
    Extracts (city, temperature) from each record.
    
    Args:
        record: Dictionary with city, temperature, and date
    
    Yields:
        Tuple (city, temperature)
    """
    yield (record['city'], record['temperature'])


def reducer(city, temperatures):
    """
    Calculates average temperature for a city.
    
    Args:
        city: City name
        temperatures: List of temperature values
    
    Returns:
        Average temperature rounded to 1 decimal
    """
    return round(sum(temperatures) / len(temperatures), 1)


if __name__ == "__main__":
    # Temperature data from Colombian cities
    temperatures = [
        {'city': 'Medellin', 'temperature': 22, 'date': '2026-01-01'},
        {'city': 'Bogota', 'temperature': 14, 'date': '2026-01-01'},
        {'city': 'Medellin', 'temperature': 24, 'date': '2026-01-02'},
        {'city': 'Cali', 'temperature': 28, 'date': '2026-01-01'},
        {'city': 'Bogota', 'temperature': 13, 'date': '2026-01-02'},
        {'city': 'Cali', 'temperature': 30, 'date': '2026-01-02'},
        {'city': 'Medellin', 'temperature': 23, 'date': '2026-01-03'},
        {'city': 'Bogota', 'temperature': 15, 'date': '2026-01-03'},
        {'city': 'Cartagena', 'temperature': 32, 'date': '2026-01-01'},
        {'city': 'Cartagena', 'temperature': 33, 'date': '2026-01-02'},
    ]
    
    print(f"Analyzing {len(temperatures)} temperature records...\n")
    
    # Execute MapReduce
    results = mapreduce(temperatures, mapper, reducer)
    
    # Show results
    print("=" * 40)
    print("Average Temperature by City")
    print("=" * 40)
    for city, temp in sorted(results.items()):
        print(f"  {city}: {temp}°C")
    print()
    
    # Additional stats
    hottest = max(results.items(), key=lambda x: x[1])
    coldest = min(results.items(), key=lambda x: x[1])
    print(f"Hottest city: {hottest[0]} ({hottest[1]}°C)")
    print(f"Coldest city: {coldest[0]} ({coldest[1]}°C)")
