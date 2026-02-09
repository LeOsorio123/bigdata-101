# mrjob Installation and Setup Guide

## Prerequisites

- **Python 3.8 to 3.12** (mrjob is not compatible with Python 3.13+)
- pip (Python package manager)
- Terminal/Command line access

> **Important**: mrjob v0.7.4 uses the `pipes` module which was removed in Python 3.13. Make sure you're using Python 3.12 or earlier.

## Installation

### Recommended: Virtual environment + requirements.txt

```bash
# Navigate to the module directory
cd modules/01-mapreduce/02-mrjob

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import mrjob; print(mrjob.__version__)"
```

### Alternative: Direct pip install

If you prefer not to use a virtual environment:

```bash
pip install mrjob PyYAML
```

## Verify Installation

Run a simple test:

```bash
# Navigate to basics directory
cd 01-basics

# Run word count example
python mr_word_count.py ../../../datasets/mapreduce/sample_text.txt
```

If you see word counts in the output, installation was successful!

## Configuration (Optional)

### Create mrjob Configuration File

Create `~/.mrjob.conf` for persistent settings:

```yaml
runners:
  inline:
    # Default runner settings
    local_tmp_dir: /tmp/mrjob
  
  local:
    # Local runner (simulates Hadoop)
    num_cores: 4  # Use 4 CPU cores
    local_tmp_dir: /tmp/mrjob
```

Or in JSON format:

```json
{
  "runners": {
    "inline": {
      "local_tmp_dir": "/tmp/mrjob"
    },
    "local": {
      "num_cores": 4,
      "local_tmp_dir": "/tmp/mrjob"
    }
  }
}
```

### Configuration Locations

mrjob looks for configuration files in this order:
1. `/etc/mrjob.conf` (system-wide)
2. `~/.mrjob.conf` (user-specific)
3. `./mrjob.conf` (project-specific)
4. `--conf-path` command line argument

## Testing Your Setup

### Test 1: Basic Job

```bash
# Create test file
echo "hello world hello" > test.txt

# Run word count
python 01-basics/mr_word_count.py test.txt
```

**Expected output**:
```
"hello"	2
"world"	1
```

### Test 2: Local Runner

```bash
# Run with local runner (simulates Hadoop)
python 01-basics/mr_word_count.py -r local test.txt
```

Should produce same output but with Hadoop-like processing.

### Test 3: Multiple Files

```bash
# Create multiple test files
echo "hello world" > test1.txt
echo "hello python" > test2.txt

# Process both
python 01-basics/mr_word_count.py test1.txt test2.txt
```

## Common Installation Issues

### Issue: "ModuleNotFoundError: No module named 'pipes'"
## Common Installation Issues

### Issue 1: "ModuleNotFoundError: No module named 'pipes'"

**Problem**: You're using Python 3.13+, which removed the `pipes` module

**Solution**: Install and use Python 3.8 - 3.12

```bash
# Check your Python version
python3 --version

# If 3.13+, install Python 3.12 or earlier
# On macOS with Homebrew:
brew install python@3.12

# Create venv with specific Python version
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue 2: "ModuleNotFoundError: No module named 'mrjob'"

**Solution**: mrjob not installed or wrong Python environment

```bash
# Check Python version
python3 --version

# Install mrjob
pip install mrjob

# If using virtual environment, make sure it's activated
source .venv/bin/activate  # macOS/Linux
```

### Issue 3: "Permission denied" when installing

**Solution**: Use user installation or virtual environment

```bash
# User installation (no sudo needed)
pip install --user mrjob

# Or use virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
pip install mrjob
```

### Issue 4: pip not found

**Solution**: Install pip

```bash
# macOS
python3 -m ensurepip --upgrade

# Ubuntu/Debian
sudo apt-get install python3-pip

# Windows
# Download get-pip.py from https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```

### Issue 5: Python version too old

**Solution**: Upgrade to Python 3.8 - 3.12

```bash
# Check version
python3 --version

# If < 3.8, upgrade:
# macOS (using Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt-get install python3.12

# Windows
# Download from https://www.python.org/downloads/
```

## Optional Dependencies

### For AWS EMR (Cloud Deployment)

```bash
pip install boto3
```

### For Google Cloud Dataproc

```bash
pip install google-cloud-dataproc
```

### For YAML Configuration Files

```bash
pip install PyYAML
```

## IDE Setup

### VS Code

1. Install Python extension
2. Select Python interpreter (Ctrl+Shift+P → "Python: Select Interpreter")
3. Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click "+" to add mrjob package
3. Configure run configurations for mrjob scripts

## Environment Variables

Useful environment variables for mrjob:

```bash
# Set temporary directory
export TMPDIR=/path/to/tmp

# Set Python path
export PYTHONPATH=/path/to/your/project

# For AWS credentials (if using EMR)
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Upgrading mrjob

```bash
# Upgrade to latest version
pip install --upgrade mrjob

# Install specific version
pip install mrjob==0.7.4
```

## Uninstalling

```bash
# Uninstall mrjob
pip uninstall mrjob

# Remove configuration
rm ~/.mrjob.conf
```

## Next Steps

After successful installation:

1. ✅ Complete the examples in `01-basics/`
2. ✅ Try the exercises in `EXERCISES.md`
3. ✅ Explore multi-step jobs in `02-multistep/`
4. ✅ Build real applications in `03-applications/`

## Getting Help

- **Documentation**: https://mrjob.readthedocs.io/
- **GitHub Issues**: https://github.com/Yelp/mrjob/issues
- **Stack Overflow**: Tag your questions with `mrjob`

## Quick Reference

```bash
# Install
pip install mrjob

# Run job (inline)
python my_job.py input.txt

# Run job (local runner)
python my_job.py -r local input.txt

# Verbose output
python my_job.py -v input.txt

# Output to file
python my_job.py input.txt > output.txt

# Multiple inputs
python my_job.py file1.txt file2.txt file3.txt

# Using wildcards
python my_job.py data/*.txt

# Keep temp files for debugging
python my_job.py --no-cleanup input.txt
```

Happy MapReducing! 🎉
