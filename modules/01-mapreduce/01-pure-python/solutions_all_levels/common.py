"""Shared imports and text normalization, only standard-library modules."""
import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
REPO = BASE.parents[2]
sys.path.insert(0, str(BASE / '01-basics'))
from mapreduce_framework import mapreduce
PUNCTUATION = '.,!?;:"()[]{}<>/\\'
def words(line):
    """Return normalized nonempty words from a line of text."""
    return [w for token in line.lower().split() if (w := token.strip(PUNCTUATION))]
def source_files():
    """Return mapreduce text datasets (excluding documentation and nested index files)."""
    return sorted((REPO / 'datasets/mapreduce').glob('*.txt'))
def lines_from_files(paths):
    """Yield (filename, line) pairs for all supplied files."""
    for path in paths:
        had_lines = False
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                had_lines = True
                yield path.name, line
        if not had_lines:
            yield path.name, ''
