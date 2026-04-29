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

You must be **physically on Davidson WiFi** (not VPN — the token server is not reachable off-campus).

**Step 1 — Create the license file**

Run the correct command for your OS in your terminal:

```bash
# macOS / Linux
echo "TOKENSERVER=gurobilicense.davidson.edu" > ~/gurobi.lic
```

```powershell
# Windows (PowerShell)
"TOKENSERVER=gurobilicense.davidson.edu" | Out-File -FilePath "$env:USERPROFILE\gurobi.lic" -Encoding ascii
```

**Step 2 — Verify it worked**

With your virtual environment activated, run:

```bash
python -c "import gurobipy as gp; m = gp.Model(); print('License OK')"
```

You should see `Set parameter TokenServer to value "gurobilicense.davidson.edu"` in the output, followed by `License OK`. If you see an error, double-check that you are on Davidson WiFi and that the file was created in the right location (`~` = your home directory, e.g. `/Users/yourname/gurobi.lic` on macOS).

**Step 3 — If it still fails**

Check whether a conflicting license file already exists somewhere else:

```bash
# macOS / Linux
find ~ -name "gurobi.lic" 2>/dev/null
echo "GRB_LICENSE_FILE=${GRB_LICENSE_FILE}"
```

If `GRB_LICENSE_FILE` is set in your environment, it overrides `~/gurobi.lic`. Unset it or point it to the file you just created.

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
The token server is only reachable on Davidson's campus WiFi network — VPN does not give access to it. Connect to Davidson WiFi and retry. Also confirm `~/gurobi.lic` contains exactly `TOKENSERVER=gurobilicense.davidson.edu` with no extra spaces or blank lines.

**`ModuleNotFoundError`**
Make sure your virtual environment is activated and all packages are installed (`pip install streamlit gurobipy pandas numpy matplotlib`).

**Streamlit opens but the page is blank**
Check the terminal for a Python error. The most common cause is a missing dependency or an import error.
