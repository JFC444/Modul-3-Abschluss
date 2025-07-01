import tkinter as tk
from tkinter import messagebox
import json
import os
import random

# Benutzerdatei laden oder erstellen
def lade_benutzer():
    if os.path.exists("benutzer.json"):
        with open("benutzer.json", "r") as f:
            return json.load(f)
    else:
        return {}

benutzer = lade_benutzer()

# Fragen aus JSON laden
def lade_fragen():
    if os.path.exists("fragen.json"):
        with open("fragen.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        messagebox.showerror("Fehler", "Die Datei 'fragen.json' wurde nicht gefunden!")
        return []

fragen = lade_fragen()
random.shuffle(fragen)

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IT-Wissensquiz")

        # Fenstergröße und Position (z.B. 900x500 Pixel, zentriert)
        fenster_breite = 900
        fenster_hoehe = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (fenster_breite / 2))
        y = int((screen_height / 2) - (fenster_hoehe / 2))
        self.root.geometry(f"{fenster_breite}x{fenster_hoehe}+{x}+{y}")

        self.username = ""
        self.kategorie = None
        self.level = None
        self.login_fenster()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_fenster(self):
        self.clear()
        tk.Label(self.root, text="Benutzername:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Passwort:").pack(pady=5)
        self.passwort_entry = tk.Entry(self.root, show="*")
        self.passwort_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Registrieren", command=self.registrieren).pack(pady=5)

    def login(self):
        benutzername = self.username_entry.get()
        passwort = self.passwort_entry.get()
        if benutzername in benutzer and benutzer[benutzername] == passwort:
            self.username = benutzername
            self.kategorie_auswahl()
        else:
            messagebox.showerror("Fehler", "Ungültiger Benutzername oder Passwort")

    def registrieren(self):
        benutzername = self.username_entry.get()
        passwort = self.passwort_entry.get()
        if benutzername in benutzer:
            messagebox.showerror("Fehler", "Benutzername existiert bereits")
        else:
            benutzer[benutzername] = passwort
            with open("benutzer.json", "w") as f:
                json.dump(benutzer, f)
            messagebox.showinfo("Erfolg", "Benutzer erfolgreich registriert")

    def start_quiz(self):
        # Filtere Fragen nach Kategorie/Level
        gefiltert = [f for f in fragen if
                     (self.kategorie is None or f.get("kategorie") == self.kategorie) and
                     (self.level is None or f.get("level") == self.level)]

        if not gefiltert:
            messagebox.showerror("Fehler", "Keine Fragen für die Auswahl gefunden.")
            return

        self.fragen = gefiltert
        random.shuffle(self.fragen)

        self.frage_index = 0
        self.punkte = 0

        self.clear()
        self.frage_label = tk.Label(self.root, text="", font=("Arial", 14), wraplength=500, justify="left", bg="#ffffff", fg="#000000")
        self.frage_label.pack(pady=20)

        self.var = tk.IntVar()
        self.option_buttons = []
        for i in range(4):
            btn = tk.Radiobutton(self.root, text="", variable=self.var, value=i, font=("Arial", 12))
            btn.pack(anchor="w", padx=20)
            self.option_buttons.append(btn)

        self.next_button = tk.Button(self.root, text="Nächste Frage", command=self.naechste_frage, font=("Arial", 12))
        self.next_button.pack(pady=20)

        self.zeige_frage()

    def zeige_frage(self):
        frage = self.fragen[self.frage_index]
        self.frage_label.config(text=f"Frage {self.frage_index + 1}: {frage['frage']}")
        self.var.set(-1)
        for i, option in enumerate(frage["optionen"]):
            self.option_buttons[i].config(text=option)

    def naechste_frage(self):
        ausgewählt = self.var.get()
        if ausgewählt == -1:
            messagebox.showwarning("Hinweis", "Bitte wähle eine Antwort aus.")
            return

        richtige_antwort = self.fragen[self.frage_index]["antwort"]
        if ausgewählt == richtige_antwort:
            self.punkte += 1

        self.frage_index += 1

        if self.frage_index >= len(self.fragen):
            self.zeige_ergebnis()
        else:
            self.zeige_frage()

    def zeige_ergebnis(self):
        self.clear()

        ergebnis_text = f"{self.username}, du hast {self.punkte} von {len(self.fragen)} Punkten erreicht.\n\n"
        if self.punkte == len(self.fragen):
            ergebnis_text += "🎉 Perfekt! Du hast alle Fragen richtig beantwortet!"
        elif self.punkte >= len(self.fragen) * 0.7:
            ergebnis_text += "👍 Sehr gut! Du hast ein solides Verständnis."
        elif self.punkte >= len(self.fragen) * 0.4:
            ergebnis_text += "⚠️ Noch ausbaufähig. Schau dir die Themen nochmal an."
        else:
            ergebnis_text += "❗ Du solltest das Thema nochmal durchgehen."

        # Ergebnis speichern
        ergebnis = {
            "benutzer": self.username,
            "punkte": self.punkte,
            "gesamt": len(self.fragen)
        }

        try:
            with open("ergebnisse.json", "r", encoding="utf-8") as f:
                daten = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            daten = []

        daten.append(ergebnis)

        with open("ergebnisse.json", "w", encoding="utf-8") as f:
            json.dump(daten, f, indent=2, ensure_ascii=False)

        ergebnis_label = tk.Label(self.root, text=ergebnis_text, font=("Arial", 14), wraplength=500, justify="left")
        ergebnis_label.pack(pady=50)

    def kategorie_auswahl(self):
        self.clear()
        tk.Label(self.root, text="Kategorie wählen:").pack(pady=5)
        self.kategorie_var = tk.StringVar(value="PowerShell")
        tk.OptionMenu(self.root, self.kategorie_var, "PowerShell", "Virtualisierung", "Automatisierung").pack(pady=5)

        tk.Label(self.root, text="Schwierigkeitsgrad wählen:").pack(pady=5)
        self.level_var = tk.StringVar(value="Einfach")
        tk.OptionMenu(self.root, self.level_var, "Einfach", "Mittel").pack(pady=5)

        tk.Button(self.root, text="Quiz starten", command=self.set_kategorie_level).pack(pady=10)

    def set_kategorie_level(self):
        self.kategorie = self.kategorie_var.get()
        self.level = self.level_var.get()
        self.start_quiz()

# Starte GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()


