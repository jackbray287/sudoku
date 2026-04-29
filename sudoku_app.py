import streamlit as st
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import time
import random
import numpy as np
import matplotlib.pyplot as plt

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

SOLVED_9X9 = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

SOLVED_16X16 = [
    [13, 16, 15,  6,  5,  8,  1, 12,  3, 14,  9, 10, 11,  2,  7,  4],
    [ 4, 11, 14,  9, 16, 15, 10, 13, 12,  1,  2,  7,  8,  5,  6,  3],
    [ 5, 12,  1,  2,  7,  6,  3,  4, 13,  8, 11, 16, 15, 14,  9, 10],
    [ 8,  7, 10,  3,  2, 11, 14,  9,  4, 15,  6,  5, 16, 13, 12,  1],
    [ 1, 10,  5,  8, 15, 14, 13, 16, 11, 12,  7,  6,  9,  4,  3,  2],
    [14, 15, 12, 13,  4,  1,  8, 11,  2,  9, 16,  3,  6,  7, 10,  5],
    [ 9,  2, 11,  4,  3, 12,  7,  6, 15, 10,  5,  8,  1, 16, 13, 14],
    [16,  3,  6,  7, 10,  9,  2,  5, 14, 13,  4,  1, 12, 15,  8, 11],
    [15,  6,  9, 12, 13, 16, 11,  2,  1,  4,  3, 14,  7, 10,  5,  8],
    [10,  1,  8, 11, 14,  5,  4, 15,  6,  7, 12, 13,  2,  3, 16,  9],
    [ 3,  4,  7, 14,  1, 10,  9,  8,  5, 16, 15,  2, 13, 12, 11,  6],
    [ 2, 13, 16,  5,  6,  7, 12,  3, 10, 11,  8,  9, 14,  1,  4, 15],
    [11, 14,  3, 16,  9,  2, 15, 10,  7,  6, 13,  4,  5,  8,  1, 12],
    [ 6,  9,  4,  1, 12,  3, 16,  7,  8,  5, 14, 15, 10, 11,  2, 13],
    [ 7,  8, 13, 10, 11,  4,  5, 14,  9,  2,  1, 12,  3,  6, 15, 16],
    [12,  5,  2, 15,  8, 13,  6,  1, 16,  3, 10, 11,  4,  9, 14,  7],
]

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


def solve_plain_nxn(N, puzzle):
    """Solve a plain N×N sudoku (no extra constraints). Returns elapsed seconds."""
    BOX = int(N ** 0.5)
    try:
        m = gp.Model(f"plain_{N}")
        m.Params.LogToConsole = 0
        NUMS = range(1, N + 1)
        CELLS = range(N)
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
                        x[br+dr, bc+dc, k]
                        for dr in range(BOX) for dc in range(BOX)
                    ) == 1)
        for r in CELLS:
            for c in CELLS:
                if puzzle[r][c] != 0:
                    m.addConstr(x[r, c, puzzle[r][c]] == 1)
        t0 = time.perf_counter()
        m.optimize()
        return time.perf_counter() - t0
    except Exception:
        return float("nan")


def solve_std(N, puzzle):
    """Solve a plain N×N sudoku. Returns solution grid or None."""
    BOX = int(N ** 0.5)
    try:
        m = gp.Model(f"std_{N}")
        m.Params.LogToConsole = 0
        NUMS = range(1, N + 1)
        CELLS = range(N)
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
                        x[br+dr, bc+dc, k]
                        for dr in range(BOX) for dc in range(BOX)
                    ) == 1)
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


def board_html_standard(N, sol, given=None):
    BOX = int(N ** 0.5)
    cell_px = "36px" if N == 16 else "48px"
    font_px = "13px" if N == 16 else "18px"
    thick = "2px solid #111" if N == 16 else "3px solid #222"
    thin  = "1px solid #bbb"
    rows = []
    for r in range(N):
        cells = []
        for c in range(N):
            d = sol[r][c]
            is_given = given is not None and given[r][c] != 0
            display = str(d) if d != 0 else ""
            bg = "#2980b9" if is_given else "#f8f9fa"
            fg = "#fff"    if is_given else "#333"
            fw = "bold"    if is_given else "normal"
            bt  = thick if r % BOX == 0       else thin
            bb  = thick if r % BOX == BOX - 1 else thin
            bl  = thick if c % BOX == 0       else thin
            bri = thick if c % BOX == BOX - 1 else thin
            cells.append(
                f'<td style="width:{cell_px};height:{cell_px};text-align:center;'
                f'vertical-align:middle;font-size:{font_px};font-weight:{fw};'
                f'color:{fg};background:{bg};'
                f'border-top:{bt};border-bottom:{bb};border-left:{bl};border-right:{bri};">'
                f'{display}</td>'
            )
        rows.append(f"<tr>{''.join(cells)}</tr>")
    overflow = "overflow-x:auto;" if N == 16 else ""
    return (
        f'<div style="display:flex;justify-content:center;margin:12px 0;{overflow}">'
        '<table style="border-collapse:collapse;">'
        + "".join(rows)
        + "</table></div>"
    )


