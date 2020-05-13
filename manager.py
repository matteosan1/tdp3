import json, datetime, random

from contrada import Contrada
from cavallo import Cavallo
from fantino import Fantino

class TdPManager:
    random.seed(1)
    PHASES = ("Estrazione Lug", "Tratta Lug", "Palio Lug", "Estrazione Ago",
              "Tratta Ago", "Palio Ago", "Estrazione Str", "Tratta Str", "Palio Str")
    def __init__(self):
        self.anno = 2020
        self.mese = 7
        self.contrade = []
        self.fantini = []
        self.cavalli = []
        self.iPhase = 3

        data = json.load(open("contrade.json"))
        for d in data:
            self.contrade.append(Contrada(d))
        data = json.load(open("cavalli.json"))
        for d in data:
            self.cavalli.append(Cavallo(d))
        data = json.load(open("fantini.json"))
        for d in data:
            self.fantini.append(Fantino(d))

        self.luglio = [c.nome for c in random.sample(self.contrade, 17)]
        self.agosto = [c.nome for c in random.sample(self.contrade, 17)]

    def nextPhase(self):
        self.iPhase += 1

        if self.iPhase == 6: #len(self.PHASES):
            self.iPhase = 0
            self.anno += 1

    def estrazione(self):
        if self.iPhase == 0:
            self.luglio = self.luglio[:7] + [c for c in random.sample(self.luglio[7:], 10)]
            self.corrono = self.luglio[:10]
        elif self.iPhase == 3:
            self.agosto = self.agosto[:7] + [c for c in random.sample(self.agosto[7:], 10)]
            self.corrono = self.agosto[:10]

    def assegnazione(self):
        pass