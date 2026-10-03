# Pure Python MapReduce — Exercises

Solutions for every exercise in `modules/01-mapreduce/01-pure-python/EXERCISES.md`. The code uses the Python standard library and the **original frameworks provided by the instructor**; it needs no third-party installations.

## Contents

| Section | Exercise | Implementation |
|---|---|---|
| Level 1 | 1.1 character count; 1.2 long words; 1.3 mean sales; 1.4 temperature statistics; 1.5 category statistics | `level1.py` |
| Level 2 | 2.1 word-length distribution; 2.2 unique words per file; 2.3 inverted index | `level2.py` |
| Level 3 | 3.1 top-N; 3.2 bigrams; 3.3 web sessions; 3.4 anomaly detection | `level3.py` |
| Performance | P.1 sequential vs. parallel; P.2 HDFS block sizes 4, 16 and 64 KB | `performance.py` |

`common.py` provides shared helpers. All the exercise mappers and reducers include docstrings. The file-loading and distinct-word functions handle empty files as well as ordinary text.

## How to run (from the repository root in Codespaces)

```bash
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/level1.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/level2.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/level3.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/test_solutions.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/performance.py
```

The automated tests cover all 12 programming exercises and additional edge cases, including empty input and empty files. Performance experiments must be run separately; they use multiprocessing and take longer than the unit tests.

## Performance report: record your own Codespaces results

After running `performance.py`, save the actual console output or copy these values into your submission notes. **Times will vary by machine and run.**

- P.1 book file and number of lines; sequential time; parallel time; whether the results match.
- P.2 for **each** of 4, 16 and 64 KB: number of HDFS blocks, upload time, processing time, and total execution time (upload + processing). Also confirm that the word counts match. The simulated HDFS and original distributed MapReduce implementation are used without editing the professor's source files.

Do not infer from a single trial that parallelism or one block size is universally faster. These are measurements of this particular dataset, resource allocation and implementation.

## Interpretation notes for the supplied examples

**Expected-output examples:** Some example numbers in the instructor's `EXERCISES.md` are illustrative rather than generated from the supplied data. With the exact Exercise 1.1 input, case-insensitive alphabetic counting yields `a: 6` and `e: 6`. For the current text files, our documented normalization (lowercase and trim surrounding punctuation) produces **116** distinct words in `sample_text.txt` and **79** in `sample_bigdata.txt`. Inspect the actual input files when explaining any differences.

**Exercise 3.4:** The supplied three S1 sensor values include `99.9`, marked as anomalous in the example. However, applying the **exact specified rule** (absolute deviation strictly greater than two **population** standard deviations computed from the same group) cannot mark any reading in a group of only three values as anomalous. The code intentionally follows the required formula and explains the resulting empty anomalies list. Ask the instructor whether the illustrative label or the specified mathematical threshold is authoritative before changing the detector.

## GitHub submission workflow

Work is saved in `feature/mapreduce-all-exercises` in the student's **own copy** of the repository. A draft pull request can show and preserve the difference relative to `main`, but neither a merge nor permission to the instructor's GitLab repository is needed unless the instructor asks for it. If submitting a private-repository link, first ensure the instructor has access.
