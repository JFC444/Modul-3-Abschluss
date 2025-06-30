import json
import os

class UserManager:
    def __init__(self, dateiname="benutzer.json"):
        self.dateiname = dateiname
        self.benutzer = self.lade_benutzer()

    def lade_benutzer(self):
        if os.path.exists(self.dateiname):
            with open(self.dateiname, "r") as f:
                return json.load(f)
        return {}

    def speichere_benutzer(self):
        with open(self.dateiname, "w") as f:
            json.dump(self.benutzer, f)

    def registrieren(self, benutzername, passwort):
        if benutzername in self.benutzer:
            return False
        self.benutzer[benutzername] = passwort
        self.speichere_benutzer()
        return True

    def login(self, benutzername, passwort):
        return self.benutzer.get(benutzername) == passwort