"""A small click-to-clear arrow puzzle, using only Python's standard library."""

import tkinter as tk

from logic import DIRECTIONS, LEVELS, SIZE, blocker


BG = "#10171f"
PANEL = "#18232e"
GRID = "#263544"
TEXT = "#f3f7f7"
MUTED = "#a7b6c2"
ACCENT = "#8ee3c8"
BAD = "#ff7b83"
CELL = 76
BOARD = SIZE * CELL
PAD = 16


class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("一箭又一箭 · Arrow Escape")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.level = 0
        self.arrows = list(LEVELS[0])
        self.misses = 3
        self.state = "start"
        self.busy = False
        self.selected = None
        self.shift = (0, 0)
        self.flash = False

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=28, pady=(24, 10))
        tk.Label(top, text="一箭又一箭", bg=BG, fg=TEXT,
                 font=("Microsoft YaHei UI", 24, "bold")).pack(anchor="w")
        tk.Label(top, text="观察方向与阻挡关系，依次让箭头飞出棋盘。",
                 bg=BG, fg=MUTED, font=("Microsoft YaHei UI", 11)).pack(anchor="w", pady=(5, 0))

        self.info = tk.Label(self.root, bg=BG, fg=ACCENT,
                             font=("Microsoft YaHei UI", 12, "bold"))
        self.info.pack(pady=8)
        self.canvas = tk.Canvas(self.root, width=BOARD + 2 * PAD, height=BOARD + 2 * PAD,
                                bg=PANEL, highlightthickness=0, cursor="hand2")
        self.canvas.pack(padx=28)
        self.canvas.bind("<Button-1>", self.click)

        controls = tk.Frame(self.root, bg=BG)
        controls.pack(fill="x", padx=28, pady=(16, 25))
        self.message = tk.Label(controls, text="", bg=BG, fg=MUTED,
                                font=("Microsoft YaHei UI", 11))
        self.message.pack(side="left")
        self.restart = tk.Button(controls, text="重新开始", command=self.reset,
                                 bg=GRID, fg=TEXT, activebackground=ACCENT,
                                 relief="flat", padx=18, pady=9,
                                 font=("Microsoft YaHei UI", 10, "bold"))
        self.restart.pack(side="right")
        self.action = tk.Button(controls, text="开始游戏", command=self.advance,
                                bg=ACCENT, fg=BG, activebackground="#c1f6e6",
                                relief="flat", padx=18, pady=9,
                                font=("Microsoft YaHei UI", 10, "bold"))
        self.action.pack(side="right", padx=(0, 10))
        self.draw()

    def reset(self):
        if self.busy:
            return
        self.arrows = list(LEVELS[self.level])
        self.misses = 3
        self.state = "playing"
        self.selected = None
        self.message.configure(text="已重新开始本关", fg=MUTED)
        self.draw()

    def advance(self):
        if self.busy:
            return
        if self.state == "start":
            self.state = "playing"
        elif self.state == "won":
            self.level += 1
            self.arrows = list(LEVELS[self.level])
            self.misses = 3
            self.state = "playing"
        elif self.state == "lost":
            self.reset()
            return
        elif self.state == "finished":
            self.level = 0
            self.arrows = list(LEVELS[0])
            self.misses = 3
            self.state = "playing"
        self.message.configure(text="点击前方没有箭头的箭头", fg=MUTED)
        self.draw()

    def click(self, event):
        if self.state != "playing" or self.busy:
            return
        col = (event.x - PAD) // CELL
        row = (event.y - PAD) // CELL
        arrow = next((a for a in self.arrows if a[:2] == (row, col)), None)
        if arrow is None:
            return
        self.selected = arrow
        self.busy = True
        if blocker(self.arrows, arrow) is None:
            self.message.configure(text="路径畅通！", fg=ACCENT)
            self.fly(0)
        else:
            self.misses -= 1
            self.message.configure(text="碰撞！前方还有箭头", fg=BAD)
            self.bump(0)

    def fly(self, step):
        dr, dc = DIRECTIONS[self.selected[2]]
        self.shift = (dc * step * 11, dr * step * 11)
        self.draw()
        row, col, _ = self.selected
        cells_to_edge = (SIZE - col if dc > 0 else col + 1 if dc < 0 else
                         SIZE - row if dr > 0 else row + 1)
        final_step = (cells_to_edge * CELL + CELL // 2) // 11 + 1
        if step < final_step:
            self.root.after(22, self.fly, step + 1)
        else:
            self.arrows.remove(self.selected)
            self.selected = None
            self.shift = (0, 0)
            self.busy = False
            if not self.arrows:
                self.state = "finished" if self.level == len(LEVELS) - 1 else "won"
            self.draw()

    def bump(self, step):
        dr, dc = DIRECTIONS[self.selected[2]]
        distance = (0, 7, 13, 7, 0, -4, 0)[step]
        self.shift = (dc * distance, dr * distance)
        self.flash = step % 2 == 1
        self.draw()
        if step < 6:
            self.root.after(65, self.bump, step + 1)
        else:
            self.selected = None
            self.shift = (0, 0)
            self.flash = False
            self.busy = False
            if self.misses == 0:
                self.state = "lost"
            self.draw()

    def draw_arrow(self, row, col, direction, color, shift=(0, 0)):
        cx = PAD + col * CELL + CELL / 2 + shift[0]
        cy = PAD + row * CELL + CELL / 2 + shift[1]
        # Shape points right; rotate to the requested direction.
        points = [(-22, -8), (2, -8), (2, -18), (25, 0),
                  (2, 18), (2, 8), (-22, 8)]
        turns = {"→": 0, "↓": 1, "←": 2, "↑": 3}[direction]
        for _ in range(turns):
            points = [(-y, x) for x, y in points]
        self.canvas.create_polygon([value for x, y in points for value in (cx + x, cy + y)],
                                   fill=color, outline="")

    def draw(self):
        self.canvas.delete("all")
        self.info.configure(text=f"第 {self.level + 1} / {len(LEVELS)} 关     ·     剩余箭头 {len(self.arrows)}     ·     剩余失误 {self.misses}")
        for row in range(SIZE):
            for col in range(SIZE):
                x = PAD + col * CELL
                y = PAD + row * CELL
                self.canvas.create_rectangle(x + 2, y + 2, x + CELL - 2, y + CELL - 2,
                                             fill=BG, outline=GRID, width=1)
        for arrow in self.arrows:
            selected = arrow == self.selected
            color = BAD if selected and self.flash else ACCENT if selected else TEXT
            self.draw_arrow(*arrow, color, self.shift if selected else (0, 0))

        labels = {"start": ("准备好了吗？", "点击开始游戏，找出每关的安全顺序", "开始游戏"),
                  "won": ("本关通关！", "所有箭头已飞出，进入下一关吧", "下一关"),
                  "lost": ("本关失败", "失误次数已耗尽，再试一次", "重试本关"),
                  "finished": ("全部通关！", "三关挑战完成，做得漂亮！", "再玩一次")}
        if self.state in labels:
            title, subtitle, button = labels[self.state]
            self.canvas.create_rectangle(25, 160, BOARD + 7, 326,
                                         fill=PANEL, outline=ACCENT if self.state != "lost" else BAD,
                                         width=2)
            self.canvas.create_text((BOARD + 2 * PAD) / 2, 215, text=title,
                                    fill=TEXT, font=("Microsoft YaHei UI", 24, "bold"))
            self.canvas.create_text((BOARD + 2 * PAD) / 2, 265, text=subtitle,
                                    fill=MUTED, font=("Microsoft YaHei UI", 11))
            self.action.configure(text=button)
            self.action.pack(side="right", padx=(0, 10))
        else:
            self.action.pack_forget()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Game().run()
