import copy
import random
from collections import deque
import tkinter as tk
from tkinter import messagebox

def random_start_state():
    nums  = list(range(9))
    random.shuffle(nums)
    start= [nums[0:3], nums[3:6], nums[6:9]]
    return start
start_state = random_start_state()
# print(start_state)
# print()

# start_state = [[2,8,3],
#               [1,6,4],
#               [7,0,5]]
goal = [[1,2,3],
        [8,0,4],
        [7,6,5]]

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
        if x < 2:
            lst_action.append('D')
        if x > 0:
            lst_action.append('U')
        if y < 2:
            lst_action.append('R')
        if y > 0:
            lst_action.append('L')
        return lst_action


class Node:
    def __init__(self, state, parent = 0, action = 0, path_cost = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    # def output(self):
    #     print("state: " + str(self.state))
    #     print("parent: " + str(self.parent))
    #     print("action: " + str(self.action))
    #     print("cost: " + str(self.path_cost))
    #     print("_____________________________")

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
    # Chuyển đổi list 2 chiều thành tuple của các tuple
    return tuple(tuple(row) for row in state)


def get_solution_path(goal_node):
    path = []
    current_node = goal_node

    while current_node != 0:
        step_info = {
            'action': current_node.action,
            'state': current_node.state
        }
        path.append(step_info)

        # Nhảy lùi về node cha
        current_node = current_node.parent

    path.reverse()

    return path


def print_matrix(state):
    for row in state:
        print(f" {row[0]}  {row[1]}  {row[2]} ")
    print("-" * 15)

def Breadth_First_Search(problem):
    node = Node(problem.state)
    if problem.goal_test(node.state):
        print("solution")
        # node.output()
        return node

    frontier = deque()
    frontier.append(node)

    frontier_states = {state_to_tuple(node.state)}

    explored = set()

    while len(frontier) != 0:
        node = frontier.popleft()

        current_state_tuple = state_to_tuple(node.state)
        frontier_states.remove(current_state_tuple)

        explored.add(current_state_tuple)

        for action in problem.Actions(node.state):
            CHILD = node_child(problem, node, action)
            child_state_tuple = state_to_tuple(CHILD.state)

            if (child_state_tuple not in explored) and (child_state_tuple not in frontier_states):
                if problem.goal_test(CHILD.state):
                    # CHILD.output()
                    print("solution")
                    return CHILD

                frontier.append(CHILD)
                frontier_states.add(child_state_tuple)
                # CHILD.output()
    print("Failure")
    return None

# new_problem = Problem(start_state, goal)
# goal_node = Breadth_First_Search(new_problem)
#
# if goal_node:
#     steps = get_solution_path(goal_node)
#
#     print(f"Tổng số bước di chuyển: {len(steps) - 1}\n")  # Trừ đi 1 state gốc
#
#     for i, step in enumerate(steps):
#         if i == 0:
#             print("STEP 0: Start State")
#         else:
#             print(f"STEP {i}: Di chuyển ô trống sang {step['action']}")
#
#         print_matrix(step['state'])
#         print()

class EightPuzzleGUI:
    def __init__(self, root, start_state, goal_state):
        self.root = root
        self.root.title("8-Puzzle Solver (BFS)")
        self.root.geometry("400x550")
        self.root.configure(bg="#f0f0f0")

        self.start_state = start_state
        self.goal_state = goal_state
        self.current_state = copy.deepcopy(start_state)

        # Biến để lưu trữ các bước giải
        self.solution_steps = []
        self.is_animating = False

        self.create_widgets()
        self.update_board(self.current_state)

    def create_widgets(self):
        # Khu vực chứa bàn cờ 3x3
        self.frame = tk.Frame(self.root, bg="#333", bd=5)
        self.frame.pack(pady=20)

        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.frame, text="", font=("Helvetica", 24, "bold"),
                                width=4, height=2, bg="white", fg="black",
                                state=tk.DISABLED)  # Khóa nút, chỉ để hiển thị
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[i][j] = btn

        # Label hiển thị trạng thái
        self.status_label = tk.Label(self.root, text="Nhấn Solve để bắt đầu tìm kiếm",
                                     font=("Arial", 12), bg="#f0f0f0", fg="#333")
        self.status_label.pack(pady=10)

        # Các nút điều khiển
        control_frame = tk.Frame(self.root, bg="#f0f0f0")
        control_frame.pack(pady=10)

        self.solve_btn = tk.Button(control_frame, text="Tự động giải (BFS)", font=("Arial", 12, "bold"),
                                   bg="#4CAF50", fg="white", command=self.solve)
        self.solve_btn.grid(row=0, column=0, padx=10)

        self.reset_btn = tk.Button(control_frame, text="Reset", font=("Arial", 12),
                                   command=self.reset_board)
        self.reset_btn.grid(row=0, column=1, padx=10)

    def update_board(self, state):
        """Cập nhật giao diện theo state hiện tại"""
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val == 0:
                    self.buttons[i][j].config(text="", bg="#e0e0e0")  # Ô trống
                else:
                    self.buttons[i][j].config(text=str(val), bg="white")

    def solve(self):
        if self.is_animating: return

        self.status_label.config(text="Đang tính toán... Vui lòng chờ", fg="blue")
        self.root.update()

        # Chạy thuật toán BFS
        problem = Problem(self.start_state, self.goal_state)
        goal_node = Breadth_First_Search(problem)

        if goal_node:
            self.solution_steps = get_solution_path(goal_node)
            self.status_label.config(text=f"Tìm thấy đích! Cần {len(self.solution_steps) - 1} bước.", fg="green")
            self.solve_btn.config(state=tk.DISABLED)

            # Bắt đầu chạy Animation từ bước 0
            self.is_animating = True
            self.animate_step(0)
        else:
            self.status_label.config(text="Không tìm thấy đường đi!", fg="red")
            messagebox.showerror("Lỗi", "Bài toán này vô nghiệm!")

    def animate_step(self, step_idx):
        """Hàm đệ quy dùng root.after để cập nhật từng khung hình"""
        if step_idx < len(self.solution_steps):
            step = self.solution_steps[step_idx]

            # Cập nhật bàn cờ
            self.update_board(step['state'])

            # Cập nhật text trạng thái
            if step_idx == 0:
                self.status_label.config(text="Trạng thái ban đầu")
            else:
                self.status_label.config(text=f"Bước {step_idx}: Di chuyển sang {step['action']}")

            # Hẹn giờ gọi lại hàm này sau 600ms (0.6 giây) cho bước tiếp theo
            self.root.after(600, self.animate_step, step_idx + 1)
        else:
            self.is_animating = False
            self.status_label.config(text="Đã giải xong!", fg="green")

    def reset_board(self):
        if self.is_animating: return
        self.start_state = random_start_state()
        self.current_state = copy.deepcopy(self.start_state)
        self.update_board(self.current_state)
        self.status_label.config(text="Đã Reset bàn cờ", fg="#333")
        self.solve_btn.config(state=tk.NORMAL)



if __name__ == "__main__":
    root = tk.Tk()
    app = EightPuzzleGUI(root, start_state, goal)
    root.mainloop()