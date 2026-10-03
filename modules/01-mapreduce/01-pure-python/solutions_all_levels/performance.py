"""Performance tasks P.1 and P.2, using the instructor's engines and stdlib."""
import sys
import tempfile
import time
from common import BASE, REPO, mapreduce

DIST = BASE / '03-distributed-simulation'
sys.path.insert(0, str(DIST))
from parallel_mapreduce import parallel_mapreduce, word_mapper, word_reducer
from simulated_hdfs import SimulatedHDFS
from distributed_mapreduce import distributed_mapreduce_from_hdfs


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
    """P.2: report block count, upload, processing and total times for each size."""
    files, data = book_lines()
    source = files[0]
    expected = mapreduce(data, word_mapper, word_reducer)
    outcomes = []
    for size in (4096, 16384, 65536):
        with tempfile.TemporaryDirectory(prefix='hdfs_blocks_') as temp_dir:
            hdfs = SimulatedHDFS(base_dir=temp_dir, block_size=size,
                                 replication=1, num_nodes=2)
            start_total = time.perf_counter()
            hdfs.put(str(source), '/book.txt')
            upload_seconds = time.perf_counter() - start_total
            blocks = hdfs.get_blocks('/book.txt')
            start_processing = time.perf_counter()
            result = distributed_mapreduce_from_hdfs(
                hdfs, '/book.txt', word_mapper, word_reducer,
                num_mappers=2, num_reducers=2
            )
            processing_seconds = time.perf_counter() - start_processing
            total_seconds = time.perf_counter() - start_total
            if len(files) == 1:
                assert result == expected, f'Mismatched counts at {size} bytes'
            print(f'P.2 block={size} bytes; blocks={len(blocks)}; '
                  f'upload={upload_seconds:.6f}s; '
                  f'processing={processing_seconds:.6f}s; '
                  f'total={total_seconds:.6f}s; unique_words={len(result)}')
            outcomes.append((size, len(blocks), upload_seconds,
                             processing_seconds, total_seconds))
    return outcomes


if __name__ == '__main__':
    sequential_parallel()
    block_sizes()
