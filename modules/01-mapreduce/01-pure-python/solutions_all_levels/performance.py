"""Performance tasks P.1 and P.2, using the instructor's engines and stdlib."""
import sys
import time
from common import BASE, REPO, mapreduce

DIST = BASE / '03-distributed-simulation'
sys.path.insert(0, str(DIST))
from parallel_mapreduce import parallel_mapreduce, word_mapper, word_reducer
from distributed_mapreduce import benchmark_block_sizes


def book_lines():
    """Load the same complete book dataset for sequential and parallel runs."""
    files = sorted((REPO / 'datasets/book').glob('*.txt'))
    if not files:
        raise FileNotFoundError('No datasets/book/*.txt files found')
    data = []
    for file in files:
        with file.open(encoding='utf-8') as stream:
            data.extend(line.rstrip('\n') for line in stream if line.strip())
    return files, data


def sequential_parallel():
    """P.1: time both engines on identical input and validate their counts."""
    files, data = book_lines()
    start = time.perf_counter()
    sequential = mapreduce(data, word_mapper, word_reducer)
    sequential_seconds = time.perf_counter() - start

    start = time.perf_counter()
    parallel = parallel_mapreduce(data, word_mapper, word_reducer,
                                  num_mappers=2, num_reducers=2)
    parallel_seconds = time.perf_counter() - start
    assert sequential == parallel, 'Sequential/parallel word counts differ'
    print(f'P.1 files: {[f.name for f in files]}; lines: {len(data)}')
    print(f'P.1 sequential: {sequential_seconds:.6f}s; '
          f'parallel: {parallel_seconds:.6f}s; equivalent: yes')
    return sequential_seconds, parallel_seconds


def block_sizes():
    """P.2: invoke the benchmarking extension in distributed_mapreduce.py."""
    files, _ = book_lines()
    source = files[0]
    with source.open(encoding='utf-8') as stream:
        data = [line.rstrip('\n') for line in stream if line.strip()]
    expected = mapreduce(data, word_mapper, word_reducer)
    return benchmark_block_sizes(source, expected=expected)


if __name__ == '__main__':
    sequential_parallel()
    block_sizes()
