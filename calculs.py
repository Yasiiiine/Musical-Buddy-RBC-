class Calcul:
    @staticmethod
    def sum(a, b): return a + b
    @staticmethod
    def diff(a, b): return a - b
    @staticmethod
    def mult(a, b): return a * b
    @staticmethod
    def div(a, b): return "Erreur: division par zéro" if b == 0 else a / b
