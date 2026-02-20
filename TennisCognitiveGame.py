import random
import time
import tkinter as tk
from tkinter import messagebox, simpledialog


class TennisCognitiveApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Tennis Cognitive Training")
        self.master.resizable(False, False)

        self.level = 1
        self.score = 0
        self.total_score = 0
        self.current_player = None
        self.current_game = None
        self.game_running = False

        self.base_speed = {
            "Attention": 1200,
            "Coordination": 20,
            "Decision": 1400,
            "Reaction": 1500,
            "Memory": 2600
        }

        self.best_scores = {
            "Attention": {},
            "Coordination": {},
            "Decision": {},
            "Reaction": {},
            "Memory": {}
        }
        self.game_records = []

        self._after_jobs = []
        self._bindings = []

        container = tk.Frame(master, bg="#1f2f1f")
        container.pack(fill="both", expand=True)

        sidebar = tk.Frame(container, width=250, bg="#193d28")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Games",
            fg="white",
            bg="#193d28",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(15, 12))

        btn_style = {
            "width": 27,
            "anchor": "w",
            "padx": 8,
            "pady": 4,
            "bg": "#e9efe9"
        }
        tk.Button(sidebar, text="1. Attention Task", command=self.start_attention, **btn_style).pack(pady=3)
        tk.Button(sidebar, text="2. Eye-Hand Coordination", command=self.start_coordination, **btn_style).pack(pady=3)
        tk.Button(sidebar, text="3. Decision-Making Task", command=self.start_decision, **btn_style).pack(pady=3)
        tk.Button(sidebar, text="4. Reaction Time Task", command=self.start_reaction, **btn_style).pack(pady=3)
        tk.Button(sidebar, text="5. Working Memory Task", command=self.start_memory, **btn_style).pack(pady=3)

        tk.Frame(sidebar, height=20, bg="#193d28").pack()
        tk.Button(
            sidebar,
            text="Main Menu",
            command=self.start_menu,
            width=27,
            anchor="w",
            padx=8,
            pady=4,
            bg="#ffe8c7"
        ).pack(pady=3)

        self.canvas = tk.Canvas(container, width=830, height=600, bg="darkgreen", highlightthickness=0)
        self.canvas.pack(side="left")

        self.title_id = None
        self.player_id = None
        self.level_id = None
        self.score_id = None
        self.help_id = None
        self.exit_btn = None
        self.exit_btn_window = None

        self.start_menu()

    # --------------------------
    # Utilities
    # --------------------------
    def _schedule(self, delay, callback):
        job = self.master.after(delay, callback)
        self._after_jobs.append(job)
        return job

    def _bind(self, widget, sequence, callback):
        funcid = widget.bind(sequence, callback)
        self._bindings.append((widget, sequence, funcid))
        return funcid

    def clear_canvas(self):
        for job in self._after_jobs:
            try:
                self.master.after_cancel(job)
            except Exception:
                pass
        self._after_jobs.clear()

        for widget, seq, funcid in self._bindings:
            try:
                widget.unbind(seq, funcid=funcid)
            except Exception:
                pass
        self._bindings.clear()

        if self.exit_btn is not None:
            try:
                self.exit_btn.destroy()
            except Exception:
                pass
            self.exit_btn = None
            self.exit_btn_window = None

        self.canvas.delete("all")
        self.canvas.configure(bg="darkgreen")

    def update_score(self, task, score, better="higher"):
        best = self.best_scores[task].get(self.level)
        if best is None:
            self.best_scores[task][self.level] = score
        elif (better == "higher" and score > best) or (better == "lower" and score < best):
            self.best_scores[task][self.level] = score

    def ask_player_name(self, game_name):
        name = simpledialog.askstring("Player Name", f"Enter Player Name for {game_name}:")
        if not name or not name.strip():
            return False
        self.current_player = name.strip()
        self.current_game = game_name
        return True

    def save_game_record(self, score):
        if self.current_player and self.current_game:
            self.game_records.append({
                "game": self.current_game,
                "player": self.current_player,
                "score": score,
                "level": self.level
            })

    def game_speed(self, game_name):
        base = self.base_speed[game_name]
        speed_boost = max(0, self.score - 25) * 0.015
        level_boost = (self.level - 1) * 0.18
        scale = max(0.35, 1.0 - speed_boost - level_boost)
        return max(8, int(base * scale))

    def setup_game_screen(self, title, help_text):
        self.clear_canvas()
        self.canvas.configure(bg="darkgreen")
        self.title_id = self.canvas.create_text(415, 30, text=title, fill="white", font=("Helvetica", 20, "bold"))
        self.player_id = self.canvas.create_text(20, 25, text="", fill="white", anchor="w", font=("Helvetica", 12, "bold"))
        self.level_id = self.canvas.create_text(20, 50, text="", fill="white", anchor="w", font=("Helvetica", 12))
        self.score_id = self.canvas.create_text(780, 25, text="", fill="white", anchor="e", font=("Helvetica", 12, "bold"))
        self.help_id = self.canvas.create_text(415, 76, text=help_text, fill="yellow", font=("Helvetica", 13))
        self.exit_btn = tk.Button(self.canvas, text="Exit Game", command=self.exit_current_game, bg="#ffd7d7")
        self.exit_btn_window = self.canvas.create_window(790, 52, window=self.exit_btn, anchor="e")
        self.refresh_hud()

    def refresh_hud(self):
        if self.player_id:
            self.canvas.itemconfigure(self.player_id, text=f"Player: {self.current_player}")
        if self.level_id:
            self.canvas.itemconfigure(self.level_id, text=f"Level: {self.level}/3")
        if self.score_id:
            self.canvas.itemconfigure(self.score_id, text=f"Score: {self.score}")

    def begin_game(self, game_name, title, help_text):
        if not self.ask_player_name(game_name):
            return False
        self.level = 1
        self.score = 0
        self.total_score = 0
        self.game_running = True
        self.setup_game_screen(title, help_text)
        return True

    def exit_current_game(self):
        if self.game_running:
            self.end_game_session("Game exited.")
        else:
            self.start_menu()

    def add_point(self, points=1):
        self.score += points
        self.total_score += points
        self.refresh_hud()

        if self.score < 80:
            return "continue"

        if self.level < 3:
            next_level = messagebox.askyesno(
                "Next Level",
                f"{self.current_player}, you reached 80 points in Level {self.level}.\nMove to Level {self.level + 1}?"
            )
            if next_level:
                self.level += 1
                self.score = 0
                self.refresh_hud()
                return "next_level"
            self.end_game_session("Game stopped before next level.")
            return "ended"

        messagebox.showinfo("Completed", f"{self.current_player}, you completed all 3 levels in {self.current_game}.")
        self.end_game_session("Game completed.")
        return "ended"

    def end_game_session(self, message=None):
        if not self.game_running:
            return
        self.game_running = False
        self.update_score(self.current_game, self.total_score, better="higher")
        self.save_game_record(self.total_score)
        if message:
            messagebox.showinfo("Game", message)
        self.start_menu()

    # --------------------------
    # Main Menu
    # --------------------------
    def start_menu(self):
        if self.game_running:
            self.game_running = False
            self.update_score(self.current_game, self.total_score, better="higher")
            self.save_game_record(self.total_score)

        self.clear_canvas()
        self.canvas.configure(bg="#123d2d")

        self.canvas.create_text(
            415,
            48,
            text="Tennis Cognitive Training",
            fill="white",
            font=("Helvetica", 28, "bold")
        )

        top_y = 120
        row_h = 34
        headers = ["Game Name", "Player Name", "Score", "Level"]
        x_cols = [70, 320, 580, 710, 800]

        self.canvas.create_rectangle(x_cols[0], top_y, x_cols[-1], top_y + row_h, fill="#0f2f22", outline="white")
        for idx, h in enumerate(headers):
            cx = (x_cols[idx] + x_cols[idx + 1]) // 2
            self.canvas.create_text(cx, top_y + row_h // 2, text=h, fill="yellow", font=("Helvetica", 12, "bold"))

        rows = self.game_records[-12:]
        for i, rec in enumerate(rows, start=1):
            y1 = top_y + i * row_h
            y2 = y1 + row_h
            self.canvas.create_rectangle(x_cols[0], y1, x_cols[-1], y2, fill="#1d5c45", outline="white")
            vals = [rec["game"], rec["player"], str(rec["score"]), str(rec["level"])]
            for c, val in enumerate(vals):
                cx = (x_cols[c] + x_cols[c + 1]) // 2
                self.canvas.create_text(cx, y1 + row_h // 2, text=val, fill="white", font=("Helvetica", 11))

        self.canvas.create_text(
            415,
            560,
            text="Use the sidebar buttons to start any game.",
            fill="white",
            font=("Helvetica", 12)
        )

    # --------------------------
    # 1) Attention Game
    # --------------------------
    def start_attention(self):
        if not self.begin_game("Attention", "Attention Task", "Click only the YELLOW target."):
            return

        self.attention_job = None

        def draw_targets():
            if not self.game_running or self.current_game != "Attention":
                return
            self.canvas.delete("play")
            count = 6 + (self.level - 1) * 2
            target_index = random.randint(0, count - 1)
            colors = ["red", "blue", "white", "orange", "pink", "cyan"]

            for i in range(count):
                r = 18
                x = random.randint(130, 780)
                y = random.randint(130, 560)
                color = "yellow" if i == target_index else random.choice(colors)
                tags = ("play", "target") if color == "yellow" else ("play",)
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="black", width=1, tags=tags)

            delay = self.game_speed("Attention")
            self.attention_job = self._schedule(delay, draw_targets)

        def on_click(event):
            if not self.game_running or self.current_game != "Attention":
                return
            item = self.canvas.find_closest(event.x, event.y)
            if not item:
                return
            if "target" in self.canvas.gettags(item[0]):
                if self.attention_job:
                    try:
                        self.master.after_cancel(self.attention_job)
                    except Exception:
                        pass
                state = self.add_point(1)
                if state != "ended":
                    draw_targets()

        self._bind(self.canvas, "<Button-1>", on_click)
        draw_targets()

    # --------------------------
    # 2) Coordination Game
    # --------------------------
    def start_coordination(self):
        if not self.begin_game(
            "Coordination",
            "Eye-Hand Coordination Task",
            "Move mouse to control paddle and catch only the instructed color."
        ):
            return

        play_left, play_top, play_right, play_bottom = 120, 120, 790, 560
        self.canvas.create_rectangle(play_left, play_top, play_right, play_bottom, outline="white", width=2, tags="play")
        palette = [
            ("BLUE", "deepskyblue"),
            ("RED", "tomato"),
            ("GREEN", "limegreen"),
            ("YELLOW", "gold"),
            ("ORANGE", "orange"),
            ("PINK", "hotpink")
        ]

        state = {
            "paddle_x": 455.0,
            "mouse_x": 455.0,
            "paddle_w": 170.0,
            "paddle_h": 16.0,
            "misses": 0,
            "target_name": "BLUE",
            "target_fill": "deepskyblue",
            "balls": []
        }

        paddle_y = play_bottom - 20
        paddle_id = self.canvas.create_rectangle(0, 0, 0, 0, fill="#f4e74f", outline="black", width=1, tags="play")
        status_id = self.canvas.create_text(415, 95, text="", fill="yellow", font=("Helvetica", 12))
        target_id = self.canvas.create_text(770, 52, text="", fill="white", anchor="e", font=("Helvetica", 12, "bold"))
        miss_id = self.canvas.create_text(770, 76, text="Misses: 0/3", fill="white", anchor="e", font=("Helvetica", 11))

        def clamp(val, lo, hi):
            return max(lo, min(hi, val))

        def choose_target():
            state["target_name"], state["target_fill"] = random.choice(palette)
            self.canvas.itemconfigure(target_id, text=f"Collect: {state['target_name']}")

        def desired_ball_count():
            return min(8, 4 + (self.level - 1) + (1 if self.score > 25 else 0))

        def spawn_ball(ball=None):
            if ball is None:
                ball = {}

            color_name, color_fill = random.choice(palette)
            ball["name"] = color_name
            ball["fill"] = color_fill
            ball["r"] = random.randint(12, 18)
            ball["x"] = random.randint(play_left + 24, play_right - 24)
            ball["y"] = random.randint(play_top + 25, play_top + 110)
            dx_mag = random.uniform(1.6, 3.2) + (self.level - 1) * 0.25 + min(1.6, max(0, self.score - 25) * 0.03)
            ball["dx"] = random.choice([-1, 1]) * dx_mag
            ball["dy"] = random.uniform(2.4, 3.8) + (self.level - 1) * 0.45 + min(3.4, max(0, self.score - 25) * 0.06)

            if "id" not in ball:
                ball["id"] = self.canvas.create_oval(0, 0, 0, 0, fill=ball["fill"], outline="white", width=2, tags="play")
            self.canvas.itemconfigure(ball["id"], fill=ball["fill"])
            self.canvas.coords(
                ball["id"],
                ball["x"] - ball["r"], ball["y"] - ball["r"],
                ball["x"] + ball["r"], ball["y"] + ball["r"]
            )
            return ball

        def rebuild_balls():
            need = desired_ball_count()
            while len(state["balls"]) < need:
                state["balls"].append(spawn_ball())
            while len(state["balls"]) > need:
                extra = state["balls"].pop()
                self.canvas.delete(extra["id"])
            for ball in state["balls"]:
                spawn_ball(ball)

        def register_miss(reason_text):
            state["misses"] += 1
            self.canvas.itemconfigure(status_id, text=reason_text)
            self.canvas.itemconfigure(miss_id, text=f"Misses: {state['misses']}/3")
            if state["misses"] >= 3:
                self.score = max(0, self.score - 1)
                self.total_score = max(0, self.total_score - 1)
                self.refresh_hud()
                self.end_game_session("Missed 3 times. -1 score. Game over.")
                return True
            return False

        def update_paddle():
            target_width = max(84, 170 - ((self.level - 1) * 26) - (max(0, self.score - 25) // 2))
            state["paddle_w"] = float(target_width)

            # Smooth paddle motion to make it a coordination challenge, not instant snapping.
            state["paddle_x"] += (state["mouse_x"] - state["paddle_x"]) * 0.32
            half_w = state["paddle_w"] / 2
            state["paddle_x"] = clamp(state["paddle_x"], play_left + half_w, play_right - half_w)

            self.canvas.coords(
                paddle_id,
                state["paddle_x"] - half_w, paddle_y - state["paddle_h"] / 2,
                state["paddle_x"] + half_w, paddle_y + state["paddle_h"] / 2
            )

        def update_ball(ball):
            tick = max(8, self.game_speed("Coordination"))
            frame_scale = 28.0 / tick
            ball["x"] += ball["dx"] * frame_scale
            ball["y"] += ball["dy"] * frame_scale

            if ball["x"] - ball["r"] <= play_left:
                ball["x"] = play_left + ball["r"]
                ball["dx"] = abs(ball["dx"])
            if ball["x"] + ball["r"] >= play_right:
                ball["x"] = play_right - ball["r"]
                ball["dx"] = -abs(ball["dx"])
            if ball["y"] - ball["r"] <= play_top:
                ball["y"] = play_top + ball["r"]
                ball["dy"] = abs(ball["dy"])

            self.canvas.coords(
                ball["id"],
                ball["x"] - ball["r"], ball["y"] - ball["r"],
                ball["x"] + ball["r"], ball["y"] + ball["r"]
            )

        def animate():
            if not self.game_running or self.current_game != "Coordination":
                return

            update_paddle()
            x1, y1, x2, y2 = self.canvas.coords(paddle_id)

            for ball in state["balls"]:
                update_ball(ball)

                ball_bottom = ball["y"] + ball["r"]
                ball_top = ball["y"] - ball["r"]
                ball_on_paddle_x = x1 <= ball["x"] <= x2
                ball_hit_paddle = ball_bottom >= y1 and ball_top <= y2 and ball["dy"] > 0 and ball_on_paddle_x

                if ball_hit_paddle:
                    if ball["name"] == state["target_name"]:
                        self.canvas.itemconfigure(status_id, text=f"Correct catch: {ball['name']}")
                        progression = self.add_point(1)
                        if progression == "ended":
                            return
                        if progression == "next_level":
                            choose_target()
                            rebuild_balls()
                        elif self.score > 0 and self.score % 12 == 0:
                            choose_target()
                        spawn_ball(ball)
                    else:
                        if register_miss(f"Wrong catch: {ball['name']}"):
                            return
                        spawn_ball(ball)
                elif ball["y"] - ball["r"] > play_bottom:
                    if ball["name"] == state["target_name"]:
                        if register_miss("Missed instructed ball"):
                            return
                    spawn_ball(ball)

            self._schedule(max(8, self.game_speed("Coordination")), animate)

        def on_mouse_move(event):
            if not self.game_running or self.current_game != "Coordination":
                return
            state["mouse_x"] = clamp(event.x, play_left + 42, play_right - 42)

        self._bind(self.canvas, "<Motion>", on_mouse_move)
        choose_target()
        rebuild_balls()
        animate()

    # --------------------------
    # 3) Decision Game
    # --------------------------
    def start_decision(self):
        if not self.begin_game("Decision", "Decision-Making Task", "Press the correct arrow key quickly."):
            return

        self.correct_key = None
        self.prompt_id = self.canvas.create_text(415, 310, text="", fill="white", font=("Helvetica", 34, "bold"))
        self.status_id = self.canvas.create_text(415, 370, text="", fill="yellow", font=("Helvetica", 14))
        self.round_job = None
        wrong_attempts = {"value": 0}
        wrong_id = self.canvas.create_text(770, 76, text="Wrong Attempts: 0/3", fill="white", anchor="e", font=("Helvetica", 11))

        def new_round():
            if not self.game_running or self.current_game != "Decision":
                return
            self.correct_key = random.choice(["Left", "Right", "Up", "Down"])
            self.canvas.itemconfigure(self.prompt_id, text=f"Press {self.correct_key.upper()}")
            self.canvas.itemconfigure(self.status_id, text="")
            if self.round_job:
                try:
                    self.master.after_cancel(self.round_job)
                except Exception:
                    pass
            self.round_job = self._schedule(self.game_speed("Decision"), new_round)

        def finish_decision_game():
            if not self.game_running or self.current_game != "Decision":
                return
            self.game_running = False
            self.update_score("Decision", self.total_score, better="higher")
            self.save_game_record(self.total_score)
            self.clear_canvas()

            play_again = messagebox.askyesno(
                "Decision Game Over",
                "3 wrong attempts reached. Do you want to play again?"
            )
            if play_again:
                self.start_decision()
            else:
                self.start_menu()

        def on_key(event):
            if not self.game_running or self.current_game != "Decision":
                return
            if event.keysym == self.correct_key:
                state = self.add_point(1)
                self.canvas.itemconfigure(self.status_id, text="Correct")
                if state != "ended":
                    new_round()
            else:
                wrong_attempts["value"] += 1
                self.canvas.itemconfigure(wrong_id, text=f"Wrong Attempts: {wrong_attempts['value']}/3")
                if wrong_attempts["value"] >= 3:
                    self.canvas.itemconfigure(self.status_id, text="Wrong key (3/3)")
                    finish_decision_game()
                else:
                    left = 3 - wrong_attempts["value"]
                    self.canvas.itemconfigure(self.status_id, text=f"Wrong key ({left} chances left)")
                    new_round()

        self._bind(self.master, "<KeyPress>", on_key)
        new_round()

    # --------------------------
    # 4) Reaction Game
    # --------------------------
    def start_reaction(self):
        if not self.begin_game("Reaction", "Reaction Time Task", "Wait for GREEN, then press SPACE immediately."):
            return

        self.waiting_green = False
        self.reaction_start_time = None
        self.signal_circle = self.canvas.create_oval(320, 180, 510, 370, fill="red", outline="white", width=3)
        self.signal_text = self.canvas.create_text(415, 430, text="WAIT...", fill="white", font=("Helvetica", 24, "bold"))
        self.status_id = self.canvas.create_text(415, 475, text="", fill="yellow", font=("Helvetica", 13))

        def points_from_reaction(reaction_time):
            if reaction_time <= 0.20:
                return 5
            if reaction_time <= 0.30:
                return 4
            if reaction_time <= 0.40:
                return 3
            if reaction_time <= 0.55:
                return 2
            return 1

        def show_green():
            if not self.game_running or self.current_game != "Reaction":
                return
            self.waiting_green = True
            self.reaction_start_time = time.perf_counter()
            self.canvas.itemconfigure(self.signal_circle, fill="lime")
            self.canvas.itemconfigure(self.signal_text, text="PRESS SPACE")

            def timeout_green():
                if self.game_running and self.current_game == "Reaction" and self.waiting_green:
                    self.waiting_green = False
                    self.canvas.itemconfigure(self.status_id, text="Missed signal")
                    prepare_round()

            self._schedule(max(220, int(self.game_speed("Reaction") * 0.45)), timeout_green)

        def prepare_round():
            if not self.game_running or self.current_game != "Reaction":
                return
            self.waiting_green = False
            self.canvas.itemconfigure(self.signal_circle, fill="red")
            self.canvas.itemconfigure(self.signal_text, text="WAIT...")
            wait_min = max(280, int(self.game_speed("Reaction") * 0.55))
            wait_max = max(wait_min + 140, int(self.game_speed("Reaction") * 1.05))
            self._schedule(random.randint(wait_min, wait_max), show_green)

        def on_space(_event):
            if not self.game_running or self.current_game != "Reaction":
                return
            if not self.waiting_green:
                self.canvas.itemconfigure(self.status_id, text="Too early")
                return
            self.waiting_green = False
            reaction_time = time.perf_counter() - self.reaction_start_time
            points = points_from_reaction(reaction_time)
            self.canvas.itemconfigure(self.status_id, text=f"Reaction: {reaction_time:.3f}s  Score +{points}")
            state = self.add_point(points)
            if state != "ended":
                prepare_round()

        self._bind(self.master, "<space>", on_space)
        prepare_round()

    # --------------------------
    # 5) Memory Game
    # --------------------------
    def start_memory(self):
        if not self.begin_game("Memory", "Working Memory Task", "Memorize and repeat the number pattern."):
            return

        self.sequence_id = self.canvas.create_text(415, 300, text="", fill="yellow", font=("Helvetica", 34, "bold"))
        self.status_id = self.canvas.create_text(415, 390, text="", fill="white", font=("Helvetica", 15))
        self.current_sequence = []
        wrong_attempts = {"value": 0}
        attempts_id = self.canvas.create_text(770, 76, text="Wrong Attempts: 0/3", fill="white", anchor="e", font=("Helvetica", 11))

        def lose_attempt(message):
            wrong_attempts["value"] += 1
            self.canvas.itemconfigure(attempts_id, text=f"Wrong Attempts: {wrong_attempts['value']}/3")
            if wrong_attempts["value"] >= 3:
                self.end_game_session("3 wrong attempts. Memory game over.")
                return "ended"
            left = 3 - wrong_attempts["value"]
            self.canvas.itemconfigure(self.status_id, text=f"{message}  ({left} wrong attempts left)")
            self._schedule(600, next_round)
            return "continue"

        def next_round():
            if not self.game_running or self.current_game != "Memory":
                return
            length = 3 + self.level + min(6, self.score // 12)
            self.current_sequence = [random.randint(1, 9) for _ in range(length)]
            self.canvas.itemconfigure(self.sequence_id, text=" ".join(map(str, self.current_sequence)))
            self.canvas.itemconfigure(self.status_id, text="Memorize...")
            display_ms = max(900, self.game_speed("Memory"))
            self._schedule(display_ms, ask_input)

        def ask_input():
            if not self.game_running or self.current_game != "Memory":
                return
            self.canvas.itemconfigure(self.sequence_id, text="...")
            self.canvas.itemconfigure(self.status_id, text="Type sequence in popup")
            answer = simpledialog.askstring("Memory", "Enter sequence separated by spaces:")
            if not self.game_running or self.current_game != "Memory":
                return
            if answer is None:
                self.canvas.itemconfigure(self.status_id, text="No input. Continue...")
                self._schedule(500, next_round)
                return
            try:
                cleaned = answer.replace(",", " ").strip()
                user_seq = [int(x) for x in cleaned.split()]
            except ValueError:
                user_seq = []

            if user_seq == self.current_sequence:
                self.canvas.itemconfigure(self.status_id, text="Correct  (+1)")
                state = self.add_point(1)
                if state != "ended":
                    next_round()
            else:
                lose_attempt("Wrong pattern")

        next_round()


if __name__ == "__main__":
    root = tk.Tk()
    app = TennisCognitiveApp(root)
    root.mainloop()
