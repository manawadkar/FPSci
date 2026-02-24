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
        self.level_2_unlock_score = 50
        self.level_3_unlock_score = 100

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

        tk.Label(
            sidebar,
            text="developed by @SunilBM",
            fg="#d7f0d7",
            bg="#193d28",
            font=("Helvetica", 10)
        ).pack(side="bottom", anchor="w", padx=8, pady=10)

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
        result = {"name": None}

        dialog = tk.Toplevel(self.master)
        dialog.title(f"{game_name} Setup")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.configure(bg="#eef5ee")

        tk.Label(
            dialog,
            text=f"{game_name} - Player Setup",
            bg="#eef5ee",
            fg="#163b27",
            font=("Helvetica", 14, "bold")
        ).grid(row=0, column=0, columnspan=2, padx=16, pady=(12, 10), sticky="w")

        tk.Label(
            dialog,
            text="Player Name:",
            bg="#eef5ee",
            fg="#163b27",
            font=("Helvetica", 11, "bold")
        ).grid(row=1, column=0, padx=(16, 8), pady=(0, 8), sticky="e")

        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, width=28, font=("Helvetica", 11))
        name_entry.grid(row=1, column=1, padx=(0, 16), pady=(0, 8), sticky="w")

        tk.Label(
            dialog,
            text="Levels",
            bg="#eef5ee",
            fg="#163b27",
            font=("Helvetica", 11, "bold")
        ).grid(row=2, column=0, columnspan=2, padx=16, pady=(2, 4), sticky="w")

        level_lines = [
            "Level 1: Unlocked",
            f"Level 2: Locked (Unlock at {self.level_2_unlock_score} score)",
            f"Level 3: Locked (Unlock at {self.level_3_unlock_score} score)"
        ]
        for idx, line in enumerate(level_lines, start=3):
            tk.Label(
                dialog,
                text=line,
                bg="#eef5ee",
                fg="#204d36",
                font=("Helvetica", 10)
            ).grid(row=idx, column=0, columnspan=2, padx=16, pady=1, sticky="w")

        btn_row = 3 + len(level_lines)
        btn_frame = tk.Frame(dialog, bg="#eef5ee")
        btn_frame.grid(row=btn_row, column=0, columnspan=2, padx=16, pady=(12, 14), sticky="e")

        def submit():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Player Name", "Please enter player name.", parent=dialog)
                name_entry.focus_set()
                return
            result["name"] = name
            dialog.destroy()

        def cancel():
            dialog.destroy()

        tk.Button(btn_frame, text="Start", width=10, command=submit, bg="#d6efd6").pack(side="left", padx=(0, 8))
        tk.Button(btn_frame, text="Cancel", width=10, command=cancel, bg="#f2d6d6").pack(side="left")

        dialog.bind("<Return>", lambda _e: submit())
        dialog.bind("<Escape>", lambda _e: cancel())

        dialog.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - dialog.winfo_width()) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(10, x)}+{max(10, y)}")

        name_entry.focus_set()
        self.master.wait_window(dialog)

        if not result["name"]:
            return False

        self.current_player = result["name"]
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
            l2_status = "Unlocked" if self.score >= self.level_2_unlock_score else f"Locked({self.level_2_unlock_score})"
            l3_status = "Unlocked" if self.score >= self.level_3_unlock_score else f"Locked({self.level_3_unlock_score})"
            self.canvas.itemconfigure(
                self.level_id,
                text=f"Level: {self.level}/3   L2: {l2_status}   L3: {l3_status}"
            )
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
        previous_level = self.level

        if self.score >= self.level_3_unlock_score:
            self.level = 3
        elif self.score >= self.level_2_unlock_score:
            self.level = 2
        else:
            self.level = 1

        self.refresh_hud()

        if self.level > previous_level:
            messagebox.showinfo("Level Unlocked", f"🔓 Level {self.level} unlocked in {self.current_game}.")
            return "next_level"
        return "continue"

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
            "Move mouse to keep one bouncing ball alive. Missing the ball ends the game."
        ):
            return

        play_left, play_top, play_right, play_bottom = 120, 120, 790, 560
        self.canvas.create_rectangle(play_left, play_top, play_right, play_bottom, outline="white", width=2, tags="play")
        ball_fill = "deepskyblue"

        state = {
            "paddle_x": 455.0,
            "mouse_x": 455.0,
            "paddle_w": 170.0,
            "paddle_h": 16.0,
            "balls": []
        }

        paddle_y = play_bottom - 20
        paddle_id = self.canvas.create_rectangle(0, 0, 0, 0, fill="#f4e74f", outline="black", width=1, tags="play")
        status_id = self.canvas.create_text(415, 95, text="", fill="yellow", font=("Helvetica", 12))
        speed_step_score = 5
        speed_step_factor = 1.06
        max_h_speed = 7.5
        max_v_speed = 10.5

        def clamp(val, lo, hi):
            return max(lo, min(hi, val))

        def speed_stage():
            return self.score // speed_step_score

        def desired_ball_count():
            return 1

        def spawn_ball(ball=None):
            if ball is None:
                ball = {}

            ball["fill"] = ball_fill
            ball["r"] = random.randint(12, 18)
            ball["x"] = random.randint(play_left + 24, play_right - 24)
            ball["y"] = random.randint(play_top + 25, play_top + 110)
            stage_factor = speed_step_factor ** speed_stage()
            dx_mag = random.uniform(1.8, 2.7) + (self.level - 1) * 0.20 + min(1.0, max(0, self.score - 25) * 0.02)
            ball["dx"] = clamp(random.choice([-1, 1]) * dx_mag * stage_factor, -max_h_speed, max_h_speed)
            ball["dy"] = clamp(
                (random.uniform(2.3, 3.1) + (self.level - 1) * 0.35 + min(2.0, max(0, self.score - 25) * 0.04)) * stage_factor,
                -max_v_speed,
                max_v_speed
            )
            ball["speed_stage"] = speed_stage()

            if "id" not in ball:
                ball["id"] = self.canvas.create_oval(0, 0, 0, 0, fill=ball["fill"], outline="white", width=2, tags="play")
            self.canvas.itemconfigure(ball["id"], fill=ball["fill"])
            self.canvas.coords(
                ball["id"],
                ball["x"] - ball["r"], ball["y"] - ball["r"],
                ball["x"] + ball["r"], ball["y"] + ball["r"]
            )
            return ball

        def apply_speed_step(ball):
            current_stage = speed_stage()
            previous_stage = ball.get("speed_stage", current_stage)
            if current_stage <= previous_stage:
                return

            factor = speed_step_factor ** (current_stage - previous_stage)
            ball["dx"] = clamp(ball["dx"] * factor, -max_h_speed, max_h_speed)
            ball["dy"] = clamp(ball["dy"] * factor, -max_v_speed, max_v_speed)
            ball["speed_stage"] = current_stage
            self.canvas.itemconfigure(status_id, text=f"Speed increased at {current_stage * speed_step_score} score")

        def rebuild_balls():
            need = desired_ball_count()
            while len(state["balls"]) < need:
                state["balls"].append(spawn_ball())
            while len(state["balls"]) > need:
                extra = state["balls"].pop()
                self.canvas.delete(extra["id"])
            for ball in state["balls"]:
                spawn_ball(ball)

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
            ball["x"] += ball["dx"]
            ball["y"] += ball["dy"]

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
                    self.canvas.itemconfigure(status_id, text="Bounce +1")
                    progression = self.add_point(1)
                    if progression == "ended":
                        return
                    ball["y"] = y1 - ball["r"] - 1
                    ball["dy"] = -abs(ball["dy"])
                    paddle_offset = (ball["x"] - state["paddle_x"]) / max(1.0, state["paddle_w"] / 2.0)
                    ball["dx"] = clamp(ball["dx"] + paddle_offset * 0.9, -max_h_speed, max_h_speed)
                    apply_speed_step(ball)
                elif ball["y"] - ball["r"] > play_bottom:
                    self.end_game_session("You missed the ball. Game over.")
                    return

            self._schedule(16, animate)

        def on_mouse_move(event):
            if not self.game_running or self.current_game != "Coordination":
                return
            state["mouse_x"] = clamp(event.x, play_left + 42, play_right - 42)

        self._bind(self.canvas, "<Motion>", on_mouse_move)
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

        def on_key(event):
            if not self.game_running or self.current_game != "Decision":
                return
            if event.keysym == self.correct_key:
                state = self.add_point(1)
                self.canvas.itemconfigure(self.status_id, text="Correct")
                if state != "ended":
                    new_round()
            else:
                self.canvas.itemconfigure(self.status_id, text="Wrong key")
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
                self.canvas.itemconfigure(self.status_id, text="Wrong pattern")
                self._schedule(600, next_round)

        next_round()


if __name__ == "__main__":
    root = tk.Tk()
    app = TennisCognitiveApp(root)
    root.mainloop()

