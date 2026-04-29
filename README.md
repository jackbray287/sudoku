# Sudoku Solver

An interactive Streamlit app that solves and visualizes four sudoku variants using Gurobi as the integer programming solver, plus a runtime benchmarking tab.

## Tabs

| Tab | Description |
|-----|-------------|
| **Puzzle Variants** | Prime Sudoku, Naked Greater-Than Sudoku, Antisymmetric Sudoku, Checkerboard 16×16 Sudoku |
| **Standard Grids** | Randomly generated 9×9 or 16×16 puzzles with ~25% of cells revealed |
| **Runtime Analysis** | Benchmark Gurobi solve times vs. board size and number of given clues |

---

## Setup

### 1. Prerequisites

- **Python 3.9 or higher**
- **Gurobi license** (see [Step 4](#4-configure-gurobi-license))

Check your Python version:
```bash
python3 --version
```

---

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install streamlit gurobipy pandas numpy matplotlib
```

---

### 4. Configure Gurobi license

Gurobi requires a license to run. The free pip-bundled license is **size-limited** (max ~2,000 variables) and cannot solve the 16×16 puzzles or the Runtime Analysis benchmarks at full scale. You have two options:

#### Option A — Davidson College token server (recommended for Davidson students)

Create the file `~/gurobi.lic` with this single line:

```
TOKENSERVER=gurobilicense.davidson.edu
```

This borrows a full unrestricted license from Davidson's server. **You must be on Davidson WiFi or connected via VPN.**

#### Option B — Free academic license (9×9 puzzles only)

Register for a free academic license at [gurobi.com/academia](https://www.gurobi.com/academia/academic-program-and-licenses/) and follow Gurobi's activation instructions. The free license supports all 9×9 puzzles but will fail on the 16×16 Checkerboard and Standard 16×16 grids.

---

### 5. Run the app

```bash
streamlit run sudoku_app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`). Open it in your browser.

---

## Troubleshooting

**`GurobiError: Model too large for size-limited license`**
You are using the default pip license. Follow Step 4 to configure a full license.

**`GurobiError: No server available`** (when using token server)
You are not on Davidson WiFi or VPN. Connect and try again.

**`ModuleNotFoundError`**
Make sure your virtual environment is activated and all packages are installed (`pip install streamlit gurobipy pandas numpy matplotlib`).

**Streamlit opens but the page is blank**
Check the terminal for a Python error. The most common cause is a missing dependency or an import error.
