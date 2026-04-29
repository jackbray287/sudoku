import streamlit as st
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

st.set_page_config(page_title="Sudoku Solver", layout="wide")
st.title("Sudoku Solver")

# ─── Constants (The Original Setup) ──────────────────────────────────────────

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]
T, F, N = True, False, None

PAIR_COLOR = {
    1: ("#c0392b", "#fff"), 9: ("#c0392b", "#fff"),
    2: ("#d35400", "#fff"), 8: ("#d35400", "#fff"),
    3: ("#b7950b", "#fff"), 7: ("#b7950b", "#fff"),
    4: ("#1a7a4a", "#fff"), 6: ("#1a7a4a", "#fff"),
    5: ("#6c3483", "#fff"),
}
PAIRS = [(1, 9), (2, 8), (3, 7), (4, 6), (5, 5)]

CB_PUZZLE = [
    [13, 0, 0, 0, 0, 8, 0, 0, 0, 0, 9, 0, 0, 0, 0, 4],
    [0, 11, 0, 0, 0, 0, 10, 0, 0, 0, 0, 7, 8, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 4, 13, 0, 0, 0, 0, 14, 0, 0],
    [0, 0, 0, 3, 2, 0, 0, 0, 0, 15, 0, 0, 0, 0, 12, 0],
    [1, 0, 0, 0, 0, 14, 0, 0, 0, 0, 7, 0, 0, 0, 0, 2],
    [0, 15, 0, 0, 0, 0, 8, 0, 0, 0, 0, 3, 6, 0, 0, 0],
    [0, 0, 11, 0, 0, 0, 0, 6, 15, 0, 0, 0, 0, 16, 0, 0],
    [0, 0, 0, 7, 10, 0, 0, 0, 0, 13, 0, 0, 0, 0, 8, 0],
    [15, 0, 0, 0, 0, 16, 0, 0, 0, 0, 3, 0, 0, 0, 0, 8],
    [0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 13, 2, 0, 0, 0],
    [0, 0, 7, 0, 0, 0, 0, 8, 5, 0, 0, 0, 0, 12, 0, 0],
    [0, 0, 0, 5, 6, 0, 0, 0, 0, 11, 0, 0, 0, 0, 4, 0],
    [11, 0, 0, 0, 0, 2, 0, 0, 0, 0, 13, 0, 0, 0, 0, 12],
    [0, 9, 0, 0, 0, 0, 16, 0, 0, 0, 0, 15, 10, 0, 0, 0],
    [0, 0, 13, 0, 0, 0, 0, 14, 9, 0, 0, 0, 0, 6, 0, 0],
    [0, 0, 0, 15, 8, 0, 0, 0, 0, 3, 0, 0, 0, 0, 14, 0],
]

# Original Hardcoded Data for Autofill
H_ORIGINAL = [
    [T, F, N, F, T, N, T, F], [T, F, N, F, F, N, F, T], [F, F, N, F, F, N, F, T],
    [T, T, N, T, F, N, F, T], [F, T, N, T, T, N, T, T], [F, T, N, F, F, N, T, F],
    [F, F, N, T, F, N, F, F], [F, T, N, F, T, N, F, F], [T, F, N, F, F, N, F, F],
]
V_ORIGINAL = [
    [F, F, F, T, T, F, T, T, T], [T, F, F, T, T, T, F, F, F], [N, N, N, N, N, N, N, N, N],
    [F, F, F, F, T, T, T, T, T], [T, F, T, T, F, F, F, T, T], [N, N, N, N, N, N, N, N, N],
    [T, T, T, F, F, T, F, T, T], [F, T, F, T, T, F, T, T, T],
]

# Mapping logic for interactive editors
H_SYMBOLS = {True: "<", False: ">", None: " "}
V_SYMBOLS = {True: "^", False: "v", None: " "}
INV_H = {v: k for k, v in H_SYMBOLS.items()}
INV_V = {v: k for k, v in V_SYMBOLS.items()}

# ─── Session State Initialization ─────────────────────────────────────────────

for _i in range(9):
    for _j in range(8):
        if f"h_sym_{_i}_{_j}" not in st.session_state:
            st.session_state[f"h_sym_{_i}_{_j}"] = H_SYMBOLS[H_ORIGINAL[_i][_j]]
