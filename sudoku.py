import tkinter as tk
from tkinter import messagebox
import random
import time

CONFIG = {
    "EASY": {
        "N": 4,
        "BOX_H": 2, "BOX_W": 2,
        "REMOVE": 6,
        "TIME": 180,
        "BG": "#E0FFE0",
        "TITLE_FONT": ("Comic Sans MS", 20, "bold")
    },
    "MEDIUM": {
        "N": 9,
        "BOX_H": 3, "BOX_W": 3,
        "REMOVE": 40,
        "TIME": 720,
        "BG": "#FFFACD",
        "TITLE_FONT": ("Helvetica", 20, "bold")
    },
    "HARD": {
        "N": 16,
        "BOX_H": 4, "BOX_W": 4,
        "REMOVE": 150,
        "TIME": 1800,
        "BG": "#FFE0E0",
        "TITLE_FONT": ("Times New Roman", 20, "bold")
    }
}

def val_to_char(v):
    if v is None or v == 0: return ""
    if 1 <= v <= 9: return str(v)
    return chr(ord('A') + v - 10)

def char_to_val(c):
    if not c: return 0
    if c.isdigit(): return int(c)
    return ord(c.upper()) - ord('A') + 10

class SudokuLogic:
    def __init__(self, n, box_h, box_w):
        self.n = n
        self.box_h = box_h
        self.box_w = box_w
        self.board = [[0]*n for _ in range(n)]

    def is_valid(self, board, r, c, num):
        for j in range(self.n):
            if board[r][j] == num: return False
        for i in range(self.n):
            if board[i][c] == num: return False
        sr = (r // self.box_h) * self.box_h
        sc = (c // self.box_w) * self.box_w
        for i in range(self.box_h):
            for j in range(self.box_w):
                if board[sr+i][sc+j] == num:
                    return False
        return True

    def fill_board(self, board):
        empty = None
        for r in range(self.n):
            for c in range(self.n):
                if board[r][c] == 0:
                    empty = (r, c)
                    break
            if empty: break
        if not empty: return True
        r, c = empty
        nums = list(range(1, self.n+1))
        random.shuffle(nums)
        for num in nums:
            if self.is_valid(board, r, c, num):
                board[r][c] = num
                if self.fill_board(board): return True
                board[r][c] = 0
        return False

    def generate_game(self, remove_count):
        self.board = [[0]*self.n for _ in range(self.n)]
        step = self.box_h
        for i in range(0, self.n, step):
            nums = list(range(1, self.n+1))
            random.shuffle(nums)
            idx = 0
            for r in range(i, i+self.box_h):
                for c in range(i, i+self.box_w):
                    if r < self.n and c < self.n:
                        self.board[r][c] = nums[idx]
                        idx += 1
        self.fill_board(self.board)
        solution = [row[:] for row in self.board]
        initial = [row[:] for row in self.board]
        attempts = remove_count
        while attempts > 0:
            r = random.randint(0, self.n-1)
            c = random.randint(0, self.n-1)
            if initial[r][c] != 0:
                initial[r][c] = 0
                attempts -= 1
        return initial, solution

class GameWindow(tk.Toplevel):
    def __init__(self, parent, difficulty, on_close_callback):
        super().__init__(parent)
        self.parent = parent
        self.on_close_callback = on_close_callback
        self.cfg = CONFIG[difficulty]
        self.n = self.cfg["N"]
        self.bg_color = self.cfg["BG"]
        self.title(f"Sudoku - {difficulty}")
        self.configure(bg=self.bg_color)
        self.geometry("950x750")
        self.logic = SudokuLogic(self.n, self.cfg["BOX_H"], self.cfg["BOX_W"])
        self.initial_board, self.solution = self.logic.generate_game(self.cfg["REMOVE"])
        self.time_left = self.cfg["TIME"]
        self.timer_running = True
        self.hints_left = 3
        self.entries = {}

        header_frame = tk.Frame(self, bg=self.bg_color)
        header_frame.pack(side="top", fill="x", pady=10)
        tk.Label(header_frame, text=f"Level: {difficulty}", font=self.cfg["TITLE_FONT"], bg=self.bg_color).pack()

        content_frame = tk.Frame(self, bg=self.bg_color)
        content_frame.pack(side="top", expand=True, fill="both", padx=20)

        self.board_frame = tk.Frame(content_frame, bg="#333333", bd=0)
        self.board_frame.pack(side="left", padx=20, pady=20)

        controls_frame = tk.Frame(content_frame, bg=self.bg_color)
        controls_frame.pack(side="right", fill="y", padx=20, pady=20)

        self.create_board_grid()
        self.create_controls(controls_frame)

        submit_btn = tk.Button(self, text="SUBMIT BOARD", bg="#4CAF50", fg="white",
                               font=("Arial", 14, "bold"), command=self.submit_board,
                               width=22, height=2)
        submit_btn.pack(side="bottom", pady=20)

        self.update_timer()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_board_grid(self):
        vcmd = (self.register(self.validate_input), '%P')
        if self.n == 16:
            cell_width = 4
            font_size = 18
        else:
            cell_width = 5
            font_size = 24

        for r in range(self.n):
            for c in range(self.n):
                left = right = top = bottom = 1
                if (c+1) % self.cfg["BOX_W"] == 0 and c != self.n-1: right = 3
                if (r+1) % self.cfg["BOX_H"] == 0 and r != self.n-1: bottom = 3
                cell_frame = tk.Frame(self.board_frame, highlightthickness=0, bd=0)
                cell_frame.grid(row=r, column=c, padx=(left,right), pady=(top,bottom), sticky="nsew")

                val = self.initial_board[r][c]
                e = tk.Entry(cell_frame, width=cell_width, justify="center",
                             font=("Arial", font_size, "bold"),
                             validate="key", validatecommand=vcmd,
                             relief="ridge", bd=1)
                e.pack(fill="both", expand=True)

                if val != 0:
                    e.insert(0, val_to_char(val))
                    e.config(state="disabled", disabledbackground="#e8e8e8", disabledforeground="black")
                else:
                    e.config(bg="#ffffff")

                self.entries[(r,c)] = e

        for i in range(self.n):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

    def create_controls(self, parent):
        self.timer_label = tk.Label(parent, text="00:00", font=("Courier", 28, "bold"),
                                    bg="black", fg="red", width=8)
        self.timer_label.pack(pady=20)

        btn_style = {"font": ("Arial", 14), "width": 18, "pady": 8}

        self.hint_status_lbl = tk.Label(parent, text=f"Hints Left: {self.hints_left}",
                                        bg=self.bg_color, font=("Arial", 12))
        self.hint_status_lbl.pack(pady=(10,0))

        tk.Button(parent, text="Get Hint", bg="orange",
                  command=self.use_hint, **btn_style).pack(pady=5)

        tk.Button(parent, text="Verify Cell", bg="#2196F3", fg="white",
                  command=self.verify_board_visual, **btn_style).pack(pady=20)

        tk.Button(parent, text="Show Solution", bg="#f44336", fg="white",
                  command=self.show_solution, **btn_style).pack(pady=5)

        tk.Button(parent, text="New Game", bg="#9C27B0", fg="white",
                  command=self.restart_game, **btn_style).pack(pady=20)

    def validate_input(self, P):
        if P == "": return True
        if len(P) > 1: return False
        P = P.upper()
        if self.n == 4: return P in "1234"
        if self.n == 9: return P in "123456789"
        if self.n == 16: return P in "123456789ABCDEFG"
        return False

    def update_timer(self):
        if self.timer_running and self.time_left > 0:
            m, s = divmod(self.time_left, 60)
            self.timer_label.config(text=f"{m:02d}:{s:02d}")
            self.time_left -= 1
            self.after(1000, self.update_timer)
        elif self.time_left == 0 and self.timer_running:
            self.timer_running = False
            self.timer_label.config(text="00:00")
            messagebox.showinfo("Time's Up", "You ran out of time!")
            self.disable_board()

    def use_hint(self):
        if not self.timer_running: return
        if self.hints_left <= 0:
            messagebox.showwarning("No Hints", "You have used all your hints!")
            return

        candidates = []
        for r in range(self.n):
            for c in range(self.n):
                if self.initial_board[r][c] == 0:
                    entry = self.entries[(r,c)]
                    val = entry.get().upper()
                    correct = val_to_char(self.solution[r][c])
                    if val != correct:
                        candidates.append((r,c))

        if not candidates:
            messagebox.showinfo("Great!", "The board is already filled correctly!")
            return

        r, c = random.choice(candidates)
        entry = self.entries[(r,c)]
        entry.delete(0, tk.END)
        entry.insert(0, val_to_char(self.solution[r][c]))
        entry.config(fg="blue", font=("Arial", 18, "bold"))

        self.hints_left -= 1
        self.hint_status_lbl.config(text=f"Hints Left: {self.hints_left}")

    def verify_board_visual(self):
        if not self.timer_running: return
        for r in range(self.n):
            for c in range(self.n):
                if self.initial_board[r][c] == 0:
                    entry = self.entries[(r,c)]
                    val = entry.get().upper()
                    if val:
                        correct = val_to_char(self.solution[r][c])
                        if val == correct:
                            entry.config(bg="#C8E6C9")
                        else:
                            entry.config(bg="#FFCDD2")
                    else:
                        entry.config(bg="#ffffff")

    def submit_board(self):
        if not self.timer_running: return
        is_full = True
        is_correct = True
        for r in range(self.n):
            for c in range(self.n):
                val = self.entries[(r,c)].get().upper()
                correct = val_to_char(self.solution[r][c])
                if val == "": is_full = False
                if val != correct: is_correct = False
        if not is_full:
            messagebox.showwarning("Incomplete", "Fill all cells before submitting.")
        elif is_correct:
            self.timer_running = False
            messagebox.showinfo("Victory!", "You solved the puzzle!")
            self.disable_board()
        else:
            messagebox.showerror("Incorrect", "Some cells are incorrect.")

    def show_solution(self):
        if not self.timer_running: return
        if not messagebox.askyesno("Confirm", "Show solution? This will end the game."):
            return
        self.timer_running = False
        for r in range(self.n):
            for c in range(self.n):
                e = self.entries[(r,c)]
                e.config(state="normal")
                e.delete(0, tk.END)
                e.insert(0, val_to_char(self.solution[r][c]))
                e.config(state="disabled", disabledbackground="#FFF9C4", disabledforeground="purple")

    def disable_board(self):
        for e in self.entries.values():
            e.config(state="disabled")

    def restart_game(self):
        if messagebox.askyesno("New Game", "Return to Main Menu?"):
            self.on_close()

    def on_close(self):
        self.timer_running = False
        self.destroy()
        try:
            self.on_close_callback()
        except:
            pass

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Master")
        self.root.geometry("500x500")
        self.root.configure(bg="#f0f0f0")

        tk.Label(root, text="SUDOKU", font=("Helvetica", 40, "bold"),
                 bg="#f0f0f0", fg="#333").pack(pady=50)

        tk.Label(root, text="Select Difficulty:", font=("Arial", 16),
                 bg="#f0f0f0").pack(pady=15)

        btn = {"width": 25, "height": 2, "font": ("Arial", 14, "bold"), "bd": 0, "fg": "white"}

        tk.Button(root, text="EASY (4x4)", bg="#66BB6A",
                  command=lambda: self.start_game("EASY"), **btn).pack(pady=10)
        tk.Button(root, text="MEDIUM (9x9)", bg="#FFCA28",
                  command=lambda: self.start_game("MEDIUM"), **btn).pack(pady=10)
        tk.Button(root, text="HARD (16x16)", bg="#EF5350",
                  command=lambda: self.start_game("HARD"), **btn).pack(pady=10)

    def start_game(self, difficulty):
        self.root.withdraw()
        GameWindow(self.root, difficulty, self.show_menu)

    def show_menu(self):
        self.root.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    SudokuApp(root)
    root.mainloop()