# ─── UI Layout ────────────────────────────────────────────────────────────────

main_tab1, main_tab2, main_tab3 = st.tabs(["Puzzle Variants", "Standard Grids", "Runtime Analysis"])

# ════ Puzzle Variants ══════════════════════════════════════════════════════════
with main_tab1:
    problem = st.radio(
        "Select a problem:",
        ["Prime Sudoku", "Naked Greater-Than Sudoku", "Antisymmetric Sudoku", "Checkerboard 16×16 Sudoku"],
        horizontal=True,
        key="problem_radio",
    )
    st.divider()

    if problem == "Naked Greater-Than Sudoku":
        st.subheader("Naked Greater-Than Sudoku")
        st.write("Click any red inequality sign to change it, then hit **Solve Puzzle**.")

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

# ════ Standard Grids ══════════════════════════════════════════════════════════
with main_tab2:
    sg_choice = st.radio(
        "Grid size:",
        ["9×9", "16×16"],
        horizontal=True,
        key="sg_radio",
    )
    st.divider()

    N_sg = 9 if sg_choice == "9×9" else 16
    solved_sg = SOLVED_9X9 if N_sg == 9 else SOLVED_16X16
    n_given_sg = int(N_sg * N_sg * 0.25)

    st.write(
        f"A plain **{N_sg}×{N_sg}** sudoku with **{n_given_sg} cells given** (~25%). "
        "Click **Generate** to randomly pick which cells are revealed as clues."
    )

    if st.button("Generate New Puzzle", type="primary", key="sg_gen"):
        all_cells_sg = [(r, c) for r in range(N_sg) for c in range(N_sg)]
        selected_sg = random.sample(all_cells_sg, n_given_sg)
        puzzle_sg = [[0] * N_sg for _ in range(N_sg)]
        for r, c in selected_sg:
            puzzle_sg[r][c] = solved_sg[r][c]
        st.session_state["sg_puzzle"] = puzzle_sg
        st.session_state["sg_N"] = N_sg
        st.session_state.pop("sg_sol", None)
        st.rerun()

    if "sg_puzzle" in st.session_state and st.session_state.get("sg_N") == N_sg:
        puzzle_sg = st.session_state["sg_puzzle"]
        n_clues = sum(1 for r in range(N_sg) for c in range(N_sg) if puzzle_sg[r][c] != 0)
        st.markdown(board_html_standard(N_sg, puzzle_sg, given=puzzle_sg), unsafe_allow_html=True)
        st.caption(f"{n_clues} of {N_sg*N_sg} cells given ({n_clues/(N_sg*N_sg)*100:.0f}%)")

        if st.button("Solve", type="primary", key="sg_solve"):
            with st.spinner(f"Solving {N_sg}×{N_sg} with Gurobi..."):
                sg_sol = solve_std(N_sg, puzzle_sg)
            if sg_sol:
                st.session_state["sg_sol"] = sg_sol
            else:
                st.error("No solution found.")

        if "sg_sol" in st.session_state:
            st.divider()
            st.success("Solution found!")
            st.markdown(
                board_html_standard(N_sg, st.session_state["sg_sol"], given=puzzle_sg),
                unsafe_allow_html=True,
            )
            st.caption("Blue cells are the given clues.")
            if st.button("Clear Solution", key="sg_clear"):
                del st.session_state["sg_sol"]
                st.rerun()
    else:
        st.info(f"Click **Generate New Puzzle** to create a random {N_sg}×{N_sg} puzzle.")