for _i in range(8):
    for _j in range(9):
        if f"v_sym_{_i}_{_j}" not in st.session_state:
            st.session_state[f"v_sym_{_i}_{_j}"] = V_SYMBOLS[V_ORIGINAL[_i][_j]]

# ─── Solver functions ─────────────────────────────────────────────────────────

def solve_naked_sudoku(h_data, v_data):
    try:
        m = gp.Model("naked_sudoku")
        m.Params.LogToConsole = 0
        DIGITS, CELLS = range(1, 10), range(9)
        x = m.addVars(CELLS, CELLS, DIGITS, vtype=GRB.BINARY)
        v = {(i, j): gp.quicksum(k * x[i, j, k] for k in DIGITS) for i in CELLS for j in CELLS}

        for i in CELLS:
            for j in CELLS:
                m.addConstr(gp.quicksum(x[i, j, k] for k in DIGITS) == 1)
        for k in DIGITS:
            for i in CELLS:
                m.addConstr(gp.quicksum(x[i, j, k] for j in CELLS) == 1)
                m.addConstr(gp.quicksum(x[j, i, k] for j in CELLS) == 1)
        for bi in range(3):
            for bj in range(3):
                for k in DIGITS:
                    m.addConstr(gp.quicksum(x[3*bi+di, 3*bj+dj, k] for di in range(3) for dj in range(3)) == 1)

        for i in range(9):
            for j in range(8):
                val = INV_H.get(h_data.iloc[i, j])
                if val is True: m.addConstr(v[i, j+1] - v[i, j] >= 1)
                elif val is False: m.addConstr(v[i, j] - v[i, j+1] >= 1)

        for i in range(8):
            for j in range(9):
                val = INV_V.get(v_data.iloc[i, j])
                if val is True: m.addConstr(v[i+1, j] - v[i, j] >= 1)
                elif val is False: m.addConstr(v[i, j] - v[i+1, j] >= 1)

        m.optimize()
        if m.Status == GRB.OPTIMAL:
            sol = [[0] * 9 for _ in range(9)]
            for i in CELLS:
                for j in CELLS:
                    for k in DIGITS:
                        if x[i, j, k].X > 0.5:
                            sol[i][j] = k
            return sol
    except Exception as e:
        st.error(f"Gurobi error: {e}")
    return None

# ─── HTML Rendering (The "Pretty" Board) ──────────────────────────────────────

