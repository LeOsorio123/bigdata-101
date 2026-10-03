# Solutions for EXERCISES.md (pure Python)

All three levels plus two performance experiments. Uses only the Python standard library and the instructor's original MapReduce modules.

Run from the repository root:

```bash
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/level1.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/level2.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/level3.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/test_solutions.py
python3 modules/01-mapreduce/01-pure-python/solutions_all_levels/performance.py
```

- Level 1: exercises 1.1–1.5
- Level 2: exercises 2.1–2.3; reads repository text datasets
- Level 3: exercises 3.1–3.4
- Performance: sequential versus parallel MapReduce, and simulated HDFS block sizes (4, 16 and 64 KB). Record timing data from your own Codespace; it varies by environment.

**Anomaly detection:** With the specified threshold of more than two population standard deviations, the provided three-value S1 example yields no outliers. The high reading is included in its own mean and SD, making the threshold unreachable in that three-value sample.

Work in the feature branch and create a pull request to your own private main; do not change the instructor's repository.
