import copy
import random
import heapq
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox

GOAL = [[1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]]

def random_start_state():
    nums = list(range(9))
    random.shuffle(nums)
    return [nums[0:3], nums[3:6], nums[6:9]]


def get_inversions(state):
    flat = [x for row in state for x in row if x != 0]
    return sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) if flat[i] > flat[j])


def can_solve(start, goal):
    return (get_inversions(start) % 2) == (get_inversions(goal) % 2)


def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j


def get_actions(state):
    x, y = find_zero(state)
    actions = []
    if x < 2: actions.append('D')
    if x > 0: actions.append('U')
    if y < 2: actions.append('R')
    if y > 0: actions.append('L')
    return actions


def apply_action(state, action):
    s = copy.deepcopy(state)
    x, y = find_zero(s)
    nx, ny = x, y
    if action == 'U':
        nx -= 1
    elif action == 'D':
        nx += 1
    elif action == 'L':
        ny -= 1
    elif action == 'R':
        ny += 1
    s[x][y], s[nx][ny] = s[nx][ny], s[x][y]
    return s


def trace_back(node):
    path = []
    cur = node
    while cur is not None:
        path.append({'state': cur['state'], 'action': cur['action']})
        cur = cur['parent']
    path.reverse()
    return path


def manhattan(state):
    pos = {}
    for i in range(3):
        for j in range(3):
            pos[GOAL[i][j]] = (i, j)
    cost = 0
    for i in range(3):
        for j in range(3):
            v = state[i][j]
            if v != 0:
                gi, gj = pos[v]
                cost += abs(i - gi) + abs(j - gj)
    return cost


def state_str(state):
    return ' '.join(str(v) for v in state[0]) + ' | ' + \
        ' '.join(str(v) for v in state[1]) + ' | ' + \
        ' '.join(str(v) for v in state[2])


# ─────────────────────────────────────────────────────
# ALGORITHMS — each yields snapshot dicts for live display
# snapshot = {
#   'exploring': node_dict,          # node being expanded
#   'frontier':  [node_dict, ...],   # current frontier (list copy)
#   'explored':  [state, ...],       # explored states so far
#   'children':  [node_dict, ...],   # children of current node
#   'goal_node': node_dict or None,
# }
# ─────────────────────────────────────────────────────

def bfs_gen(start):
    root = {'state': start, 'parent': None, 'action': None, 'cost': 0, 'g': 0, 'h': 0}
    if start == GOAL:
        yield {'exploring': root, 'frontier': [], 'explored': [], 'children': [], 'goal_node': root}
        return
    frontier = deque([root])
    frontier_set = {state_to_tuple(start)}
    explored_set = set()
    explored_list = []
    while frontier:
        node = frontier.popleft()
        k = state_to_tuple(node['state'])
        frontier_set.discard(k)
        explored_set.add(k)
        explored_list.append(node['state'])
        children = []
        goal_node = None
        for a in get_actions(node['state']):
            ns = apply_action(node['state'], a)
            nk = state_to_tuple(ns)
            if nk not in explored_set and nk not in frontier_set:
                child = {'state': ns, 'parent': node, 'action': a, 'cost': node['cost'] + 1, 'g': node['cost'] + 1,
                         'h': 0}
                children.append(child)
                if ns == GOAL:
                    goal_node = child
                    frontier.append(child)
                    frontier_set.add(nk)
                    break
                frontier.append(child)
                frontier_set.add(nk)
        yield {
            'exploring': node,
            'frontier': list(frontier),
            'explored': list(explored_list),
            'children': children,
            'goal_node': goal_node,
        }
        if goal_node:
            return


def dfs_gen(start):
    root = {'state': start, 'parent': None, 'action': None, 'cost': 0, 'g': 0, 'h': 0}
    if start == GOAL:
        yield {'exploring': root, 'frontier': [], 'explored': [], 'children': [], 'goal_node': root}
        return
    frontier = [root]
    explored_set = set()
    explored_list = []
    while frontier:
        node = frontier.pop()
        k = state_to_tuple(node['state'])
        if k in explored_set:
            continue
        explored_set.add(k)
        explored_list.append(node['state'])
        children = []
        goal_node = None
        if node['state'] == GOAL:
            yield {'exploring': node, 'frontier': list(frontier), 'explored': list(explored_list), 'children': [],
                   'goal_node': node}
            return
        for a in get_actions(node['state']):
            ns = apply_action(node['state'], a)
            nk = state_to_tuple(ns)
            if nk not in explored_set:
                child = {'state': ns, 'parent': node, 'action': a, 'cost': node['cost'] + 1, 'g': node['cost'] + 1,
                         'h': 0}
                children.append(child)
                frontier.append(child)
        yield {
            'exploring': node,
            'frontier': list(frontier),
            'explored': list(explored_list),
            'children': children,
            'goal_node': goal_node,
        }