def render_board_html(h_df, v_df, sol=None):
    rows = []
    for i in range(9):
        cells = []
        for j in range(9):
            val = str(sol[i][j]) if sol else "?"
            thick, thin = "3px solid #222", "1px solid #ccc"
            border = f"border-top:{thick if i%3==0 else thin};border-bottom:{thick if i%3==2 else thin};border-left:{thick if j%3==0 else thin};border-right:{thick if j%3==2 else thin};"
            cells.append(f'<td style="width:45px;height:45px;text-align:center;font-size:18px;font-weight:bold;{border}background:#f8f9fa;">{val}</td>')
            if j < 8:
                sym = h_df.iloc[i, j]
                cells.append(f'<td style="width:20px;text-align:center;color:#e74c3c;font-weight:bold;">{sym if sym != " " else ""}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
        if i < 8:
            v_cells = []
            for j in range(9):
                sym = v_df.iloc[i, j]
                v_cells.append(f'<td style="height:20px;text-align:center;color:#e74c3c;font-weight:bold;">{sym if sym != " " else ""}</td>')
                if j < 8: v_cells.append('<td></td>')
            rows.append(f'<tr>{"".join(v_cells)}</tr>')

    return f'<div style="display:flex;justify-content:center;"><table style="border-collapse:collapse;font-family:monospace;">{"".join(rows)}</table></div>'


def render_prime_html(sol, given=None):
    rows = []
    for i in range(9):
        cells = []
        for j in range(9):
            val = str(sol[i][j]) if sol else ""
            is_given = given is not None and given[i][j] != 0
            thick, thin = "3px solid #222", "1px solid #ccc"
            border = (
                f"border-top:{thick if i%3==0 else thin};"
                f"border-bottom:{thick if i%3==2 else thin};"
                f"border-left:{thick if j%3==0 else thin};"
                f"border-right:{thick if j%3==2 else thin};"
            )
            bg = "#cfe2ff" if is_given else "#f8f9fa"
            fw = "bold" if is_given else "normal"
            cells.append(
                f'<td style="width:56px;height:48px;text-align:center;vertical-align:middle;'
                f'font-size:15px;font-weight:{fw};{border}background:{bg};">{val}</td>'
            )
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<div style="display:flex;justify-content:center;"><table style="border-collapse:collapse;font-family:monospace;">{"".join(rows)}</table></div>'


def solve_prime_sudoku(given):
    try:
        m = gp.Model("prime_sudoku")
        m.Params.LogToConsole = 0
        x = {(r, c, p): m.addVar(vtype=GRB.BINARY)
             for r in range(1, 10) for c in range(1, 10) for p in PRIMES}
        for r in range(1, 10):
            for c in range(1, 10):
                m.addConstr(gp.quicksum(x[r, c, p] for p in PRIMES) == 1)
        for r in range(1, 10):
            for p in PRIMES:
                m.addConstr(gp.quicksum(x[r, c, p] for c in range(1, 10)) == 1)
        for c in range(1, 10):
            for p in PRIMES:
                m.addConstr(gp.quicksum(x[r, c, p] for r in range(1, 10)) == 1)
        for br in [1, 4, 7]:
            for bc in [1, 4, 7]:
                for p in PRIMES:
                    m.addConstr(gp.quicksum(x[r, c, p]
                                            for r in range(br, br + 3)
                                            for c in range(bc, bc + 3)) == 1)
        for r in range(9):
            for c in range(9):
                if given[r][c] != 0:
                    m.addConstr(x[r + 1, c + 1, given[r][c]] == 1)
        m.optimize()
        if m.Status == GRB.OPTIMAL:
            sol = [[0] * 9 for _ in range(9)]
            for r in range(1, 10):
                for c in range(1, 10):
                    for p in PRIMES:
                        if x[r, c, p].X > 0.5:
                            sol[r - 1][c - 1] = p
            return sol
    except Exception as e:
        st.error(f"Gurobi error: {e}")
    return None


def solve_antisymmetric(seed_val: int):
    """Find a valid antisymmetric sudoku where cell(r,c) + cell(8-r,8-c) = 10."""
    try:
        m = gp.Model("antisym")
        m.Params.LogToConsole = 0
        DIGITS = range(1, 10)
        CELLS = range(9)
        x = m.addVars(CELLS, CELLS, DIGITS, vtype=GRB.BINARY)
        for r in CELLS:
            for c in CELLS:
                m.addConstr(gp.quicksum(x[r, c, k] for k in DIGITS) == 1)
        for r in CELLS:
            for k in DIGITS:
                m.addConstr(gp.quicksum(x[r, c, k] for c in CELLS) == 1)
        for c in CELLS:
            for k in DIGITS:
                m.addConstr(gp.quicksum(x[r, c, k] for r in CELLS) == 1)
        for br in range(3):
            for bc in range(3):
                for k in DIGITS:
                    m.addConstr(gp.quicksum(
                        x[3*br+dr, 3*bc+dc, k]
                        for dr in range(3) for dc in range(3)
                    ) == 1)
        val = {(r, c): gp.quicksum(k * x[r, c, k] for k in DIGITS) for r in CELLS for c in CELLS}
        for r in range(5):
            for c in CELLS:
                if r == 4 and c >= 5:
                    break
                m.addConstr(val[r, c] + val[8 - r, 8 - c] == 10)
        m.addConstr(x[0, 0, seed_val] == 1)
        m.optimize()
        if m.Status == GRB.OPTIMAL:
            return [
                [next(k for k in DIGITS if x[r, c, k].X > 0.5) for c in CELLS]
                for r in CELLS
            ]
        return None
    except Exception as e:
        st.error(f"Gurobi error: {e}")
        return None


def board_html_antisym(sol, spotlight=None):
    rows = []
    for r in range(9):
        cells = []
        for c in range(9):
            d = sol[r][c]
            bg, fg = PAIR_COLOR[d]
            if spotlight is not None:
                partner = 10 - spotlight
                if d != spotlight and d != partner:
                    bg, fg = "#e8e8e8", "#b0b0b0"
            thick, thin = "3px solid #111", "1px solid #999"
            bt = thick if r % 3 == 0 else thin
            bb = thick if r % 3 == 2 else thin
            bl = thick if c % 3 == 0 else thin
            br = thick if c % 3 == 2 else thin
            pr, pc = 8 - r, 8 - c
            tip = f"({r},{c})={d} ↔ ({pr},{pc})={sol[pr][pc]} sum={d+sol[pr][pc]}"
            cells.append(
                f'<td title="{tip}" style="width:54px;height:54px;text-align:center;'
                f'vertical-align:middle;font-size:22px;font-weight:bold;'
                f'color:{fg};background:{bg};cursor:default;'
                f'border-top:{bt};border-bottom:{bb};border-left:{bl};border-right:{br};">'
                f'{d}</td>'
            )
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        '<div style="display:flex;justify-content:center;margin:12px 0;">'
        '<table style="border-collapse:collapse;">'
        + "".join(rows)
        + "</table></div>"
    )


