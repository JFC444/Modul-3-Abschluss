import tkinter as tk
from tkinter import messagebox
from user_manager import UserManager
from quiz_logic import QuizLogic
import json
import os

def lade_fragen():
    if os.path.exists("fragen.json"):
        with open("fragen.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        messagebox.showerror("Fehler", "Die Datei 'fragen.json' wurde nicht gefunden!")
        return []

FRAGEN = lade_fragen()

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IT-Wissensquiz")
        self.user_manager = UserManager()
        self.quiz = None
        self.username = ""
        self.kategorie = None
        self.level = None
        self.login_fenster()

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
        if self.user_manager.login(benutzername, passwort):
            self.username = benutzername
            self.kategorie_auswahl()
        else:
            messagebox.showerror("Fehler", "Ungültiger Benutzername oder Passwort")

    def registrieren(self):
        benutzername = self.username_entry.get()
        passwort = self.passwort_entry.get()
        if self.user_manager.registrieren(benutzername, passwort):
            messagebox.showinfo("Erfolg", "Benutzer erfolgreich registriert")
        else:
            messagebox.showerror("Fehler", "Benutzername existiert bereits")

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
        # Filtere die Fragen nach Kategorie und Level
        gefilterte_fragen = [f for f in FRAGEN if f["kategorie"] == self.kategorie and f["level"] == self.level]
        if not gefilterte_fragen:
            messagebox.showerror("Fehler", "Keine Fragen für diese Auswahl gefunden!")
            self.kategorie_auswahl()
            return
        self.quiz = QuizLogic(gefilterte_fragen)
        self.start_quiz()

    def start_quiz(self):
        self.frage_label = None
        self.var = tk.IntVar()
        self.option_buttons = []
        self.clear()
        self.frage_label = tk.Label(self.root, text="", font=("Arial", 14), wraplength=500, justify="left")
        self.frage_label.pack(pady=20)

        for i in range(4):
            btn = tk.Radiobutton(self.root, text="", variable=self.var, value=i, font=("Arial", 12))
            btn.pack(anchor="w", padx=20)
            self.option_buttons.append(btn)

        self.next_button = tk.Button(self.root, text="Nächste Frage", command=self.naechste_frage, font=("Arial", 12))
        self.next_button.pack(pady=20)

        self.zeige_frage()

    def zeige_frage(self):
        frage = self.quiz.aktuelle_frage()
        self.frage_label.config(text=f"Frage {self.quiz.frage_index + 1}: {frage['frage']}")
        self.var.set(-1)
        for i, option in enumerate(frage["optionen"]):
            self.option_buttons[i].config(text=option)

    def naechste_frage(self):
        ausgewählt = self.var.get()
        if ausgewählt == -1:
            messagebox.showwarning("Hinweis", "Bitte wähle eine Antwort aus.")
            return

        self.quiz.pruefe_antwort(ausgewählt)

        if self.quiz.quiz_beendet():
            self.zeige_ergebnis()
        else:
            self.zeige_frage()

    def zeige_ergebnis(self):
        self.clear()
        punkte = self.quiz.punkte
        gesamt = len(self.quiz.fragen)
        ergebnis_text = f"{self.username}, du hast {punkte} von {gesamt} Punkten erreicht.\n\n"
        if punkte == gesamt:
            ergebnis_text += "🎉 Perfekt! Du hast alle Fragen richtig beantwortet!"
        elif punkte >= gesamt * 0.7:
            ergebnis_text += "👍 Sehr gut! Du hast ein solides Verständnis."
        elif punkte >= gesamt * 0.4:
            ergebnis_text += "⚠️ Noch ausbaufähig. Schau dir die Themen nochmal an."
        else:
            ergebnis_text += "❗ Du solltest das Thema nochmal durchgehen."

        ergebnis_label = tk.Label(self.root, text=ergebnis_text, font=("Arial", 14), wraplength=500, justify="left")
        ergebnis_label.pack(pady=50)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()