def ids_gen(start):
    for depth_limit in range(200):
        root = {'state': start, 'parent': None, 'action': None, 'cost': 0, 'g': 0, 'h': 0}
        stack = [root]
        explored_map = {state_to_tuple(start): 0}
        explored_list = []
        cutoff = False
        found = False
        while stack:
            node = stack.pop()
            explored_list.append(node['state'])
            if node['state'] == GOAL:
                yield {'exploring': node, 'frontier': list(stack), 'explored': list(explored_list),
                       'children': [], 'goal_node': node, 'ids_depth': depth_limit}
                return
            children = []
            if node['cost'] >= depth_limit:
                cutoff = True
                yield {'exploring': node, 'frontier': list(stack), 'explored': list(explored_list),
                       'children': [], 'goal_node': None, 'ids_depth': depth_limit, 'cutoff': True}
                continue
            for a in get_actions(node['state']):
                ns = apply_action(node['state'], a)
                nk = state_to_tuple(ns)
                nc = node['cost'] + 1
                if nk not in explored_map or nc < explored_map[nk]:
                    explored_map[nk] = nc
                    child = {'state': ns, 'parent': node, 'action': a, 'cost': nc, 'g': nc, 'h': 0}
                    children.append(child)
                    stack.append(child)
            yield {'exploring': node, 'frontier': list(stack), 'explored': list(explored_list),
                   'children': children, 'goal_node': None, 'ids_depth': depth_limit}


class _HN:
    def __init__(self, f, node): self.f = f; self.node = node

    def __lt__(self, o): return self.f < o.f


def ucs_gen(start):
    root = {'state': start, 'parent': None, 'action': None, 'g': 0, 'h': manhattan(start), 'cost': 0}
    heap = [_HN(root['g'] + root['h'], root)]
    frontier_map = {state_to_tuple(start): root['g'] + root['h']}
    explored_set = set()
    explored_list = []
    while heap:
        item = heapq.heappop(heap)
        node = item.node
        k = state_to_tuple(node['state'])
        if k in explored_set:
            continue
        explored_set.add(k)
        explored_list.append(node['state'])
        frontier_map.pop(k, None)
        if node['state'] == GOAL:
            yield {'exploring': node, 'frontier': [i.node for i in heap],
                   'explored': list(explored_list), 'children': [], 'goal_node': node}
            return
        children = []
        for a in get_actions(node['state']):
            ns = apply_action(node['state'], a)
            nk = state_to_tuple(ns)
            if nk not in explored_set:
                g = node['g'] + 1
                h = manhattan(ns)
                f = g + h
                if nk not in frontier_map or f < frontier_map[nk]:
                    frontier_map[nk] = f
                    child = {'state': ns, 'parent': node, 'action': a, 'g': g, 'h': h, 'cost': g}
                    children.append(child)
                    heapq.heappush(heap, _HN(f, child))
        yield {'exploring': node, 'frontier': [i.node for i in heap],
               'explored': list(explored_list), 'children': children, 'goal_node': None}


# ─────────────────────────────────────────────────────
# GUI
# ─────────────────────────────────────────────────────
COLORS = {
    'bg': '#1e1e2e',
    'panel': '#27273a',
    'panel2': '#313244',
    'tile_num': '#cdd6f4',
    'tile_bg': '#45475a',
    'tile_empty': '#11111b',
    'tile_moved': '#89b4fa',
    'accent': '#89dceb',
    'green': '#a6e3a1',
    'red': '#f38ba8',
    'yellow': '#f9e2af',
    'orange': '#fab387',
    'text': '#cdd6f4',
    'muted': '#6c7086',
    'border': '#45475a',
    'frontier_bg': '#1a3a2a',
    'explored_bg': '#1a1a3a',
}

