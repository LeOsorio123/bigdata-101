"""Performance experiments using only the standard library and instructor's code."""
import sys
import time
import tempfile
from common import BASE, REPO, mapreduce
DIST=BASE/'03-distributed-simulation'
sys.path.insert(0,str(DIST))
from parallel_mapreduce import parallel_mapreduce,word_mapper,word_reducer
from simulated_hdfs import SimulatedHDFS
from distributed_mapreduce import distributed_mapreduce_from_hdfs
def book_lines():
    files=sorted((REPO/'datasets/book').glob('*.txt'))
    if not files:raise FileNotFoundError('No datasets/book/*.txt files')
    return files,[line.rstrip('\n') for f in files for line in f.open(encoding='utf-8') if line.strip()]
def sequential_parallel():
    files,data=book_lines()
    start=time.perf_counter();seq=mapreduce(data,word_mapper,word_reducer);seq_seconds=time.perf_counter()-start
    start=time.perf_counter();par=parallel_mapreduce(data,word_mapper,word_reducer,num_mappers=2,num_reducers=2);par_seconds=time.perf_counter()-start
    assert seq==par,'Mismatch between sequential and parallel results'
    print(f'P.1 files: {[p.name for p in files]}; lines: {len(data)}')
    print(f'P.1 sequential: {seq_seconds:.6f}s; parallel: {par_seconds:.6f}s; equivalent: yes')
    return seq_seconds,par_seconds
def block_sizes():
    files,_=book_lines();source=files[0];outcome=[]
    for size in (4096,16384,65536):
        with tempfile.TemporaryDirectory(prefix='hdfs_blocks_') as tmp:
            hdfs=SimulatedHDFS(base_dir=tmp,block_size=size,replication=1,num_nodes=2)
            hdfs.put(str(source),'/book.txt')
            blocks=hdfs.get_blocks('/book.txt')
            start=time.perf_counter()
            result=distributed_mapreduce_from_hdfs(hdfs,'/book.txt',word_mapper,word_reducer,num_mappers=2,num_reducers=2)
            elapsed=time.perf_counter()-start
            print(f'P.2 block={size} bytes; blocks={len(blocks)}; processing={elapsed:.6f}s; unique_words={len(result)}')
            outcome.append((size,len(blocks),elapsed))
    return outcome
if __name__=='__main__':
    sequential_parallel()
    block_sizes()
