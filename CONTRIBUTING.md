
# Contributing to HyParse

Thanks for your interest in contributing to **HyParse**!

We welcome meaningful contributions, but ask that you follow the delines below to maintain code quality and consistency.

---

## ✅ Contribution Guidelines

### 1. Minimum Test Coverage

- Every new **Python file** or **module** must come with **at least 5 test cases**.
- The number of test cases can vary based on the size and complexity of the file.
- Tests should be added in a `tests/` directory or inline if appropriate.
- Use `unittest`, `pytest`, or any standard testing framework.

### 2. Code Style & Quality

- Follow PEP8 for Python and appropriate conventions for C++.
- Write meaningful docstrings and comments where necessary.
- Avoid hardcoding values unless justified.

### 3. C++ Stubs for Performance-Sensitive Code

- If a section of Python code can potentially be optimized using C++,  
  **a stub `.cpp` file should be included with the same module name** as a placeholder or partial implementation.
- This helps future contributors identify performance bottlenecks and provides a roadmap for optimization.

### 4. Submitting Pull Requests

- Clearly describe what your PR does and why.
- Include all relevant test cases in the PR.
- Mention in the PR description:
  - What was tested
  - How the tests were structured
  - If any temp test files should be removed after merging

---

## ⚠️ Important

Test files **must be included in the pull request**, but **may be excluded from the final merged code** if they are meant for temporary verification.

---

> 💡 Build responsibly. Optimize when needed. Test always.
