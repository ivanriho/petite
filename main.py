#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                         CATCH THE SKY - SPELBESKRIVNING                    ║
╚════════════════════════════════════════════════════════════════════════════╝

Detta är ett arkadspel byggt med Python och Tkinter där spelaren kontrollerar
en gul triangel för att fånga fallande objekt från himlen.

SPELMEKANIK:
- Spelaren kontrolleras med VÄNSTER/HÖGER piltangenter
- Gröna cirklar: +10 poäng (bra att fånga)
- Röda cirklar: -5 poäng när fångade, -1 liv om de nå botten (farliga)
- Gula stjärnor: +25 poäng (bonus, sällsynta)
- Fallande stjärnor i bakgrunden: endast visuell effekt

NIVÅER OCH SVÅRIGHET:
- Spelet nivåer upp var 100:e poäng
- Objekten faller snabbare på högre nivåer
- Spelaren blir också snabbare

TID & ÄLSKA:
- Du har 45 sekunder per omgång
- Du börjar med 3 liv
- Missa en grön cirkel: -1 poäng
- Låt en röd cirkel nå botten: -1 liv
- När liv = 0: Game Over

PARTIKELEFFEKTER:
- När ett objekt fångas eller missar skapas färgade partiklar
- Partiklarna flyger slumpmässigt och försvinner efter kort tid