def solve_checkerboard(puzzle):
    try:
        m = gp.Model("checkerboard")
        m.Params.LogToConsole = 0
        N, BOX = 16, 4
        NUMS = range(1, N + 1)
        CELLS = range(N)
        odd_nums  = list(range(1, N + 1, 2))
        even_nums = list(range(2, N + 1, 2))

        x = m.addVars(CELLS, CELLS, NUMS, vtype=GRB.BINARY)

        for r in CELLS:
            for c in CELLS:
                m.addConstr(gp.quicksum(x[r, c, k] for k in NUMS) == 1)
        for r in CELLS:
            for k in NUMS:
                m.addConstr(gp.quicksum(x[r, c, k] for c in CELLS) == 1)
        for c in CELLS:
            for k in NUMS:
                m.addConstr(gp.quicksum(x[r, c, k] for r in CELLS) == 1)
        for br in range(0, N, BOX):
            for bc in range(0, N, BOX):
                for k in NUMS:
                    m.addConstr(gp.quicksum(
                        x[br + dr, bc + dc, k]
                        for dr in range(BOX) for dc in range(BOX)
                    ) == 1)

        for r in CELLS:
            for c in CELLS:
                if (r + c) % 2 == 0:
                    m.addConstr(gp.quicksum(x[r, c, k] for k in odd_nums) == 1)
                else:
                    m.addConstr(gp.quicksum(x[r, c, k] for k in even_nums) == 1)

        for r in CELLS:
            for c in CELLS:
                if puzzle[r][c] != 0:
                    m.addConstr(x[r, c, puzzle[r][c]] == 1)

        m.optimize()
        if m.Status == GRB.OPTIMAL:
            NUMS_L = list(NUMS)
            return [
                [next(k for k in NUMS_L if x[r, c, k].X > 0.5) for c in CELLS]
                for r in CELLS
            ]
        return None
    except Exception as e:
        st.error(f"Gurobi error: {e}")
        return None


def board_html_checkerboard(sol, given=None):
    N, BOX = 16, 4
    rows = []
    for r in range(N):
        cells = []
        for c in range(N):
            d = sol[r][c]
            is_given = given is not None and given[r][c] != 0
            if (r + c) % 2 == 0:
                bg = "#c8860a" if is_given else "#f5d87a"   # amber — odd cells
                fg = "#fff"   if is_given else "#7a4f00"
            else:
                bg = "#1a6aa8" if is_given else "#aed6f1"   # blue — even cells
                fg = "#fff"   if is_given else "#154360"

            thick = "2px solid #111"
            thin  = "1px solid #aaa"
            bt = thick if r % BOX == 0 else thin
            bb = thick if r % BOX == BOX - 1 else thin
            bl = thick if c % BOX == 0 else thin
            br = thick if c % BOX == BOX - 1 else thin
            fw = "bold" if is_given else "normal"
            cells.append(
                f'<td style="width:36px;height:36px;text-align:center;vertical-align:middle;'
                f'font-size:13px;font-weight:{fw};color:{fg};background:{bg};'
                f'border-top:{bt};border-bottom:{bb};border-left:{bl};border-right:{br};">'
                f'{d}</td>'
            )
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        '<div style="display:flex;justify-content:center;margin:12px 0;overflow-x:auto;">'
        '<table style="border-collapse:collapse;">'
        + "".join(rows)
        + "</table></div>"
    )


