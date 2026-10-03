"""Level 2: text files, distinct vocabulary, and inverted index."""
from common import mapreduce, words, source_files, lines_from_files
def length_mapper(line):
    """Generate word-length counts from a text line."""
    for word in words(line): yield len(word),1
def sum_reducer(key,values):
    """Count emitted records."""
    return sum(values)
def file_word_mapper(record):
    """Emit (filename, normalized word) for every word in a file line."""
    filename,line=record
    for word in words(line): yield filename,word
def unique_reducer(filename, words_list):
    """Count distinct normalized words for one file."""
    return len(set(words_list))
def index_mapper(record):
    """Map each word to the file it came from."""
    filename,line=record
    for word in words(line): yield word,filename
def index_reducer(word, filenames):
    """Return sorted unique filenames containing the word."""
    return sorted(set(filenames))
def main():
    """Process the sample dataset and print three result types."""
    files=source_files()
    if not files: raise FileNotFoundError('datasets/mapreduce/*.txt not found')
    sample=next((p for p in files if p.name=='sample_text.txt'),None)
    if sample is None:raise FileNotFoundError('sample_text.txt not found')
    lines=sample.read_text(encoding='utf-8').splitlines()
    records=list(lines_from_files(files))
    tasks=[('2.1 Length distribution',mapreduce(lines,length_mapper,sum_reducer)),
           ('2.2 Unique words by file',mapreduce(records,file_word_mapper,unique_reducer)),
           ('2.3 Inverted index',mapreduce(records,index_mapper,index_reducer))]
    for title,results in tasks:
        print('\n'+title)
        for key,value in sorted(results.items()):print(f'  {key}: {value}')
if __name__=='__main__':main()
