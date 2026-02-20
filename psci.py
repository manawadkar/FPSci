import tkinter as tk
from tkinter import simpledialog
import random
import time


class TennisCognitiveApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Tennis Cognitive Training")
        self.master.resizable(False, False)

        self.level = 1

        self.best_scores = {
            "Attention": {},
            "Coordination": {},
            "Decision": {},
            "Reaction": {},
            "Memory": {}
        }

        self.game_records = []
        self.current_player = None
        self.current_game = None
        self.attention_target_color = "yellow"

        control_frame = tk.Frame(master)
        control_frame.pack(fill="x", pady=6)

        tk.Button(control_frame, text="1. Attention Task", command=self.start_attention).pack(side="left", padx=4)
        tk.Button(control_frame, text="2. Eye-Hand Coordination Task", command=self.start_coordination).pack(side="left", padx=4)
        tk.Button(control_frame, text="3. Decision-Making Task", command=self.start_decision).pack(side="left", padx=4)
        tk.Button(control_frame, text="4. Reaction Time Task", command=self.start_reaction).pack(side="left", padx=4)
        tk.Button(control_frame, text="5. Working Memory Task", command=self.start_memory).pack(side="left", padx=4)
        tk.Button(control_frame, text="Main Menu", command=self.start_menu).pack(side="right", padx=6)

        self.canvas = tk.Canvas(master, width=800, height=600, bg="darkgreen")
        self.canvas.pack()

        self._after_jobs = []
        self._bindings = []

        self.start_menu()

    # --------------------------
    # Utilities
    # --------------------------
    def clear_canvas(self):
        for job in self._after_jobs:
            try:
                self.master.after_cancel(job)
            except:
                pass
        self._after_jobs.clear()

        for seq, func in self._bindings:
            try:
                self.master.unbind(seq, funcid=func)
            except:
                pass
        self._bindings.clear()

        self.canvas.delete("all")

    def update_score(self, task, score, better="higher"):
        best = self.best_scores[task].get(self.level)
        if best is None:
            self.best_scores[task][self.level] = score
        else:
            if (better == "higher" and score > best) or (better == "lower" and score < best):
                self.best_scores[task][self.level] = score

    def ask_player_name(self, game_name):
        name = simpledialog.askstring("Player Name", f"Enter Player Name for {game_name}:")
        if not name:
            return False
        self.current_player = name
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

    # --------------------------
    # Main Menu
    # --------------------------
    def start_menu(self):
        self.clear_canvas()

        self.canvas.create_text(400, 60, text="Tennis Cognitive Training",
                                fill="white", font=("Helvetica", 28, "bold"))

        y = 150
        headers = ["Game", "Player", "Score", "Level"]
        x_positions = [150, 350, 550, 700]

        for i, header in enumerate(headers):
            self.canvas.create_text(x_positions[i], y, text=header,
                                    fill="yellow", font=("Helvetica", 14, "bold"))
        y += 30

        for record in self.game_records[-10:]:
            self.canvas.create_text(150, y, text=record["game"], fill="white")
            self.canvas.create_text(350, y, text=record["player"], fill="white")
            self.canvas.create_text(550, y, text=record["score"], fill="white")
            self.canvas.create_text(700, y, text=record["level"], fill="white")
            y += 25

    # --------------------------
    # Decision Game
    # --------------------------
    def start_decision(self):
        if not self.ask_player_name("Decision"):
            return

        self.clear_canvas()
        self.score = 0
        self.decision_running = True

        self.canvas.create_text(400, 100, text="Press LEFT or RIGHT arrow based on instruction",
                                fill="white", font=("Helvetica", 16))

        self.score_text = self.canvas.create_text(700, 50, text="Score: 0", fill="white")

        def new_round():
            if not self.decision_running:
                return

            self.correct = random.choice(["Left", "Right"])
            self.canvas.delete("instruction")
            self.canvas.create_text(400, 300, text=f"Press {self.correct}",
                                    fill="yellow", font=("Helvetica", 28),
                                    tags="instruction")

        def check(event):
            if not self.decision_running:
                return

            if event.keysym == self.correct:
                self.score += 1
                self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")

            new_round()

        bind_id = self.master.bind("<KeyPress>", check)
        self._bindings.append(("<KeyPress>", bind_id))

        new_round()

    # --------------------------
    # Reaction Game
    # --------------------------
    def start_reaction(self):
        if not self.ask_player_name("Reaction"):
            return

        self.clear_canvas()
        self.reaction_start_time = None

        self.canvas.create_text(400, 200, text="Wait for GREEN signal...",
                                fill="white", font=("Helvetica", 18))

        def show_signal():
            self.canvas.delete("all")
            self.canvas.configure(bg="green")
            self.canvas.create_text(400, 300, text="CLICK NOW!",
                                    fill="black", font=("Helvetica", 28))
            self.reaction_start_time = time.time()

            def clicked(event):
                reaction_time = round(time.time() - self.reaction_start_time, 3)
                self.update_score("Reaction", reaction_time, better="lower")
                self.save_game_record(reaction_time)
                self.canvas.delete("all")
                self.canvas.configure(bg="darkgreen")
                self.canvas.create_text(400, 300,
                                        text=f"Reaction Time: {reaction_time}s",
                                        fill="white", font=("Helvetica", 28))

            self.canvas.bind("<Button-1>", clicked)

        delay = random.randint(2000, 4000)
        job = self.master.after(delay, show_signal)
        self._after_jobs.append(job)

    # --------------------------
    # Memory Game
    # --------------------------
    def start_memory(self):
        if not self.ask_player_name("Memory"):
            return

        self.clear_canvas()

        self.sequence = [random.randint(1, 9) for _ in range(self.level + 2)]

        self.canvas.create_text(400, 200,
                                text="Memorize the sequence:",
                                fill="white", font=("Helvetica", 18))

        self.canvas.create_text(400, 300,
                                text=" ".join(map(str, self.sequence)),
                                fill="yellow", font=("Helvetica", 28),
                                tags="sequence")

        def hide_sequence():
            self.canvas.delete("sequence")
            answer = simpledialog.askstring("Memory",
                                            "Enter the sequence separated by spaces:")

            if answer:
                user_seq = list(map(int, answer.split()))
                if user_seq == self.sequence:
                    score = len(self.sequence)
                    self.update_score("Memory", score)
                    self.save_game_record(score)
                    self.canvas.create_text(400, 400,
                                            text="Correct!",
                                            fill="green", font=("Helvetica", 24))
                else:
                    self.canvas.create_text(400, 400,
                                            text="Wrong!",
                                            fill="red", font=("Helvetica", 24))

        job = self.master.after(3000, hide_sequence)
        self._after_jobs.append(job)


if __name__ == "__main__":
    root = tk.Tk()
    app = TennisCognitiveApp(root)
    root.mainloop()