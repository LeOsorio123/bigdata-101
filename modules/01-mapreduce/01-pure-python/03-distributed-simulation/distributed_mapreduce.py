"""
Complete Distributed MapReduce Simulation

Combines HDFS simulation with parallel MapReduce processing.
Demonstrates the full Hadoop-style workflow:
1. Upload files to HDFS (split into blocks)
2. Process blocks in parallel with Map tasks
3. Shuffle and sort intermediate results
4. Reduce in parallel to produce final results
"""

import sys; import os; sys.path.append(os.path.dirname(__file__)); from simulated_hdfs import SimulatedHDFS
import sys; import os; sys.path.append(os.path.dirname(__file__)); from parallel_mapreduce import parallel_mapreduce
import os
from pathlib import Path


def distributed_mapreduce_from_hdfs(
    hdfs: SimulatedHDFS,
    hdfs_path: str,
    mapper,
    reducer,
    num_mappers: int = 4,
    num_reducers: int = 2
):
    """
    Execute MapReduce on data stored in simulated HDFS.
    
    Args:
        hdfs: SimulatedHDFS instance
        hdfs_path: Path to file in HDFS
        mapper: Map function
        reducer: Reduce function
        num_mappers: Number of parallel map tasks
        num_reducers: Number of parallel reduce tasks
    
    Returns:
        Final MapReduce results
    """
    print(f"\n{'='*70}")
    print(f"DISTRIBUTED MAPREDUCE WITH SIMULATED HDFS")
    print(f"{'='*70}\n")
    
    # Get file blocks from HDFS
    print(f"[HDFS] Reading file: {hdfs_path}")
    blocks = hdfs.get_blocks(hdfs_path)
    print(f"[HDFS] File has {len(blocks)} blocks\n")
    
    # Read blocks and convert to lines (optimized)
    print("[HDFS] Reading blocks from distributed nodes...")
    
    # Read all blocks and concatenate before decoding
    full_content = b''
    total_blocks = len(blocks)
    
    for i, block_info in enumerate(blocks):
        # Simulate data locality: read from first replica
        replica = block_info['replicas'][0]
        block_data = hdfs.read_block(replica)
        full_content += block_data
        
        # Show progress every 50 blocks
        if (i + 1) % 50 == 0 or (i + 1) == total_blocks:
            print(f"  Progress: {i + 1}/{total_blocks} blocks read ({(i+1)/total_blocks*100:.1f}%)")
    
    # Decode the complete content
    print("\n[HDFS] Decoding content...")
    text = full_content.decode('utf-8')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    all_data = lines
    
    print(f"[HDFS] Total lines read: {len(all_data)}\n")
    
    # Execute parallel MapReduce
    results = parallel_mapreduce(
        all_data,
        mapper,
        reducer,
        num_mappers=num_mappers,
        num_reducers=num_reducers
    )
    
    return results


# Define mapper and reducer at module level for multiprocessing serialization
def word_mapper(line):
    """Extract words from line."""
    words = line.lower().split()
    return [(word.strip('.,!?;:"()[]{}'), 1) for word in words if word.strip('.,!?;:"()[]{}')]


def word_reducer(key, values):
    """Sum word counts."""
    return sum(values)


def benchmark_block_sizes(file_path, expected=None, sizes=(4096, 16384, 65536)):
    """Compare HDFS block counts and end-to-end processing time for P.2.

    Reads identical source data for each experiment, preserving the original
    distributed_mapreduce_from_hdfs implementation and changing block size only.
    """
    import tempfile
    import time

    rows = []
    for block_size in sizes:
        with tempfile.TemporaryDirectory(prefix="mapreduce_hdfs_") as temp_dir:
            hdfs = SimulatedHDFS(base_dir=temp_dir, block_size=block_size,
                                 replication=1, num_nodes=2)
            started = time.perf_counter()
            hdfs.put(str(file_path), "/book.txt")
            upload_seconds = time.perf_counter() - started
            blocks = len(hdfs.get_blocks("/book.txt"))
            processing_start = time.perf_counter()
            results = distributed_mapreduce_from_hdfs(
                hdfs, "/book.txt", word_mapper, word_reducer,
                num_mappers=2, num_reducers=2
            )
            processing_seconds = time.perf_counter() - processing_start
            total_seconds = time.perf_counter() - started
            if expected is not None:
                assert results == expected, f"Word counts differ at {block_size} bytes"
            print(f"P.2 block={block_size} bytes; blocks={blocks}; "
                  f"upload={upload_seconds:.6f}s; "
                  f"processing={processing_seconds:.6f}s; "
                  f"total={total_seconds:.6f}s; unique_words={len(results)}")
            rows.append((block_size, blocks, upload_seconds,
                         processing_seconds, total_seconds))
    return rows


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python distributed_mapreduce.py <file1> [file2] [file3] ...")
        print("\nExample:")
        print("  python distributed_mapreduce.py ../../../../datasets/book/The\\ story\\ of\\ the\\ universe.txt")
        print("  python distributed_mapreduce.py file1.txt file2.txt file3.txt")
        sys.exit(1)
    
    input_files = sys.argv[1:]
    
    # Validate files exist
    for file_path in input_files:
        if not Path(file_path).exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
    
    # Initialize HDFS
    hdfs = SimulatedHDFS(
        base_dir="hdfs_storage",
        block_size=24576,  # 24KB blocks (8KB * 3)
        replication=3,
        num_nodes=6  # 6 nodes in the cluster
    )
    
    # Upload files to HDFS
    print("\n" + "="*70)
    print("UPLOADING FILES TO HDFS")
    print("="*70)
    
    hdfs_paths = []
    for i, file_path in enumerate(input_files):
        file_name = Path(file_path).name
        hdfs_path = f"/data/{file_name}"
        hdfs.put(file_path, hdfs_path)
        hdfs_paths.append(hdfs_path)
    
    # Process each file
    all_results = {}
    
    for hdfs_path in hdfs_paths:
        print("\n" + "="*70)
        print(f"PROCESSING FILE: {hdfs_path}")
        print("="*70)
        
        results = distributed_mapreduce_from_hdfs(
            hdfs,
            hdfs_path,
            word_mapper,
            word_reducer,
            num_mappers=4,
            num_reducers=2
        )
        
        # Merge results
        for word, count in results.items():
            all_results[word] = all_results.get(word, 0) + count
        
        print(f"\nTOP 10 WORDS IN {hdfs_path}:")
        print("-" * 40)
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)[:10]
        for word, count in sorted_results:
            print(f"{word:20} {count:5}")
    
    # Show combined results if multiple files
    if len(hdfs_paths) > 1:
        print("\n" + "="*70)
        print("COMBINED RESULTS FROM ALL FILES")
        print("="*70)
        print("\nTOP 20 WORDS OVERALL:")
        print("-" * 40)
        sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)[:20]
        for word, count in sorted_results:
            print(f"{word:20} {count:5}")
        
        print(f"\nTotal unique words: {len(all_results)}")
        print(f"Total word count: {sum(all_results.values())}")
    
    # Cleanup info
    print("\n" + "="*70)
    print("PROCESSING COMPLETE")
    print("="*70)
    print(f"\nHDFS storage location: {hdfs.base_dir}")
    print("To clean up: rm -rf hdfs_storage")