BACKGRUND:
- 24 stjärnor rör sig från toppen till botten
- Ger ett rörligt och liv fullo utseende
"""

import math
import random
import tkinter as tk
from tkinter import messagebox

# ═══════════════════════════════════════════════════════════════════════════
# HJÄLPFUNKTIONER - Användbara verktyg för spelet
# ═══════════════════════════════════════════════════════════════════════════

def clamp(value, minimum, maximum):
    # Begränsa ett värde mellan min och max (använd inte längre men finns här)
    return max(minimum, min(value, maximum))


def random_between(minimum, maximum):
    # Returnera ett slumpmässigt heltal mellan två värden
    return random.randint(minimum, maximum)


def distance_between(x1, y1, x2, y2):
    # Beräkna avståndet mellan två punkter (används för kollisionskontroll)
    return math.hypot(x2 - x1, y2 - y1)


def pick_color(options):
    # Välj en slumpmässig färg från en lista
    return random.choice(options)


def build_window(title, width, height):
    # Skapa och konfigurerar huvudfönstret för spelet
    root = tk.Tk()
    root.title(title)  # Sätt fönstrets titel
    root.geometry(f"{width}x{height}")  # Sätt fönstrets storlek
    root.resizable(False, False)  # Gör så man inte kan ändra storlek
    return root


# ═══════════════════════════════════════════════════════════════════════════
# HUVUDSPELKLASSEN - Styr all spelogik
# ═══════════════════════════════════════════════════════════════════════════

class CatchTheSky:
    # Denna klass hanterar alla aspekter av spelet: grafik, logik, input osv
    
    def __init__(self, root):
        # Initialisera spelet med alla variabler och inställningar
        self.root = root  # Referens till Tkinter-fönstret
        self.width = 820  # Spelfältets bredd i pixlar
        self.height = 620  # Spelfältets höjd i pixlar
        
        # Spelarens statistik
        self.score = 0  # Antal poäng spelaren har
        self.level = 1  # Vilken nivå spelaren är på
        self.lives = 3  # Antal liv kvar
        self.time_left = 45  # Sekunder kvar att spela
        self.state = "ready"  # Spelstatus: "ready", "running", "paused", "game_over"
        
        # Spelarens rörelse
        self.player_speed = 10  # Hur många pixlar per frame spelaren rör sig
        self.keys = {"left": False, "right": False}  # Vilka knappar är nedtryckta
        self.player = None  # ID för spelarens form på canvas
        
        # Objekt i spelet
        self.objects = []  # Lista med alla fallande objekt
        self.particles = []  # Lista med alla partikeleffekter
        self.background = []  # Lista med bakgrundsstjärnor
        
        # Tidskontroll
        self.after_id = None  # ID för Tkinter's timer (används för att uppdatera spelet)
        self.msg = ""  # Meddelande som visas på skärmen

        self.create_layout()
        self.prepare_background()
        self.reset_game()

    def create_layout(self):
        # Skapa all grafik för spelets användargränssnitt
        self.title = self.make_title()  # Titel "Catch the Sky"
        self.hud = self.make_hud()  # Poäng, nivå, liv, tid-display
        self.canvas = self.make_canvas()  # Huvudspelområdet
        self.buttons = self.make_buttons()  # Starta, Pausa, Nytt spel knappar
        self.bind_keys()  # Sätt upp tangentbordskontrroller

    def make_title(self):
        # Skapa en titel-etikett längst upp i fönstret
        label = tk.Label(self.root, text="Catch the Sky", font=("Arial", 24, "bold"), fg="#122033")
        label.pack(pady=(16, 6))  # Placera med mellanrum
        return label

    def make_hud(self):
        # Skapa informationspanelen (HUD = Heads Up Display)
        frame = tk.Frame(self.root, bg="#edf5ff")  # Container för all info
        frame.pack(fill="x", padx=18, pady=4)

        # Visa poäng
        self.score_label = tk.Label(frame, text="Poäng: 0", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.score_label.grid(row=0, column=0, padx=12, pady=6)

        # Visa nivå
        self.level_label = tk.Label(frame, text="Nivå: 1", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.level_label.grid(row=0, column=1, padx=12, pady=6)

        # Visa antal liv
        self.lives_label = tk.Label(frame, text="Liv: 3", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.lives_label.grid(row=0, column=2, padx=12, pady=6)

        # Visa tid kvar
        self.timer_label = tk.Label(frame, text="Tid: 45s", font=("Arial", 12, "bold"), bg="#edf5ff")
        self.timer_label.grid(row=0, column=3, padx=12, pady=6)

        return frame

    def make_canvas(self):
        # Skapa huvudspelområdet (canvas) där allt ritas
        canvas = tk.Canvas(self.root, width=self.width, height=self.height - 180, bg="#dfeeff", highlightthickness=2, highlightbackground="#adc6e8")
        canvas.pack(padx=18, pady=(6, 8))  # Placera med mellanrum
        return canvas

    def make_buttons(self):
        # Skapa knappar för att starta, pausa och starta om spelet
        frame = tk.Frame(self.root, bg="#f6f9ff")
        frame.pack(fill="x", padx=18, pady=(0, 16))

        # "Starta" knapp - grön
        self.start_button = tk.Button(frame, text="Starta", command=self.start_game, font=("Arial", 12, "bold"), bg="#2ecc71", fg="white", width=12)
        self.start_button.grid(row=0, column=0, padx=8, pady=4)

        # "Pausa" knapp - orange
        self.pause_button = tk.Button(frame, text="Pausa", command=self.toggle_pause, font=("Arial", 12, "bold"), bg="#f39c12", fg="white", width=12)
        self.pause_button.grid(row=0, column=1, padx=8, pady=4)

        # "Nytt spel" knapp - blå
        self.restart_button = tk.Button(frame, text="Nytt spel", command=self.restart_game, font=("Arial", 12, "bold"), bg="#3498db", fg="white", width=12)
        self.restart_button.grid(row=0, column=2, padx=8, pady=4)

        return frame

    def bind_keys(self):
        # Registrera tangentbordskommandon
        self.root.bind("<KeyPress-Left>", self.handle_left_press)  # Vänster pil nedtryckt
        self.root.bind("<KeyPress-Right>", self.handle_right_press)  # Höger pil nedtryckt
        self.root.bind("<KeyRelease-Left>", self.handle_left_release)  # Vänster pil släppt
        self.root.bind("<KeyRelease-Right>", self.handle_right_release)  # Höger pil släppt
        self.root.bind("<space>", self.handle_space)  # Mellanslag för start/pausa

    def handle_left_press(self, event):
        # Markera att vänster pil är nedtryckt
        self.keys["left"] = True

    def handle_right_press(self, event):
        # Markera att höger pil är nedtryckt
        self.keys["right"] = True

    def handle_left_release(self, event):
        # Markera att vänster pil är släppt
        self.keys["left"] = False

    def handle_right_release(self, event):
        # Markera att höger pil är släppt
        self.keys["right"] = False

    def handle_space(self, event):
        # Hantera SPACE-knappen - startar, pausar eller startar om spelet
        if self.state == "ready":
            self.start_game()  # Om redo: starta
        elif self.state == "paused":
            self.toggle_pause()  # Om pausad: fortsätt
        elif self.state == "running":
            self.toggle_pause()  # Om kör: pausa
        elif self.state == "game_over":
            self.restart_game()  # Om slut: starta nytt spel

    def prepare_background(self):
        # Skapa 24 slumpmässiga stjärnor för bakgrunden
        self.background = []
        for _ in range(24):
            self.background.append(
                {
                    "x": random_between(0, self.width),  # Slumpmässig x-position
                    "y": random_between(0, self.height - 180),  # Slumpmässig y-position
                    "size": random_between(2, 5),  # Stjärnans storlek
                    "speed": random_between(1, 4),  # Hur snabbt stjärnan faller
                }
            )

    def draw_background(self):
        # Rita alla bakgrundsstjärnor och flytta dem ned
        self.canvas.delete("background")  # Sudda föregående stjärnor
        for star in self.background:
            # Rita en oval (cirkel) för varje stjärna
            self.canvas.create_oval(star["x"], star["y"], star["x"] + star["size"], star["y"] + star["size"], fill="#7aa7d9", outline="#7aa7d9", tags="background")
            star["y"] += star["speed"]  # Flytta stjärnan ned
            # När stjärnan når botten: sätt den upphögt igen
            if star["y"] > self.height - 180:
                star["y"] = -10
                star["x"] = random_between(0, self.width)

    def reset_game(self):
        # Återställ alla spelvariablar för ett nytt spel
        self.score = 0  # Nollställ poäng
        self.level = 1  # Återställ till nivå 1
        self.lives = 3  # Ge 3 liv
        self.time_left = 45  # 45 sekunder att spela
        self.objects = []  # Ta bort alla fallande objekt
        self.particles = []  # Ta bort alla partiklar
        self.clear_canvas()  # Sudda canvas
        self.create_player()  # Skapa spelaren på nytt
        self.update_hud()  # Uppdatera info-displayen
        self.show_message("Tryck på Starta eller SPACE")  # Instruktion
        self.state = "ready"  # Weit för att spelaren startar spelet

    def clear_canvas(self):
        # Sudda allt på canvas och rita bakgrunden
        self.canvas.delete("all")  # Sudda alla element
        self.draw_background()  # Rita bakgrundsstärnor

    def create_player(self):
        # Skapa eller återskapar spelaren (en gul triangel)
        if self.player is not None:
            self.canvas.delete(self.player)  # Ta bort gammal spelare om den finns

        x = self.width // 2  # Centrera horizontellt
        y = self.height - 120  # Lägg längst ner
        # Skapa en triangel med 3 punkter
        player = self.canvas.create_polygon(
            x, y - 18,  # Övre punkt
            x - 18, y + 18,  # Vänster nedre punkt
            x + 18, y + 18,  # Höger nedre punkt
            fill="#ffd166",  # Gul färg
            outline="#b88200",  # Gul kant
            width=3,
            tags="player",
        )
        self.player = player

    def update_hud(self):
        # Uppdatera all info på skärmen (poäng, nivå, liv, tid)
        self.score_label.config(text=f"Poäng: {self.score}")
        self.level_label.config(text=f"Nivå: {self.level}")
        self.lives_label.config(text=f"Liv: {self.lives}")
        self.timer_label.config(text=f"Tid: {int(self.time_left)}s")

    def show_message(self, text):
        # Visa ett meddelande på mitten av canvas (för t ex "Kör!" eller "Pausad")
        self.msg = text
        self.canvas.delete("message")  # Ta bort gammal meddelande
        # Rita nytt meddelande
        self.canvas.create_text(self.width / 2, self.height - 160, text=text, font=("Arial", 15, "bold"), fill="#11263e", tags="message")

    def start_game(self):
        # Starta spelet (kallas när du klickar Start eller SPACE)
        if self.state == "running":
            return  # Om redan kör: gör ingenting
        self.state = "running"  # Ändra till "kör"
        self.clear_canvas()  # Sudda gammal canvas
        self.create_player()  # Skapa spelaren
        self.update_hud()  # Uppdatera info
        self.show_message("Kör!")  # Visa meddelande
        self.start_tick_loop()  # Börja spelet

    def restart_game(self):
        # Starta ett helt nytt spel (används när man klickar "Nytt spel")
        self.cancel_tick_loop()  # Stopp nuvarande spel
        self.reset_game()  # Återställ allt
        self.start_game()  # Starta på nytt

    def toggle_pause(self):
        # Växl mellan pausad och kör (t ex när du klickar Pausa)
        if self.state == "running":
            self.state = "paused"  # Ändra till pausad
            self.show_message("Pausad")
            self.cancel_tick_loop()  # Stopp uppdateringar
        elif self.state == "paused":
            self.state = "running"  # Ändra till kör
            self.show_message("Kör!")
            self.start_tick_loop()  # Fortsätt uppdateringar

    def move_player(self):
        # Flytta spelaren baserat på tangentbordsinmatning
        if self.player is None:
            return  # Inget att flytta om spelaren inte finns

        # Flytta vänster om vänster pil är nedtryckt
        if self.keys["left"]:
            self.canvas.move("player", -self.player_speed, 0)
        # Flytta höger om höger pil är nedtryckt
        if self.keys["right"]:
            self.canvas.move("player", self.player_speed, 0)

        # Hämta spelarens nuvarande position
        player_coords = self.canvas.coords(self.player)
        # Hitta minsta och största x-koordinat (spelarens vänstra och högra kanten)
        left = min(player_coords[0], player_coords[2], player_coords[4])
        right = max(player_coords[0], player_coords[2], player_coords[4])

        # Kontrollera skärmgränser och skjut tillbaka spelaren om den går ut
        if left < 20:
            self.canvas.move("player", 20 - left, 0)
        if right > self.width - 20:
            self.canvas.move("player", (self.width - 20) - right, 0)

    def create_star_shape(self, x, y, radius, fill, outline, width):
        # Skapa en 5-uddad stjärna med matematik (10 punkter som alternerar mellan lång och kort radie)
        points = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)  # 10 vinklar runt cirkeln
            dist = radius if i % 2 == 0 else radius * 0.45  # Varannan punkt är kortare
            px = x + dist * math.cos(angle)  # Beräkna x
            py = y + dist * math.sin(angle)  # Beräkna y
            points.extend([px, py])
        return self.canvas.create_polygon(points, fill=fill, outline=outline, width=width)

    def create_hex_shape(self, x, y, radius, fill, outline, width):
        # Skapa en hexagon (6-sidig form) med matematik
        points = []
        for i in range(6):
            angle = math.radians(60 * i)  # 6 vinklar runt cirkeln
            px = x + radius * math.cos(angle)  # Beräkna x
            py = y + radius * math.sin(angle)  # Beräkna y
            points.extend([px, py])
        return self.canvas.create_polygon(points, fill=fill, outline=outline, width=width)

    def spawn_good_item(self):
        # Skapa en grön cirkel (bra att fånga: +10 poäng)
        x = random_between(30, self.width - 30)  # Slumpmässig x-position
        y = -20  # Spawna över skärmen
        radius = random_between(10, 18)  # Slumpmässig storlek
        color = pick_color(["#2ecc71", "#00c896", "#3ad29f", "#61dafb"])  # En grön nians
        item_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="#0d6b4e", width=2)
        # Lagra objektets data
        self.objects.append({"id": item_id, "kind": "good", "x": x, "y": y, "radius": radius, "speed": random_between(3, 6) + self.level})

    def spawn_bad_item(self):
        # Skapa en röd cirkel (farlig! Minska poäng eller liv om den når botten)
        x = random_between(30, self.width - 30)  # Slumpmässig x-position
        y = -20  # Spawna över skärmen
        radius = random_between(12, 18)  # Slumpmässig storlek
        color = pick_color(["#e74c3c", "#d35400", "#c0392b", "#ff4d4d"])  # En röd nians
        item_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="#7d1d1d", width=2)
        # Lagra objektets data (Röda är snabbare)
        self.objects.append({"id": item_id, "kind": "bad", "x": x, "y": y, "radius": radius, "speed": random_between(4, 7) + self.level})

    def spawn_bonus_item(self):
        # Skapa en gul stjärna (sällsynt bonus: +25 poäng!)
        x = random_between(40, self.width - 40)  # Slumpmässig x-position
        y = -25  # Spawna över skärmen
        radius = random_between(14, 20)  # Slumpmässig storlek
        item_id = self.create_star_shape(x, y, radius, "#ffd166", "#c79200", 3)  # Stjärnform
        # Lagra objektets data (Bonus är långsamare)
        self.objects.append({"id": item_id, "kind": "bonus", "x": x, "y": y, "radius": radius, "speed": random_between(2, 5) + self.level})

    def spawn_wave(self):
        # Slumpmässigt skapa nya fallande objekt (varje frame)
        if self.state != "running":
            return  # Inget ska spawnas om spelet inte kör
        
        roll = random.random()  # Tal mellan 0.0 och 1.0
        
        # 45% chans för grön cirkel
        if roll < 0.45:
            self.spawn_good_item()
        # 20% chans för röd cirkel (45-65%)
        elif roll < 0.65:
            self.spawn_bad_item()
        # 20% chans för gul stjärna (65-85%)
        elif roll < 0.85:
            self.spawn_bonus_item()
        # 15% chans för ingenting (85-100%)

    def add_particles(self, x, y, color, count):
        # Skapa explosion-effekt: flera små partiklar som flyger slumpmässigt
        for _ in range(count):
            particle = self.canvas.create_oval(x, y, x + 5, y + 5, fill=color, outline=color)
            self.particles.append({
                "id": particle,  # Canvas ID
                "x": x,  # X-position
                "y": y,  # Y-position
                "dx": random_between(-4, 4),  # Slumpmässig hastighet i x-riktning
                "dy": random_between(-4, 2),  # Slumpmässig hastighet i y-riktning
                "life": 18  # Antal frames innan partikeln försvinner
            })

    def update_particles(self):
        # Uppdatera alla partiklar: flytta dem, dra ner de känner gravitation, och radera när de dör
        for particle in self.particles[:]:
            particle["x"] += particle["dx"]  # Flytta i x-riktning
            particle["y"] += particle["dy"]  # Flytta i y-riktning
            particle["life"] -= 1  # Minska livstid
            # Uppdatera partikelns position på canvas
            self.canvas.coords(particle["id"], particle["x"], particle["y"], particle["x"] + 5, particle["y"] + 5)
            # När partikeln dör: ta bort den
            if particle["life"] <= 0:
                self.canvas.delete(particle["id"])
                self.particles.remove(particle)

    def update_objects(self):
        # Uppdatera alla fallande objekt: flytta ned dem och se om de missar
        for item in self.objects[:]:
            item["y"] += item["speed"]  # Flytta objektet ned baserat på dess hastighet
            self.canvas.move(item["id"], 0, item["speed"])  # Uppdatera canvas

            # Kontrollera om objektet når botten utan att bli fångat
            if item["y"] > self.height - 70:
                if item["kind"] == "good":
                    # Miss en grön: förlora 1 poäng
                    self.score = max(0, self.score - 1)
                    self.add_particles(item["x"], item["y"], "#f1c40f", 12)
                elif item["kind"] == "bad":
                    # Miss en röd: förlora 1 liv! (och få varning)
                    self.lose_life()
                    self.add_particles(item["x"], item["y"], "#e74c3c", 18)
                elif item["kind"] == "bonus":
                    # Miss en bonus: förlora 4 poäng
                    self.score += 4  # Egentligen ett misslyckande, så vi ger poäng här
                    self.add_particles(item["x"], item["y"], "#ffd166", 16)

                # Ta bort objektet från listan och canvas
                self.canvas.delete(item["id"])
                self.objects.remove(item)
                self.update_hud()

    def check_collisions(self):
        # Kontrollera om spelaren kolliderar med fallande objekt
        if self.player is None:
            return  # Inget att kollidera med om spelaren inte finns

        # Hämta spelarens koordinater (det är en triangel med 3 hörn)
        player_coords = self.canvas.coords(self.player)
        # Beräkna spelarens mittpunkt (medelvärdet av alla 3 hörn)
        px = (player_coords[0] + player_coords[2] + player_coords[4]) / 3
        py = (player_coords[1] + player_coords[3] + player_coords[5]) / 3

        # Gå igenom alla fallande objekt och se om spelaren kolliderade med någon
        for item in self.objects[:]:
            dist = distance_between(px, py, item["x"], item["y"])  # Beräkna avstånd mellan spelare och objekt
            if dist <= item["radius"] + 20:  # Om avstånd är mindre än radierna tillsammans: kollision!
                if item["kind"] == "good":
                    self.collect_good(item)  # Fångade en grön
                elif item["kind"] == "bad":
                    self.collect_bad(item)  # Fångade en röd
                elif item["kind"] == "bonus":
                    self.collect_bonus(item)  # Fångade en bonus

    def collect_good(self, item):
        # Spelaren fångade en grön cirkel: +10 poäng!
        self.score += 10
        self.add_particles(item["x"], item["y"], "#27ae60", 18)  # Grön explosion
        self.canvas.delete(item["id"])  # Ta bort från canvas
        self.objects.remove(item)  # Ta bort från lista
        self.update_hud()  # Uppdatera poäng-displayen

    def collect_bad(self, item):
        # Spelaren fångade en röd cirkel: -5 poäng (olyckligtvis!)
        self.score = max(0, self.score - 5)
        self.add_particles(item["x"], item["y"], "#e74c3c", 20)  # Röd explosion
        self.canvas.delete(item["id"])  # Ta bort från canvas
        self.objects.remove(item)  # Ta bort från lista
        self.update_hud()  # Uppdatera poäng-displayen

    def collect_bonus(self, item):
        # Spelaren fångade en gul stjärna: +25 poäng (jackpot!)
        self.score += 25
        self.add_particles(item["x"], item["y"], "#ffd166", 24)  # Gul explosion
        self.canvas.delete(item["id"])  # Ta bort från canvas
        self.objects.remove(item)  # Ta bort från lista
        self.update_hud()  # Uppdatera poäng-displayen

    def lose_life(self):
        # Spelaren förlorade ett liv (när en röd cirkel nått botten)
        self.lives -= 1  # Minska antal liv
        self.show_message(f"Miss! Liv kvar: {self.lives}")  # Visa meddelande
        self.update_hud()  # Uppdatera liv-displayen
        # Om inga liv kvar: spelet är över
        if self.lives <= 0:
            self.end_game()

    def maybe_level_up(self):
        # Kontrollera om spelaren ska gå upp en nivå
        if self.score >= self.level * 100:  # Varje nivå kräver 100 * nivånummer poäng
            self.level += 1  # Gå upp en nivå
            self.player_speed += 1  # Spelaren blir snabbare
            self.show_message(f"Nivå {self.level}!")  # Visa gratismeddelande
            self.update_hud()  # Uppdatera nivå-displayen

    def tick(self):
        # HUVUDSPELETS UPPDATERINGSFUNKTION - kallas ~33 gånger per sekund
        if self.state != "running":
            return  # Inget ska uppdateras om spelet inte kör

        # Uppdatera alla element i spelet i rätt ordning:
        self.draw_background()  # Rita bakgrundsstjärnor
        self.move_player()  # Flytta spelaren baserat på tangentbordsinmatning
        self.spawn_wave()  # Skapa nya fallande objekt
        self.update_objects()  # Flytta ner alla fallande objekt
        self.check_collisions()  # Se om spelaren fångade något
        self.update_particles()  # Uppdatera och rita partikeleffekter
        self.maybe_level_up()  # Kontrollera om spelaren ska gå upp en nivå
        self.time_left = max(0, self.time_left - 0.03)  # Minska tiden (- 0.03 per frame)
        self.update_hud()  # Uppdatera poäng/nivå/liv/tid-displayen

        # Kontrollera om tiden är slut
        if self.time_left <= 0:
            self.end_game()  # Avsluta spelet
            return

        # Schemalägg nästa uppdatering om 30 millisekunder
        self.after_id = self.root.after(30, self.tick)

    def start_tick_loop(self):
        # Sluta eventuell gammal timer och starta en ny
        self.cancel_tick_loop()  # Avsluta eventuell tidigare timer
        self.after_id = self.root.after(30, self.tick)  # Schemalägga första tick om 30ms

    def cancel_tick_loop(self):
        # Stoppa spel-loopen (pausar spelet)
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)  # Avbryt den schemalagda tick:en
            self.after_id = None

    def end_game(self):
        # Avsluta spelet och visa resultat
        self.state = "game_over"  # Ändra spelets tillstånd
        self.cancel_tick_loop()  # Sluta uppdatera spelet
        self.show_message("Spelet slut")  # Visa meddelande på canvas
        # Rita slutresultatet på canvas
        self.canvas.create_text(self.width / 2, 90, text=f"Slutpoäng: {self.score}", font=("Arial", 22, "bold"), fill="#15263d", tags="summary")
        # Visa en popup-ruta med slutresultatet
        messagebox.showinfo("Game over", f"Du fick {self.score} poäng och nådde nivå {self.level}.")

    def run(self):
        # Starta Tkinter-loopen och gör GUI interaktiv
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════════════════
# PROGRAMMETS STARTPUNKT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    # Huvudfunktion - startar hela spelet
    root = build_window("Catch the Sky", 820, 620)  # Skapa fönstret
    game = CatchTheSky(root)  # Skapa spel-objektet
    game.run()  # Starta spelet


if __name__ == "__main__":
    # Denna kod körs bara om filen körs direkt (inte om den importeras)
    main()
