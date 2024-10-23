# CythonOptimizer

CythonOptimizer is a CI/CD tool designed to optimize Python projects by selectively cythonizing parts of the codebase. The primary goal is to reduce the size of the deployed package, increase execution speed, and strip away unused portions of large libraries.

## Features

- Automatic detection of Python files in a project
- Selective cythonization of code
- Removal of unused imports and dead code
- Integration with CI/CD pipelines
- Reduced package size and improved execution speed

## Installation

1. Ensure you have Python 3.7+ installed.

2. Install the required dependencies:

```bash
pip install cython numpy
```

3. Install the NumPy development headers:

   - On Ubuntu or Debian:
     ```
     sudo apt-get install python3-dev
     ```
   - On macOS (using Homebrew):
     ```
     brew install python
     ```
   - On Windows:
     The NumPy development headers should be included with the NumPy installation from pip.

4. Install CythonOptimizer:

```bash
pip install cython-optimizer
```

## Usage

```bash
cython_optimizer /path/to/your/project --output optimized_output
```

## Integration with CI/CD

To integrate CythonOptimizer into your CI/CD pipeline, add the following step to your pipeline configuration:

```yaml
- name: Optimize Python Project
  run: |
    pip install cython-optimizer
    cython_optimizer /path/to/your/project --output optimized_output
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.