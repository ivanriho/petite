#!/usr/bin/env python3
"""Nytt GUI-spel: Catch the Sky."""

import math
import random
import tkinter as tk
from tkinter import messagebox


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def random_between(minimum, maximum):
    return random.randint(minimum, maximum)


def distance_between(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def pick_color(options):
    return random.choice(options)


def build_window(title, width, height):
    root = tk.Tk()
    root.title(title)
    root.geometry(f"{width}x{height}")
    root.resizable(False, False)
    return root


class CatchTheSky:
    def __init__(self, root):
        self.root = root
        self.width = 820
        self.height = 620
        self.score = 0
        self.level = 1
        self.lives = 3
        self.time_left = 45
        self.state = "ready"
        self.player_speed = 10
        self.keys = {"left": False, "right": False}
        self.player = None
        self.objects = []
        self.particles = []
        self.background = []
        self.after_id = None
        self.msg = ""

        self.create_layout()
        self.prepare_background()
        self.reset_game()

    def create_layout(self):
        self.title = self.make_title()
        self.hud = self.make_hud()
        self.canvas = self.make_canvas()
        self.buttons = self.make_buttons()
        self.bind_keys()

    def make_title(self):
        label = tk.Label(self.root, text="Catch the Sky", font=("Arial", 24, "bold"), fg="#122033")
        label.pack(pady=(16, 6))
        return label

    def make_hud(self):
        frame = tk.Frame(self.root, bg="#edf5ff")
        frame.pack(fill="x", padx=18, pady=4)

        self.score_label = tk.Label(frame, text="Poäng: 0", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.score_label.grid(row=0, column=0, padx=12, pady=6)

        self.level_label = tk.Label(frame, text="Nivå: 1", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.level_label.grid(row=0, column=1, padx=12, pady=6)

        self.lives_label = tk.Label(frame, text="Liv: 3", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.lives_label.grid(row=0, column=2, padx=12, pady=6)

        self.timer_label = tk.Label(frame, text="Tid: 45s", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.timer_label.grid(row=0, column=3, padx=12, pady=6)

        return frame

    def make_canvas(self):
        canvas = tk.Canvas(self.root, width=self.width, height=self.height - 180, bg="#dfeeff", highlightthickness=2, highlightbackground="#adc6e8")
        canvas.pack(padx=18, pady=(6, 8))
        return canvas

    def make_buttons(self):
        frame = tk.Frame(self.root, bg="#f6f9ff")
        frame.pack(fill="x", padx=18, pady=(0, 16))

        self.start_button = tk.Button(frame, text="Starta", command=self.start_game, font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", width=12)
        self.start_button.grid(row=0, column=0, padx=8, pady=4)

        self.pause_button = tk.Button(frame, text="Pausa", command=self.toggle_pause, font=("Arial", 12, "bold"), bg="#f39c12", fg="white", width=12)
        self.pause_button.grid(row=0, column=1, padx=8, pady=4)

        self.restart_button = tk.Button(frame, text="Nytt spel", command=self.restart_game, font=("Arial", 12, "bold"), bg="#3498db", fg="white", width=12)
        self.restart_button.grid(row=0, column=2, padx=8, pady=4)

        return frame

    def bind_keys(self):
        self.root.bind("<KeyPress-Left>", self.handle_left_press)
        self.root.bind("<KeyPress-Right>", self.handle_right_press)
        self.root.bind("<KeyRelease-Left>", self.handle_left_release)
        self.root.bind("<KeyRelease-Right>", self.handle_right_release)
        self.root.bind("<space>", self.handle_space)

    def handle_left_press(self, event):
        self.keys["left"] = True

    def handle_right_press(self, event):
        self.keys["right"] = True

    def handle_left_release(self, event):
        self.keys["left"] = False

    def handle_right_release(self, event):
        self.keys["right"] = False

    def handle_space(self, event):
        if self.state == "ready":
            self.start_game()
        elif self.state == "paused":
            self.toggle_pause()
        elif self.state == "running":
            self.toggle_pause()
        elif self.state == "game_over":
            self.restart_game()

    def prepare_background(self):
        self.background = []
        for _ in range(24):
            self.background.append(
                {
                    "x": random_between(0, self.width),
                    "y": random_between(0, self.height - 180),
                    "size": random_between(2, 5),
                    "speed": random_between(1, 4),
                }
            )

    def draw_background(self):
        self.canvas.delete("background")
        for star in self.background:
            self.canvas.create_oval(star["x"], star["y"], star["x"] + star["size"], star["y"] + star["size"], fill="#7aa7d9", outline="#7aa7d9", tags="background")
            star["y"] += star["speed"]
            if star["y"] > self.height - 180:
                star["y"] = -10
                star["x"] = random_between(0, self.width)

    def reset_game(self):
        self.score = 0
        self.level = 1
        self.lives = 3
        self.time_left = 45
        self.objects = []
        self.particles = []
        self.clear_canvas()
        self.create_player()
        self.update_hud()
        self.show_message("Tryck på Starta eller SPACE")
        self.state = "ready"

    def clear_canvas(self):
        self.canvas.delete("all")
        self.draw_background()

    def create_player(self):
        if self.player is not None:
            self.canvas.delete(self.player)

        x = self.width // 2
        y = self.height - 120
        player = self.canvas.create_polygon(
            x, y - 18,
            x - 18, y + 18,
            x + 18, y + 18,
            fill="#ffd166",
            outline="#b88200",
            width=3,
            tags="player",
        )
        self.player = player

    def update_hud(self):
        self.score_label.config(text=f"Poäng: {self.score}")
        self.level_label.config(text=f"Nivå: {self.level}")
        self.lives_label.config(text=f"Liv: {self.lives}")
        self.timer_label.config(text=f"Tid: {int(self.time_left)}s")

    def show_message(self, text):
        self.msg = text
        self.canvas.delete("message")
        self.canvas.create_text(self.width / 2, self.height - 160, text=text, font=("Arial", 15, "bold"), fill="#11263e", tags="message")

    def start_game(self):
        if self.state == "running":
            return
        self.state = "running"
        self.clear_canvas()
        self.create_player()
        self.update_hud()
        self.show_message("Kör!")
        self.start_tick_loop()

    def restart_game(self):
        self.cancel_tick_loop()
        self.reset_game()
        self.start_game()

    def toggle_pause(self):
        if self.state == "running":
            self.state = "paused"
            self.show_message("Pausad")
            self.cancel_tick_loop()
        elif self.state == "paused":
            self.state = "running"
            self.show_message("Kör!")
            self.start_tick_loop()

    def move_player(self):
        if self.player is None:
            return

        if self.keys["left"]:
            self.canvas.move("player", -self.player_speed, 0)
        if self.keys["right"]:
            self.canvas.move("player", self.player_speed, 0)

        player_coords = self.canvas.coords(self.player)
        left = min(player_coords[0], player_coords[2], player_coords[4])
        right = max(player_coords[0], player_coords[2], player_coords[4])
        left = clamp(left, 20, self.width - 20)
        right = clamp(right, 20, self.width - 20)

        if left < 20:
            self.canvas.move("player", 20 - left, 0)
        if right > self.width - 20:
            self.canvas.move("player", (self.width - 20) - right, 0)

    def create_star_shape(self, x, y, radius, fill, outline, width):
        points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            dist = radius if i % 2 == 0 else radius * 0.45
            px = x + dist * math.cos(angle)
            py = y + dist * math.sin(angle)
            points.extend([px, py])
        return self.canvas.create_polygon(points, fill=fill, outline=outline, width=width)

    def create_hex_shape(self, x, y, radius, fill, outline, width):
        points = []
        for i in range(6):
            angle = math.radians(60 * i)
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.extend([px, py])
        return self.canvas.create_polygon(points, fill=fill, outline=outline, width=width)

    def spawn_good_item(self):
        x = random_between(30, self.width - 30)
        y = -20
        radius = random_between(10, 18)
        color = pick_color(["#2ecc71", "#00c896", "#3ad29f", "#61dafb"])
        item_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="#0d6b4e", width=2)
        self.objects.append({"id": item_id, "kind": "good", "x": x, "y": y, "radius": radius, "speed": random_between(3, 6) + self.level})

    def spawn_bad_item(self):
        x = random_between(30, self.width - 30)
        y = -20
        radius = random_between(12, 18)
        color = pick_color(["#e74c3c", "#d35400", "#c0392b", "#ff4d4d"])
        item_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="#7d1d1d", width=2)
        self.objects.append({"id": item_id, "kind": "bad", "x": x, "y": y, "radius": radius, "speed": random_between(4, 7) + self.level})

    def spawn_bonus_item(self):
        x = random_between(40, self.width - 40)
        y = -25
        radius = random_between(14, 20)
        item_id = self.create_star_shape(x, y, radius, "#ffd166", "#c79200", 3)
        self.objects.append({"id": item_id, "kind": "bonus", "x": x, "y": y, "radius": radius, "speed": random_between(2, 5) + self.level})

    def spawn_wave(self):
        if self.state != "running":
            return
        roll = random.random()
        if roll < 0.45:
            self.spawn_good_item()
        if roll < 0.25:
            self.spawn_bad_item()
        if roll > 0.8:
            self.spawn_bonus_item()

    def add_particles(self, x, y, color, count):
        for _ in range(count):
            particle = self.canvas.create_oval(x, y, x + 5, y + 5, fill=color, outline=color)
            self.particles.append({"id": particle, "x": x, "y": y, "dx": random_between(-4, 4), "dy": random_between(-4, 2), "life": 18})

    def update_particles(self):
        for particle in self.particles[:]:
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            particle["life"] -= 1
            self.canvas.coords(particle["id"], particle["x"], particle["y"], particle["x"] + 5, particle["y"] + 5)
            if particle["life"] <= 0:
                self.canvas.delete(particle["id"])
                self.particles.remove(particle)

    def update_objects(self):
        for item in self.objects[:]:
            item["y"] += item["speed"]
            self.canvas.move(item["id"], 0, item["speed"])

            if item["y"] > self.height - 70:
                if item["kind"] == "good":
                    self.score = max(0, self.score - 1)
                    self.add_particles(item["x"], item["y"], "#f1c40f", 12)
                elif item["kind"] == "bad":
                    self.lose_life()
                    self.add_particles(item["x"], item["y"], "#e74c3c", 18)
                elif item["kind"] == "bonus":
                    self.score += 4
                    self.add_particles(item["x"], item["y"], "#ffd166", 16)

                self.canvas.delete(item["id"])
                self.objects.remove(item)
                self.update_hud()

    def check_collisions(self):
        if self.player is None:
            return

        player_coords = self.canvas.coords(self.player)
        px = (player_coords[0] + player_coords[2] + player_coords[4]) / 3
        py = (player_coords[1] + player_coords[3] + player_coords[5]) / 3

        for item in self.objects[:]:
            dist = distance_between(px, py, item["x"], item["y"])
            if dist <= item["radius"] + 20:
                if item["kind"] == "good":
                    self.collect_good(item)
                elif item["kind"] == "bad":
                    self.collect_bad(item)
                elif item["kind"] == "bonus":
                    self.collect_bonus(item)

    def collect_good(self, item):
        self.score += 10
        self.add_particles(item["x"], item["y"], "#27ae60", 18)
        self.canvas.delete(item["id"])
        self.objects.remove(item)
        self.update_hud()

    def collect_bad(self, item):
        self.score = max(0, self.score - 5)
        self.add_particles(item["x"], item["y"], "#e74c3c", 20)
        self.canvas.delete(item["id"])
        self.objects.remove(item)
        self.update_hud()

    def collect_bonus(self, item):
        self.score += 25
        self.add_particles(item["x"], item["y"], "#ffd166", 24)
        self.canvas.delete(item["id"])
        self.objects.remove(item)
        self.update_hud()

    def lose_life(self):
        self.lives -= 1
        self.show_message(f"Miss! Liv kvar: {self.lives}")
        self.update_hud()
        if self.lives <= 0:
            self.end_game()

    def maybe_level_up(self):
        if self.score >= self.level * 100:
            self.level += 1
            self.player_speed += 1
            self.show_message(f"Nivå {self.level}!")
            self.update_hud()

    def tick(self):
        if self.state != "running":
            return

        self.draw_background()
        self.move_player()
        self.spawn_wave()
        self.update_objects()
        self.check_collisions()
        self.update_particles()
        self.maybe_level_up()
        self.time_left = max(0, self.time_left - 0.03)
        self.update_hud()

        if self.time_left <= 0:
            self.end_game()
            return

        self.after_id = self.root.after(30, self.tick)

    def start_tick_loop(self):
        self.cancel_tick_loop()
        self.after_id = self.root.after(30, self.tick)

    def cancel_tick_loop(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def end_game(self):
        self.state = "game_over"
        self.cancel_tick_loop()
        self.show_message("Spelet slut")
        self.canvas.create_text(self.width / 2, 90, text=f"Slutpoäng: {self.score}", font=("Arial", 22, "bold"), fill="#15263d", tags="summary")
        messagebox.showinfo("Game over", f"Du fick {self.score} poäng och nådde nivå {self.level}.")

    def run(self):
        self.root.mainloop()


def main():
    root = build_window("Catch the Sky", 820, 620)
    game = CatchTheSky(root)
    game.run()


if __name__ == "__main__":
    main()
