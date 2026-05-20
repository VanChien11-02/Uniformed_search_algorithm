import random
import copy
import tkinter as tk
from tkinter import messagebox

def random_start_state():
    nums  = list(range(9))
    random.shuffle(nums)
    start= [nums[0:3], nums[3:6], nums[6:9]]
    return start
start_state = random_start_state()

goal = [[1, 2, 3],
        [8, 0, 4],
        [7, 6, 5]]


class Problem:
    def __init__(self, initial_state, goal_state):
        self.state = initial_state
        self.goal = goal_state

    def goal_test(self, state):
        return state == self.goal

    @staticmethod
    def getLocationNull(node_state):
        for i in range(3):
            for j in range(3):
                if node_state[i][j] == 0:
                    return i, j
        return None

    def Actions(self, state):
        x, y = self.getLocationNull(state)
        lst_action = []
        if x < 2: lst_action.append('D')
        if x > 0: lst_action.append('U')
        if y < 2: lst_action.append('R')
        if y > 0: lst_action.append('L')
        return lst_action


class Node:
    def __init__(self, state, parent=0, action=0, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost


def move(problem, node, action):
    x, y = problem.getLocationNull(node.state)
    if action == 'U':
        x -= 1
    elif action == 'D':
        x += 1
    elif action == 'L':
        y -= 1
    elif action == 'R':
        y += 1
    return x, y


def node_child(problem, node, action):
    parent_state = node.state
    x, y = problem.getLocationNull(parent_state)
    nx, ny = move(problem, node, action)
    child_state = copy.deepcopy(node.state)
    child_state[x][y], child_state[nx][ny] = child_state[nx][ny], child_state[x][y]
    return Node(state=child_state, parent=node, action=action, path_cost=node.path_cost + 1)


def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def get_solution_path(goal_node):
    path = []
    current_node = goal_node
    while current_node != 0:
        step_info = {'action': current_node.action, 'state': current_node.state}
        path.append(step_info)
        current_node = current_node.parent
    path.reverse()
    return path


# Tách riêng hàm DLS như của bạn
def Depth_limit_search(problem, i):
    node = Node(problem.state)
    result = False
    frontier = [node]
    explored = {state_to_tuple(node.state): 0}

    while len(frontier) > 0:
        current_node = frontier.pop()

        if problem.goal_test(current_node.state):
            return current_node

        if current_node.path_cost >= i:
            result = True
            continue

        for action in problem.Actions(current_node.state):
            CHILD = node_child(problem, current_node, action)
            child_tuple = state_to_tuple(CHILD.state)

            if (child_tuple not in explored) or (CHILD.path_cost < explored[child_tuple]):
                explored[child_tuple] = CHILD.path_cost
                frontier.append(CHILD)

    if result:
        return "CUTOFF"
    else:
        return None

class IDSPuzzleGUI:
    def __init__(self, root, start_state, goal_state):
        self.root = root
        self.root.title("8-Puzzle Solver (IDS)")
        self.root.geometry("380x520")
        self.root.configure(bg="#f4f4f9")

        self.start_state = start_state
        self.goal_state = goal_state
        self.current_state = copy.deepcopy(start_state)

        self.solution_steps = []
        self.is_animating = False
        self.is_searching = False
        self.current_depth = 0
        self.problem = Problem(self.start_state, self.goal_state)

        self.create_widgets()
        self.update_board(self.current_state)

    def create_widgets(self):
        # Header - Hiển thị độ sâu đang xét
        self.depth_label = tk.Label(self.root, text="Đang chờ lệnh...",
                                    font=("Helvetica", 14, "bold"), bg="#f4f4f9", fg="#d35400")
        self.depth_label.pack(pady=10)

        # Bàn cờ
        self.frame = tk.Frame(self.root, bg="#2c3e50", bd=5)
        self.frame.pack(pady=10)

        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.frame, text="", font=("Helvetica", 24, "bold"),
                                width=4, height=2, bg="white", fg="#2c3e50", state=tk.DISABLED)
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[i][j] = btn

        # Label trạng thái các bước đi
        self.status_label = tk.Label(self.root, text="Nhấn Solve để tìm kiếm",
                                     font=("Arial", 12), bg="#f4f4f9", fg="#333")
        self.status_label.pack(pady=10)

        # Các nút bấm
        control_frame = tk.Frame(self.root, bg="#f4f4f9")
        control_frame.pack(pady=10)

        self.solve_btn = tk.Button(control_frame, text="Tự động giải (IDS)", font=("Arial", 12, "bold"),
                                   bg="#27ae60", fg="white", command=self.start_ids_search)
        self.solve_btn.grid(row=0, column=0, padx=10)

        self.reset_btn = tk.Button(control_frame, text="Reset", font=("Arial", 12),
                                   command=self.reset_board)
        self.reset_btn.grid(row=0, column=1, padx=10)

    def update_board(self, state):
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val == 0:
                    self.buttons[i][j].config(text="", bg="#bdc3c7")  # Ô trống màu xám
                else:
                    self.buttons[i][j].config(text=str(val), bg="white")

    def start_ids_search(self):
        """Bắt đầu vòng lặp tìm kiếm IDS"""
        if self.is_animating or self.is_searching: return

        self.solve_btn.config(state=tk.DISABLED)
        self.is_searching = True
        self.current_depth = 0
        self.status_label.config(text="Đang tìm kiếm đường đi...", fg="blue")

        # Gọi hàm đệ quy để bắt đầu dò từng depth
        self.search_next_depth()

    def search_next_depth(self):
        """Hàm này thay thế cho vòng lặp while True của IDS để GUI không bị treo"""
        if not self.is_searching: return

        # Cập nhật GUI hiện Depth limit
        self.depth_label.config(text=f"Vòng lặp IDS - Depth Limit: {self.current_depth}")
        self.root.update()

        # Chạy DLS cho độ sâu hiện tại
        result = Depth_limit_search(self.problem, self.current_depth)

        if result == "CUTOFF":
            # Nếu bị ngắt (CUTOFF), tăng độ sâu lên 1
            self.current_depth += 1
            # Đặt lịch chạy lại hàm này sau 50ms để user kịp nhìn thấy số Depth nhảy
            self.root.after(50, self.search_next_depth)

        elif result is None:
            # Thất bại hoàn toàn
            self.depth_label.config(text="Bài toán vô nghiệm!")
            self.status_label.config(text="Không tìm thấy đường đi.", fg="red")
            self.is_searching = False
            self.solve_btn.config(state=tk.NORMAL)

        else:
            # Tìm thấy Node đích
            self.is_searching = False
            self.solution_steps = get_solution_path(result)
            self.depth_label.config(text=f"TÌM THẤY TẠI DEPTH: {self.current_depth}")
            self.status_label.config(text=f"Hoàn thành trong {len(self.solution_steps) - 1} bước!", fg="green")

            # Kích hoạt hiệu ứng di chuyển bàn cờ
            self.is_animating = True
            self.animate_step(0)

    def animate_step(self, step_idx):
        if step_idx < len(self.solution_steps):
            step = self.solution_steps[step_idx]

            self.update_board(step['state'])

            if step_idx == 0:
                self.status_label.config(text="STEP 0: Trạng thái ban đầu")
            else:
                self.status_label.config(text=f"STEP {step_idx}: Di chuyển ô trống sang {step['action']}")

            # Hẹn giờ gọi lại hàm sau 600ms
            self.root.after(600, self.animate_step, step_idx + 1)
        else:
            self.is_animating = False
            self.status_label.config(text="🎉 Đã giải xong!", fg="green")
            self.solve_btn.config(state=tk.NORMAL)

    def reset_board(self):
        if self.is_animating or self.is_searching: return
        self.current_state = random_start_state()
        self.update_board(self.current_state)
        self.depth_label.config(text="Đang chờ lệnh...")
        self.status_label.config(text="Đã Reset bàn cờ", fg="#333")
        self.solve_btn.config(state=tk.NORMAL)



if __name__ == "__main__":
    root = tk.Tk()
    app = IDSPuzzleGUI(root, start_state, goal)
    root.mainloop()