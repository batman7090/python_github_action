# Python GitHub Actions Playground

A tiny Python package (a calculator with `add`, `subtract`, `multiply`, `divide`) used as a **sandbox for learning GitHub Actions** — automated testing, CI pipelines, and workflow syntax — rather than as a real library.

> 📚 If you're here to learn GitHub Actions: skip to the [CI Pipeline](#-ci-pipeline-explained) section — that's the real point of this repo.

---

## 📁 Project Structure

```
python_github_action/
├── .github/
│   └── workflows/
│       └── python-ci.yml      # GitHub Actions CI pipeline definition
├── src/
│   ├── __init__.py            # Exposes add, subtract, multiply, divide
│   └── funcs.py                # The actual function implementations
├── tests/
│   └── test_functions.py      # Pytest test suite
├── requirements.txt            # Project dependencies (pytest, etc.)
├── pytest.ini                  # Tells pytest where to find the src package
└── README.md
```

---

## ✨ What's in the package

| Function | Signature | Description |
|---|---|---|
| `add` | `add(a: float, b: float) -> float` | Returns `a + b` |
| `subtract` | `subtract(a: float, b: float) -> float` | Returns `a - b` |
| `multiply` | `multiply(a: float, b: float) -> float` | Returns `a * b` |
| `divide` | `divide(a: float, b: float) -> float` | Returns `a / b` |

```python
from src import add, subtract, multiply, divide

add(2, 3)        # 5
subtract(5, 3)    # 2
multiply(2, 5)    # 10
divide(6, 3)      # 2.0
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/python_github_action.git
cd python_github_action
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the tests locally

```bash
pytest
```

You should see all tests pass:

```
======================== test session starts ========================
collected 4 items

tests/test_functions.py ....                                   [100%]

========================= 4 passed in 0.05s ==========================
```

---

## ⚙️ CI Pipeline (explained)

Every push or pull request to `main` triggers `.github/workflows/python-ci.yml`, which automatically:

1. **Checks out the code** — `actions/checkout`
2. **Sets up Python** — `actions/setup-python`
3. **Installs dependencies** — `pip install -r requirements.txt`
4. **Runs the test suite** — `pytest`

```yaml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v7

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest
```

This means **every change is automatically tested** before it's merged — no more "it works on my machine."

### Why `pytest.ini` exists

Without it, pytest run from `tests/` can't resolve `from src import ...`, because the project root isn't on Python's import path by default. `pytest.ini` fixes this with:

```ini
[pytest]
pythonpath = .
```

This works identically whether you run `pytest` locally or in CI — which is exactly the kind of "gotcha" this repo exists to surface and learn from.

---

## 🎯 What this repo is meant to teach

- ✅ Structuring a Python package with `src/` + `tests/`
- ✅ Writing unit tests with `pytest`
- ✅ Triggering workflows on `push` / `pull_request`
- ✅ Reading and debugging CI logs in the GitHub Actions tab
- ✅ Common pitfalls: import errors in CI, malformed `run:` commands, missing files
- ✅ Workflow syntax: jobs, steps, `uses` vs `run`, `with`, `env`

---