LABEL_FONT = ("Helvetica", 11)
BTN_FONT = ("Helvetica", 11, "bold")
MONO_FONT = ("Courier", 10)
MONO_SM = ("Courier", 9)

ANIM_DELAY = 400  # ms per step during animation


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle Unified Solver")
        self.configure(bg=COLORS['bg'])

        # Start fullscreen / maximized
        try:
            self.state('zoomed')  # Windows
        except Exception:
            self.attributes('-zoomed', True)  # Linux

        self.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.bind('<Escape>', lambda e: self._exit_fullscreen())

        self.start_state = self._new_solvable_state()
        self.solution = []
        self.anim_step = 0
        self.anim_job = None
        self.is_running = False
        self._gen = None  # search generator
        self._all_snaps = []  # all snapshots from generator
        self._path = None

        self._build_ui()
        self.update_idletasks()
        self._draw_board(self.start_state, None)
        self._draw_goal()

    def _new_solvable_state(self):
        s = random_start_state()
        while not can_solve(s, GOAL):
            s = random_start_state()
        return s

    def _toggle_fullscreen(self):
        state = self.attributes('-fullscreen')
        self.attributes('-fullscreen', not state)

    def _exit_fullscreen(self):
        self.attributes('-fullscreen', False)
        try:
            self.state('zoomed')
        except:
            pass

    # ──────────────────────────────────────────
    # UI BUILD
    # ──────────────────────────────────────────
    def _build_ui(self):
        # Root grid: row0=topbar, row1=main, row2=pathbar
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0, minsize=110)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)

        self._build_topbar()
        self._build_left_panel()
        self._build_right_panel()
        self._build_bottom_bar()

    # ── Top bar ───────────────────────────────
    def _build_topbar(self):
        top = tk.Frame(self, bg=COLORS['bg'], pady=6)
        top.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10)

        tk.Label(top, text="Thuat toan:", bg=COLORS['bg'],
                 fg=COLORS['text'], font=LABEL_FONT).pack(side='left', padx=(0, 4))

        self.algo_var = tk.StringVar(value='BFS')
        algo_cb = ttk.Combobox(top, textvariable=self.algo_var, state='readonly', width=35,
                               values=['BFS — Breadth-First Search',
                                       'DFS — Depth-First Search',
                                       'IDS — Iterative Deepening Search',
                                       'UCS — Uniform Cost Search (A* Manhattan)'])
        algo_cb.pack(side='left', padx=6)
        algo_cb.current(0)

        self.solve_btn = tk.Button(top, text="  Giai  ", font=BTN_FONT,
                                   bg=COLORS['green'], fg='#1e1e2e', relief='flat',
                                   padx=14, pady=4, command=self._on_solve)
        self.solve_btn.pack(side='left', padx=6)

        self.reset_btn = tk.Button(top, text="  Reset  ", font=BTN_FONT,
                                   bg=COLORS['panel2'], fg=COLORS['text'], relief='flat',
                                   padx=14, pady=4, command=self._on_reset)
        self.reset_btn.pack(side='left', padx=4)

        self.status_lbl = tk.Label(top, text="● Cho lenh", bg=COLORS['bg'],
                                   fg=COLORS['muted'], font=("Helvetica", 12))
        self.status_lbl.pack(side='left', padx=16)

        # stat summary inline
        for key, lbl, default in [('explored', 'Explored', '0'), ('frontier_cnt', 'Frontier', '0'),
                                  ('steps', 'Buoc giai', '—')]:
            tk.Label(top, text=lbl + ':', bg=COLORS['bg'], fg=COLORS['muted'],
                     font=("Helvetica", 10)).pack(side='left', padx=(12, 2))
            v = tk.StringVar(value=default)
            setattr(self, f'sv_{key}', v)
            tk.Label(top, textvariable=v, bg=COLORS['bg'], fg=COLORS['accent'],
                     font=("Helvetica", 12, "bold")).pack(side='left', padx=(0, 4))

    # ── Left panel: board + goal ───────────────
    def _build_left_panel(self):
        left = tk.Frame(self, bg=COLORS['bg'])
        left.grid(row=1, column=0, sticky='nsew', padx=(10, 4), pady=4)
        left.rowconfigure(0, weight=3)
        left.rowconfigure(1, weight=0)
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        # Board frame — canvas sized dynamically
        board_lf = tk.LabelFrame(left, text=" 8-Puzzle Board ",
                                 bg=COLORS['panel'], fg=COLORS['accent'],
                                 font=LABEL_FONT, bd=1, relief='solid')
        board_lf.grid(row=0, column=0, sticky='nsew', pady=(0, 4))
        board_lf.rowconfigure(0, weight=1)
        board_lf.columnconfigure(0, weight=1)

        self.board_canvas = tk.Canvas(board_lf, bg=COLORS['panel'], highlightthickness=0)
        self.board_canvas.grid(row=0, column=0, sticky='nsew', padx=8, pady=8)
        board_lf.bind('<Configure>', self._on_board_resize)

        self.step_lbl = tk.Label(left, text="Trang thai ban dau",
                                 bg=COLORS['bg'], fg=COLORS['muted'],
                                 font=("Helvetica", 12), pady=4)
        self.step_lbl.grid(row=1, column=0)

        # Goal frame
        goal_lf = tk.LabelFrame(left, text=" Goal State ",
                                bg=COLORS['panel'], fg=COLORS['muted'],
                                font=LABEL_FONT, bd=1, relief='solid')
        goal_lf.grid(row=2, column=0, sticky='nsew')
        goal_lf.rowconfigure(0, weight=1)
        goal_lf.columnconfigure(0, weight=1)

        self.goal_canvas = tk.Canvas(goal_lf, bg=COLORS['panel'], highlightthickness=0)
        self.goal_canvas.grid(row=0, column=0, sticky='nsew', padx=6, pady=6)
        goal_lf.bind('<Configure>', self._on_goal_resize)

        self._board_tile = 90  # default, updated on resize
        self._goal_tile = 45

    # ── Right panel: frontier + explored ──────
    def _build_right_panel(self):
        right = tk.Frame(self, bg=COLORS['bg'])
        right.grid(row=1, column=1, sticky='nsew', padx=(4, 10), pady=4)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=3)
        right.columnconfigure(1, weight=2)

        # Frontier
        fr_lf = tk.LabelFrame(right, text=" Frontier (hang doi / ngan xep) ",
                              bg=COLORS['panel'], fg=COLORS['green'],
                              font=LABEL_FONT, bd=1, relief='solid')
        fr_lf.grid(row=0, column=0, sticky='nsew', padx=(0, 4))
        fr_lf.rowconfigure(0, weight=1)
        fr_lf.columnconfigure(0, weight=1)
        self.frontier_text = tk.Text(fr_lf, bg=COLORS['panel'], fg=COLORS['green'],
                                     font=MONO_SM, relief='flat', state='disabled',
                                     wrap='none')
        sc3 = tk.Scrollbar(fr_lf, command=self.frontier_text.yview, bg=COLORS['panel'])
        self.frontier_text.configure(yscrollcommand=sc3.set)
        sc3.pack(side='right', fill='y')
        self.frontier_text.pack(fill='both', expand=True, padx=4, pady=4)

        # Explored
        ex_lf = tk.LabelFrame(right, text=" Explored (da tham) ",
                              bg=COLORS['panel'], fg=COLORS['tile_moved'],
                              font=LABEL_FONT, bd=1, relief='solid')
        ex_lf.grid(row=0, column=1, sticky='nsew', padx=(4, 0))
        ex_lf.rowconfigure(0, weight=1)
        ex_lf.columnconfigure(0, weight=1)
        self.explored_text = tk.Text(ex_lf, bg=COLORS['panel'], fg=COLORS['tile_moved'],
                                     font=MONO_SM, relief='flat', state='disabled',
                                     wrap='none')
        sc4 = tk.Scrollbar(ex_lf, command=self.explored_text.yview, bg=COLORS['panel'])
        self.explored_text.configure(yscrollcommand=sc4.set)
        sc4.pack(side='right', fill='y')
        self.explored_text.pack(fill='both', expand=True, padx=4, pady=4)

    # ── Bottom bar: path ──────────────────────
    def _build_bottom_bar(self):
        path_lf = tk.LabelFrame(self, text=" Duong di: Start -> Goal ",
                                bg=COLORS['panel'], fg=COLORS['accent'],
                                font=LABEL_FONT, bd=1, relief='solid')
        path_lf.grid(row=2, column=0, columnspan=2, sticky='ew',
                     padx=10, pady=(4, 8))
        path_lf.columnconfigure(0, weight=1)

        self.path_canvas = tk.Canvas(path_lf, bg=COLORS['panel'],
                                     height=80, highlightthickness=0)
        path_sb = tk.Scrollbar(path_lf, orient='horizontal',
                               command=self.path_canvas.xview,
                               bg=COLORS['panel'])
        path_sb.pack(side='bottom', fill='x')
        self.path_canvas.pack(side='top', fill='both', expand=True)
        self.path_canvas.configure(xscrollcommand=path_sb.set)

        self.path_inner = tk.Frame(self.path_canvas, bg=COLORS['panel'])
        self._path_win = self.path_canvas.create_window(
            (0, 0), window=self.path_inner, anchor='nw')
        self.path_inner.bind('<Configure>',
                             lambda e: self.path_canvas.configure(
                                 scrollregion=self.path_canvas.bbox('all')))

        tk.Label(self.path_inner, text="Chua co duong di...",
                 bg=COLORS['panel'], fg=COLORS['muted'],
                 font=LABEL_FONT).pack(padx=12, pady=20)

    # ──────────────────────────────────────────
    # RESIZE HANDLERS
    # ──────────────────────────────────────────
    def _on_board_resize(self, event):
        size = min(event.width - 16, event.height - 16)
        if size < 60: return
        self._board_tile = max(30, size // 3)
        self.board_canvas.configure(
            width=self._board_tile * 3 + 8, height=self._board_tile * 3 + 8)
        state = self.solution[self.anim_step - 1]['state'] if self.solution and self.anim_step > 0 else self.start_state
        action = self.solution[self.anim_step - 1]['action'] if self.solution and self.anim_step > 0 else None
        self._draw_board(state, action)

    def _on_goal_resize(self, event):
        size = min(event.width - 12, event.height - 12)
        if size < 30: return
        self._goal_tile = max(15, size // 3)
        self.goal_canvas.configure(
            width=self._goal_tile * 3 + 8, height=self._goal_tile * 3 + 8)
        self._draw_goal()

    # ──────────────────────────────────────────
    # DRAW HELPERS
    # ──────────────────────────────────────────
    def _draw_board(self, state, moved_action):
        c = self.board_canvas
        c.delete('all')
        T = self._board_tile
        zx, zy = find_zero(state)
        prev_zero = None
        if moved_action:
            px, py = zx, zy
            if moved_action == 'U':
                px += 1
            elif moved_action == 'D':
                px -= 1
            elif moved_action == 'L':
                py += 1
            elif moved_action == 'R':
                py -= 1
            prev_zero = (px, py)

        font_size = max(12, T // 3)
        tile_font = ("Helvetica", font_size, "bold")

        for i in range(3):
            for j in range(3):
                x0 = j * T + 4
                y0 = i * T + 4
                x1 = x0 + T - 4
                y1 = y0 + T - 4
                v = state[i][j]
                if v == 0:
                    fill, tc = COLORS['tile_empty'], COLORS['muted']
                elif prev_zero and (i, j) == prev_zero:
                    fill, tc = COLORS['tile_moved'], '#1e1e2e'
                else:
                    fill, tc = COLORS['tile_bg'], COLORS['tile_num']
                c.create_rectangle(x0, y0, x1, y1, fill=fill,
                                   outline=COLORS['border'], width=2, tags='tile')
                if v != 0:
                    c.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=str(v),
                                  font=tile_font, fill=tc, tags='tile')

    def _draw_goal(self):
        c = self.goal_canvas
        c.delete('all')
        T = self._goal_tile
        for i in range(3):
            for j in range(3):
                x0 = j * T + 4
                y0 = i * T + 4
                x1 = x0 + T - 4
                y1 = y0 + T - 4
                v = GOAL[i][j]
                fill = COLORS['tile_empty'] if v == 0 else COLORS['tile_bg']
                c.create_rectangle(x0, y0, x1, y1, fill=fill,
                                   outline=COLORS['border'], width=1)
                if v != 0:
                    fs = max(8, T // 4)
                    c.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=str(v),
                                  font=("Helvetica", fs, "bold"), fill=COLORS['muted'])

    # ──────────────────────────────────────────
    # PANEL TEXT HELPERS
    # ──────────────────────────────────────────
    def _set_text(self, widget, content):
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('end', content)
        widget.configure(state='disabled')

    def _node_line(self, node):
        """Format a node into a compact display string."""
        s = node['state']
        row0 = ' '.join(str(x) for x in s[0])
        row1 = ' '.join(str(x) for x in s[1])
        row2 = ' '.join(str(x) for x in s[2])
        info = f"g={node.get('g', 0)}"
        if node.get('h', 0):
            info += f" h={node['h']} f={node['g'] + node['h']}"
        action = node.get('action') or 'start'
        return f"[{row0}]\n[{row1}]  via:{action} {info}\n[{row2}]\n"

    def _state_line(self, state, idx):
        r0 = ' '.join(str(x) for x in state[0])
        r1 = ' '.join(str(x) for x in state[1])
        r2 = ' '.join(str(x) for x in state[2])
        return f"#{idx:>3}: [{r0}|{r1}|{r2}]\n"

    def _fmt_state_inline(self, state):
        """Format state as [[r0] | [r1] | [r2]]"""
        r0 = ','.join(str(x) for x in state[0])
        r1 = ','.join(str(x) for x in state[1])
        r2 = ','.join(str(x) for x in state[2])
        return f"[[{r0}] | [{r1}] | [{r2}]]"

    def _update_panels(self, snap):

        # Frontier
        frontier = snap.get('frontier', [])
        self.sv_frontier_cnt.set(str(len(frontier)))
        fr_txt = f'[Frontier: {len(frontier)} nodes]\n\n'
        for node in reversed(frontier[-100:]):
            s = node['state']
            state_str = self._fmt_state_inline(s)
            parent = node.get('parent')
            parent_str = self._fmt_state_inline(parent['state']) if parent else 'None'
            action = node.get('action') or '-'
            cost = node.get('g', node.get('cost', 0))
            fr_txt += f"{state_str}, {parent_str}, {action}, {cost}\n"
        if len(frontier) > 100:
            fr_txt += f"... (+{len(frontier) - 100} more)\n"
        self._set_text(self.frontier_text, fr_txt)

        # Explored
        explored = snap.get('explored', [])
        self.sv_explored.set(str(len(explored)))
        ex_txt = f'[Explored: {len(explored)} states]\n\n'
        for state in reversed(explored[-150:]):
            ex_txt += self._fmt_state_inline(state) + '\n'
        if len(explored) > 150:
            ex_txt += f"... (+{len(explored) - 150} more)\n"
        self._set_text(self.explored_text, ex_txt)

        # IDS info
        if 'ids_depth' in snap:
            extra = ' [CUTOFF]' if snap.get('cutoff') else ''
            self._set_status(f'IDS depth={snap["ids_depth"]}{extra}', COLORS['yellow'])

    # ──────────────────────────────────────────
    # PATH RENDER
    # ──────────────────────────────────────────
    def _render_path(self, path):
        for w in self.path_inner.winfo_children():
            w.destroy()
        MINI = 20
        GAP = 2
        for idx, step in enumerate(path):
            if idx > 0:
                tk.Label(self.path_inner, text="->",
                         bg=COLORS['panel'], fg=COLORS['muted'],
                         font=("Helvetica", 13)).pack(side='left', padx=2)
            cell = tk.Frame(self.path_inner, bg=COLORS['panel'])
            cell.pack(side='left', padx=2, pady=4)
            cv = tk.Canvas(cell, width=MINI * 3 + GAP * 2 + 2,
                           height=MINI * 3 + GAP * 2 + 2,
                           bg=COLORS['panel'], highlightthickness=0)
            cv.pack()
            zx, zy = find_zero(step['state'])
            prev_zero = None
            if step['action']:
                px, py = zx, zy
                if step['action'] == 'U':
                    px += 1
                elif step['action'] == 'D':
                    px -= 1
                elif step['action'] == 'L':
                    py += 1
                elif step['action'] == 'R':
                    py -= 1
                prev_zero = (px, py)
            for r in range(3):
                for cc in range(3):
                    x0 = cc * (MINI + GAP) + 1;
                    y0 = r * (MINI + GAP) + 1
                    x1 = x0 + MINI;
                    y1 = y0 + MINI
                    v = step['state'][r][cc]
                    if v == 0:
                        fill, tc = COLORS['tile_empty'], COLORS['muted']
                    elif prev_zero and (r, cc) == prev_zero:
                        fill, tc = COLORS['tile_moved'], '#1e1e2e'
                    else:
                        fill, tc = COLORS['tile_bg'], COLORS['tile_num']
                    cv.create_rectangle(x0, y0, x1, y1, fill=fill, outline=COLORS['border'], width=1)
                    if v != 0:
                        cv.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=str(v),
                                       font=("Helvetica", 8, "bold"), fill=tc)
            lbl = step['action'] if step['action'] else 'Start'
            tk.Label(cell, text=lbl, bg=COLORS['panel'], fg=COLORS['accent'],
                     font=("Courier", 8)).pack()

    # ──────────────────────────────────────────
    # STATUS
    # ──────────────────────────────────────────
    def _set_status(self, msg, color=None):
        self.status_lbl.config(text=msg, fg=color or COLORS['muted'])

    # ──────────────────────────────────────────
    # BUTTON CALLBACKS
    # ──────────────────────────────────────────
    def _on_reset(self):
        if self.is_running: return
        if self.anim_job:
            self.after_cancel(self.anim_job)
            self.anim_job = None
        self.start_state = self._new_solvable_state()
        self.solution = []
        self.anim_step = 0
        self._path = None
        self._draw_board(self.start_state, None)
        self.step_lbl.config(text="Trang thai ban dau")
        for w in self.path_inner.winfo_children(): w.destroy()
        tk.Label(self.path_inner, text="Chua co duong di...",
                 bg=COLORS['panel'], fg=COLORS['muted'],
                 font=LABEL_FONT).pack(padx=12, pady=20)
        self._set_text(self.frontier_text, '')
        self._set_text(self.explored_text, '')
        self.sv_explored.set('0')
        self.sv_frontier_cnt.set('0')
        self.sv_steps.set('—')
        self._set_status("● Cho lenh", COLORS['muted'])
        self.solve_btn.config(state='normal')

    def _on_solve(self):
        if self.is_running: return
        self.is_running = True
        self.solve_btn.config(state='disabled')
        self._set_status("⟳ Dang chay...", COLORS['yellow'])
        self.sv_explored.set('0')
        self.sv_frontier_cnt.set('0')
        self.sv_steps.set('—')
        self.update()

        algo_raw = self.algo_var.get().split(' ')[0].lower()

        # Run entire generator upfront (collect all snapshots)
        self._set_status("⟳ Dang tinh toan...", COLORS['yellow'])
        self.update()

        if algo_raw == 'bfs':
            gen = bfs_gen(self.start_state)
        elif algo_raw == 'dfs':
            gen = dfs_gen(self.start_state)
        elif algo_raw == 'ids':
            gen = ids_gen(self.start_state)
        else:
            gen = ucs_gen(self.start_state)

        self._all_snaps = list(gen)

        # Find the solution path
        goal_snap = None
        for snap in self._all_snaps:
            if snap.get('goal_node'):
                goal_snap = snap

        if not goal_snap:
            self._set_status("✗ Vo nghiem", COLORS['red'])
            messagebox.showerror("That bai", "Khong tim thay duong di!")
            self.is_running = False
            self.solve_btn.config(state='normal')
            return

        self._path = trace_back(goal_snap['goal_node'])
        self.sv_steps.set(str(len(self._path) - 1))
        self._render_path(self._path)

        # Show final search state in panels (last snapshot)
        self._update_panels(self._all_snaps[-1])
        self.sv_explored.set(str(len(self._all_snaps)))

        # Animate solution path directly (no per-snap replay)
        self._set_status("▶ Hien thi duong di giai...", COLORS['green'])
        self.anim_step = 0
        self._animate_solution()

    def _animate_solution(self):
        if self.anim_step >= len(self._path):
            self.is_running = False
            self._set_status("✓ Da giai xong!", COLORS['green'])
            self.solve_btn.config(state='normal')
            return
        step = self._path[self.anim_step]
        self._draw_board(step['state'], step['action'])
        if self.anim_step == 0:
            self.step_lbl.config(text="SOLUTION — Trang thai ban dau")
        else:
            self.step_lbl.config(
                text=f"SOLUTION — Buoc {self.anim_step}/{len(self._path) - 1}  |  Di chuyen: {step['action']}")
        self.anim_step += 1
        self.anim_job = self.after(ANIM_DELAY, self._animate_solution)


# ─────────────────────────────────────────────────────
if __name__ == '__main__':
    app = App()
    app.mainloop()