# ════ Runtime Analysis ════════════════════════════════════════════════════════
with main_tab3:
    st.subheader("Gurobi Runtime Analysis")
    st.write("Benchmark solve times as board size and number of given cells vary.")

    tab1, tab2 = st.tabs(["Board Size Scaling", "Given Cells (9×9)"])

    with tab1:
        st.write(
            "Solve an empty N×N sudoku (no given clues — find any valid solution) "
            "for N = 4, 9, and 16. Each size is timed over multiple trials."
        )
        trials_size = st.slider("Trials per size:", 1, 10, 5, key="rt_size_trials")

        if st.button("Run Benchmark", type="primary", key="run_size_bench"):
            sizes = [4, 9, 16]
            data = {}
            prog = st.progress(0, text="Benchmarking…")
            total = len(sizes) * trials_size
            done = 0
            for N in sizes:
                empty = [[0] * N for _ in range(N)]
                times = []
                for _ in range(trials_size):
                    times.append(solve_plain_nxn(N, empty) * 1000)
                    done += 1
                    prog.progress(done / total, text=f"N={N} — trial {done}")
                data[N] = times
            prog.empty()
            st.session_state["rt_size_data"] = data

        if "rt_size_data" in st.session_state:
            data = st.session_state["rt_size_data"]
            sizes = sorted(data.keys())
            means = [np.mean(data[n]) for n in sizes]
            stds  = [np.std(data[n])  for n in sizes]

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar([str(n) for n in sizes], means, yerr=stds,
                   color=["#3498db", "#e67e22", "#e74c3c"],
                   capsize=6, edgecolor="#222", linewidth=0.8)
            for i, (m, s) in enumerate(zip(means, stds)):
                ax.text(i, m + s + max(means) * 0.02,
                        f"{m:.1f} ms", ha="center", va="bottom", fontsize=9)
            ax.set_xlabel("Board size (N×N)", fontsize=11)
            ax.set_ylabel("Solve time (ms)", fontsize=11)
            ax.set_title("Gurobi solve time vs. board size\n(empty puzzle, no given clues)", fontsize=12)
            ax.spines[["top", "right"]].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            with st.expander("Raw times (ms)"):
                for n in sizes:
                    st.write(f"**{n}×{n}**: " + ", ".join(f"{t:.2f}" for t in data[n]))

    with tab2:
        st.write(
            "Solve 9×9 puzzles derived from a fixed solution, varying the number of "
            "cells revealed as clues. Each clue count is timed over multiple trials "
            "with a fresh random selection of cells each trial."
        )
        c1, c2 = st.columns(2)
        with c1:
            trials_given = st.slider("Trials per clue count:", 1, 10, 5, key="rt_given_trials")
        with c2:
            step = st.select_slider("Clue count step:", [5, 10, 15], value=5, key="rt_given_step")

        if st.button("Run Benchmark", type="primary", key="run_given_bench"):
            all_cells = [(r, c) for r in range(9) for c in range(9)]
            k_values = list(range(0, 76, step))
            data_g = {}
            prog = st.progress(0, text="Benchmarking…")
            total = len(k_values) * trials_given
            done = 0
            for k in k_values:
                times = []
                for _ in range(trials_given):
                    selected = random.sample(all_cells, k)
                    puzzle = [[0] * 9 for _ in range(9)]
                    for r, c in selected:
                        puzzle[r][c] = SOLVED_9X9[r][c]
                    times.append(solve_plain_nxn(9, puzzle) * 1000)
                    done += 1
                    prog.progress(done / total, text=f"{k} clues — trial {done}")
                data_g[k] = times
            prog.empty()
            st.session_state["rt_given_data"] = data_g

        if "rt_given_data" in st.session_state:
            data_g = st.session_state["rt_given_data"]
            ks    = sorted(data_g.keys())
            means = np.array([np.mean(data_g[k]) for k in ks])
            stds  = np.array([np.std(data_g[k])  for k in ks])

            fig, ax1 = plt.subplots(figsize=(8, 4))
            ax1.plot(ks, means, color="#2980b9", linewidth=2, marker="o", markersize=5)
            ax1.fill_between(ks, np.maximum(means - stds, 0), means + stds,
                             color="#2980b9", alpha=0.15)
            ax1.set_xlabel("Number of given cells (out of 81)", fontsize=11)
            ax1.set_ylabel("Solve time (ms)", fontsize=11)
            ax1.set_title("Gurobi solve time vs. number of given clues (9×9)", fontsize=12)
            ax1.spines[["top", "right"]].set_visible(False)

            ax2 = ax1.twiny()
            ax2.set_xlim(ax1.get_xlim())
            tick_ks = [k for k in ks if k % 20 == 0 or k == ks[-1]]
            ax2.set_xticks(tick_ks)
            ax2.set_xticklabels([f"{k/81*100:.0f}%" for k in tick_ks], fontsize=8)
            ax2.set_xlabel("% of cells given", fontsize=9)

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            with st.expander("Raw times (ms)"):
                for k in ks:
                    st.write(f"**{k} clues**: " + ", ".join(f"{t:.2f}" for t in data_g[k]))
