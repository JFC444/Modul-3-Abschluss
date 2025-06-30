import random

class QuizLogic:
    def __init__(self, fragen):
        self.fragen = random.sample(fragen, len(fragen))
        self.frage_index = 0
        self.punkte = 0

    def aktuelle_frage(self):
        return self.fragen[self.frage_index]

    def pruefe_antwort(self, antwort_index):
        richtig = self.fragen[self.frage_index]["antwort"] == antwort_index
        if richtig:
            self.punkte += 1
        self.frage_index += 1
        return richtig

    def quiz_beendet(self):
        return self.frage_index >= len(self.fragen)