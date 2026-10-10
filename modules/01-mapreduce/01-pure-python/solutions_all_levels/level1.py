"""Level 1: exercises 1.1–1.5, built on the instructor's MapReduce engine."""
from common import mapreduce, words
TEXT = ['MapReduce is a programming model', 'for processing large data sets']
SALES = [
    {'product': 'Laptop', 'amount': 1200}, {'product': 'Mouse', 'amount': 25},
    {'product': 'Laptop', 'amount': 1100}, {'product': 'Mouse', 'amount': 30},
    {'product': 'Laptop', 'amount': 1250}, {'product': 'Keyboard', 'amount': 75},
    {'product': 'Keyboard', 'amount': 80},
]
TEMPS = [
    {'city': 'Medellin', 'temperature': 22}, {'city': 'Bogota', 'temperature': 14},
    {'city': 'Medellin', 'temperature': 24}, {'city': 'Cali', 'temperature': 28},
    {'city': 'Bogota', 'temperature': 13}, {'city': 'Cali', 'temperature': 30},
    {'city': 'Medellin', 'temperature': 23}, {'city': 'Bogota', 'temperature': 15},
    {'city': 'Cartagena', 'temperature': 32}, {'city': 'Cartagena', 'temperature': 33},
]
CATEGORIES = [
    {'product': 'Laptop', 'category': 'Electronics', 'amount': 1200},
    {'product': 'Mouse', 'category': 'Electronics', 'amount': 25},
    {'product': 'Desk', 'category': 'Furniture', 'amount': 600},
    {'product': 'Chair', 'category': 'Furniture', 'amount': 350},
    {'product': 'Monitor', 'category': 'Electronics', 'amount': 450},
]
def sum_values(key, values):
    """Add grouped numeric values."""
    return sum(values)
def character_mapper(line):
    """Emit one occurrence for each alphabetic character ignoring case."""
    for char in line.lower():
        if char.isalpha(): yield char, 1
def long_words_mapper(line):
    """Emit only words whose normalized length exceeds five."""
    for word in words(line):
        if len(word)>5: yield word, 1
def product_mapper(sale):
    """Emit product and sale amount."""
    yield sale['product'], sale['amount']
def mean_reducer(key, amounts):
    """Compute rounded mean from grouped sale amounts."""
    return round(sum(amounts)/len(amounts), 1)
def temp_mapper(record):
    """Emit a city and its recorded temperature."""
    yield record['city'], record['temperature']
def temp_reducer(city, values):
    """Calculate minimum, maximum and one-decimal mean for a city."""
    return {'min':min(values), 'max':max(values), 'avg':round(sum(values)/len(values),1)}
def category_mapper(sale):
    """Emit category and amount from a sale."""
    yield sale['category'], sale['amount']
def category_reducer(category, values):
    """Calculate count, total, and mean sale per category."""
    return {'count':len(values), 'total':sum(values),'avg':round(sum(values)/len(values),1)}
def main():
    """Print the five exercise solutions."""
    exercises=[('1.1 Character Counter',mapreduce(TEXT,character_mapper,sum_values)),
        ('1.2 Long Words',mapreduce(TEXT,long_words_mapper,sum_values)),
        ('1.3 Sales Average',mapreduce(SALES,product_mapper,mean_reducer)),
        ('1.4 Temperature Statistics',mapreduce(TEMPS,temp_mapper,temp_reducer)),
        ('1.5 Category Statistics',mapreduce(CATEGORIES,category_mapper,category_reducer))]
    for title,results in exercises:
        print('\n'+title)
        for key,value in sorted(results.items()):print(f'  {key}: {value}')
if __name__=='__main__': main()