# ─── UI Layout ────────────────────────────────────────────────────────────────

problem = st.radio("Select a problem:", ["Prime Sudoku", "Naked Greater-Than Sudoku", "Antisymmetric Sudoku", "Checkerboard 16×16 Sudoku"], horizontal=True)
st.divider()

if problem == "Naked Greater-Than Sudoku":
    st.subheader("Naked Greater-Than Sudoku")
    st.write("Click any red inequality sign to change it, then hit **Solve Puzzle**.")

    # Build constraint DataFrames from current session state (used by solver + solution display)
    h_df = pd.DataFrame([
        [st.session_state.get(f"h_sym_{i}_{j}", " ") for j in range(8)]
        for i in range(9)
    ])
    v_df = pd.DataFrame([
        [st.session_state.get(f"v_sym_{i}_{j}", " ") for j in range(9)]
        for i in range(8)
    ])

    btn_col, _ = st.columns([1, 5])
    with btn_col:
        if st.button("Default Puzzle", key="reset_naked"):
            for i in range(9):
                for j in range(8):
                    st.session_state[f"h_sym_{i}_{j}"] = H_SYMBOLS[H_ORIGINAL[i][j]]
            for i in range(8):
                for j in range(9):
                    st.session_state[f"v_sym_{i}_{j}"] = V_SYMBOLS[V_ORIGINAL[i][j]]
            st.session_state.pop("naked_sol", None)
            st.rerun()

    CW = [3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    thick, thin = "3px solid #222", "1px solid #ccc"
    _sol = st.session_state.get("naked_sol", None)

    for i in range(9):
        # ── value row ──────────────────────────────────────────────────────────
        cols = st.columns(CW)
        for ci, col in enumerate(cols):
            with col:
                if ci % 2 == 0:
                    j = ci // 2
                    val = str(_sol[i][j]) if _sol else "?"
                    bt = thick if i % 3 == 0 else thin
                    bb = thick if i % 3 == 2 else thin
                    bl = thick if j % 3 == 0 else thin
                    br = thick if j % 3 == 2 else thin
                    st.markdown(
                        f'<div style="border-top:{bt};border-bottom:{bb};'
                        f'border-left:{bl};border-right:{br};height:45px;'
                        f'display:flex;align-items:center;justify-content:center;'
                        f'font-size:20px;font-weight:bold;background:#f8f9fa;">{val}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    j = (ci - 1) // 2
                    if H_ORIGINAL[i][j] is None:
                        st.markdown('<div style="height:45px;"></div>', unsafe_allow_html=True)
                    else:
                        st.selectbox(
                            " ", [" ", "<", ">"],
                            key=f"h_sym_{i}_{j}",
                            label_visibility="collapsed",
                        )

        # ── vertical-symbol row (skip box-boundary rows i=2,5) ─────────────
        if i < 8 and i not in (2, 5):
            sep_cols = st.columns(CW)
            for ci, col in enumerate(sep_cols):
                with col:
                    if ci % 2 == 0:
                        j = ci // 2
                        st.selectbox(
                            " ", [" ", "^", "v"],
                            key=f"v_sym_{i}_{j}",
                            label_visibility="collapsed",
                        )
                    else:
                        st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    st.caption("**< >** horizontal (left smaller/larger)  |  **^ v** vertical (top smaller/larger)  |  space = no constraint")

    if st.button("Solve Puzzle", type="primary", use_container_width=True):
        with st.spinner("Solving..."):
            result = solve_naked_sudoku(h_df, v_df)
        if result:
            st.session_state.naked_sol = result
            st.rerun()
        else:
            st.error("No solution found for these constraints.")

    if "naked_sol" in st.session_state:
        st.divider()
        st.success("Solution Found!")
        st.markdown("### Solution")
        st.markdown(render_board_html(h_df, v_df, sol=st.session_state.naked_sol), unsafe_allow_html=True)
        if st.button("Clear Solution"):
            del st.session_state.naked_sol
            st.rerun()

elif problem == "Prime Sudoku":
    st.subheader("Prime Sudoku")
    st.write(
        f"Each cell must contain one of the nine primes `{PRIMES}`. "
        "Fill in the known values — use **0** for empty cells — then click **Solve**."
    )

    if "prime_df" not in st.session_state:
        st.session_state.prime_df = pd.DataFrame(
            [[0] * 9 for _ in range(9)],
            columns=[str(j + 1) for j in range(9)],
            index=[str(i + 1) for i in range(9)],
        )

    col_cfg = {
        str(j + 1): st.column_config.SelectboxColumn(
            label=str(j + 1),
            options=[0] + PRIMES,
            required=True,
        )
        for j in range(9)
    }

    edited_prime = st.data_editor(
        st.session_state.prime_df,
        column_config=col_cfg,
        use_container_width=False,
        hide_index=False,
        key="prime_editor",
        height=375,
    )

    if st.button("Solve Puzzle", type="primary", use_container_width=True, key="btn_prime"):
        given = [[int(edited_prime.iloc[i, j]) for j in range(9)] for i in range(9)]
        st.session_state.prime_given = given
        st.session_state.pop("prime_sol", None)
        with st.spinner("Solving with Gurobi..."):
            sol = solve_prime_sudoku(given)
        if sol:
            st.session_state.prime_sol = sol
        else:
            st.error("No solution exists for the board you entered.")

    if "prime_sol" in st.session_state:
        st.divider()
        st.success("Solution Found!")
        st.markdown("### Solution")
        st.markdown(
            render_prime_html(
                st.session_state.prime_sol,
                st.session_state.get("prime_given"),
            ),
            unsafe_allow_html=True,
        )
        st.caption("Blue cells are the pre-filled given values.")
        if st.button("Clear Solution", key="clear_prime"):
            del st.session_state.prime_sol
            st.rerun()

elif problem == "Antisymmetric Sudoku":
    st.subheader("Antisymmetric Sudoku")
    st.write(
        "Every pair of cells mirrored through the center sums to **10** — "
        "so 1↔9, 2↔8, 3↔7, 4↔6, and 5 sits alone at the center. "
        "Pick a seed digit for the top-left corner and watch the color mirror emerge."
    )

    seed_col, btn_col, _ = st.columns([1, 1, 4])
    with seed_col:
        aseed = int(st.number_input(
            "Seed digit (1–9):", min_value=1, max_value=9, value=1, step=1, key="aseed_input"
        ))
    with btn_col:
        st.caption(f"(0,0) = **{aseed}**  →  (8,8) = **{10 - aseed}**")
        generate = st.button("Generate Board", type="primary", key="btn_antisym")

    # Color legend
    legend_parts = []
    for a, b in PAIRS:
        bg, fg = PAIR_COLOR[a]
        text = f"{a} ↔ {b}" if a != b else f"{a} center"
        legend_parts.append(
            f'<span style="background:{bg};color:{fg};padding:3px 14px;'
            f'border-radius:5px;font-weight:bold;margin-right:6px;">{text}</span>'
        )
    st.markdown("**Color legend:** " + "".join(legend_parts), unsafe_allow_html=True)

    if generate:
        with st.spinner("Solving with Gurobi..."):
            asol = solve_antisymmetric(aseed)
        if asol:
            st.session_state["asol"] = asol
            st.session_state["aseed_used"] = aseed
            st.session_state.pop("aspotlight", None)
        else:
            st.error("No solution found.")

    # Spotlight selector (above board, only when a solution exists)
    aspotlight = None
    if "asol" in st.session_state:
        choice = st.radio(
            "Spotlight a pair (dims all others):",
            [0, 1, 2, 3, 4, 5],
            format_func=lambda x: "Show all" if x == 0 else (
                f"{x} ↔ {10 - x}" if x != 5 else "5 (center)"
            ),
            horizontal=True,
            key="aspotlight",
        )
        aspotlight = None if choice == 0 else choice

    # Board
    if "asol" in st.session_state:
        sol = st.session_state["asol"]
        aseed_used = st.session_state["aseed_used"]

        st.markdown(board_html_antisym(sol, spotlight=aspotlight), unsafe_allow_html=True)
        st.caption("Hover a cell to see its symmetric partner and confirm the sum.")

        all_ok = all(sol[r][c] + sol[8-r][8-c] == 10 for r in range(9) for c in range(9))
        if all_ok:
            st.success(
                f"All 40 symmetric pairs verified — each sums to 10. "
                f"Seed **{aseed_used}** at (0,0), **{10 - aseed_used}** at (8,8)."
            )

        with st.expander("Show all symmetric pair values"):
            lines = []
            for r in range(4):
                for c in range(9):
                    a, b = sol[r][c], sol[8-r][8-c]
                    lines.append(f"({r},{c})={a}  +  ({8-r},{8-c})={b}  =  {a+b}")
            for c in range(4):
                a, b = sol[4][c], sol[4][8-c]
                lines.append(f"(4,{c})={a}  +  (4,{8-c})={b}  =  {a+b}")
            lines.append(f"(4,4)={sol[4][4]}  — center")
            st.code("\n".join(lines))

        if st.button("Clear Board", key="clear_antisym"):
            del st.session_state["asol"]
            st.rerun()

elif problem == "Checkerboard 16×16 Sudoku":
    st.subheader("Checkerboard 16×16 Sudoku")
    st.write(
        "A 16×16 sudoku (digits 1–16, with 4×4 boxes) plus a checkerboard parity rule: "
        "**amber cells** must contain odd numbers, **blue cells** must contain even numbers. "
        "Edit the clues below or use the default puzzle, then click **Solve**."
    )

    rc1, rc2, _ = st.columns([1, 1, 5])
    with rc1:
        if st.button("Load default puzzle", key="cb_load"):
            st.session_state["cb_df"] = pd.DataFrame(
                CB_PUZZLE,
                columns=[str(c + 1) for c in range(16)],
                index=[str(r + 1) for r in range(16)],
            )
            st.session_state.pop("cb_sol", None)
            st.rerun()
    with rc2:
        if st.button("Clear all clues", key="cb_clear_clues"):
            st.session_state["cb_df"] = pd.DataFrame(
                [[0] * 16 for _ in range(16)],
                columns=[str(c + 1) for c in range(16)],
                index=[str(r + 1) for r in range(16)],
            )
            st.session_state.pop("cb_sol", None)
            st.rerun()

    if "cb_df" not in st.session_state:
        st.session_state["cb_df"] = pd.DataFrame(
            CB_PUZZLE,
            columns=[str(c + 1) for c in range(16)],
            index=[str(r + 1) for r in range(16)],
        )

    col_cfg_cb = {
        str(c + 1): st.column_config.NumberColumn(
            label=str(c + 1), min_value=0, max_value=16, step=1, default=0
        )
        for c in range(16)
    }

    edited_cb = st.data_editor(
        st.session_state["cb_df"],
        column_config=col_cfg_cb,
        use_container_width=True,
        hide_index=False,
        key="cb_editor",
        height=600,
    )

    if st.button("Solve Puzzle", type="primary", use_container_width=True, key="btn_cb"):
        given_cb = [[int(edited_cb.iloc[r, c]) for c in range(16)] for r in range(16)]
        st.session_state["cb_given"] = given_cb
        st.session_state.pop("cb_sol", None)
        with st.spinner("Solving 16×16 checkerboard sudoku with Gurobi..."):
            sol_cb = solve_checkerboard(given_cb)
        if sol_cb:
            st.session_state["cb_sol"] = sol_cb
        else:
            st.error("No solution found for these clues.")

    if "cb_sol" in st.session_state:
        st.divider()
        st.success("Solution found!")
        st.markdown(
            board_html_checkerboard(
                st.session_state["cb_sol"],
                given=st.session_state.get("cb_given"),
            ),
            unsafe_allow_html=True,
        )
        st.caption("Bold darker cells are the given clues. Amber = odd, blue = even.")
        if st.button("Clear Solution", key="clear_cb"):
            del st.session_state["cb_sol"]
            st.rerun()
