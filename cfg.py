import string

class CFG:
    def __init__(self, axiome='S'):
        """
        Initialiser un format CFG, contenant l'ensemble des non-terminaux, l'ensemble des terminaux, le symbole de départ et les règles de production.

        :param axiome: Le symbole de départ, par défaut 'S'
        """
        self.non_terminals = set()  # Ensemble des non-terminaux
        self.terminals = set()  # Ensemble des terminaux
        self.productions = {}  # Règles de production, format {non-terminal: [liste de productions]}
        self.axiome = axiome  # Symbole de départ

    def add_production(self, non_terminal, production_list):
        """
        Ajouter des règles de production.

        :param non_terminal: Non-terminal
        :param production_list: Liste des productions (list de str)
        """
        if non_terminal not in self.non_terminals:
            self.non_terminals.add(non_terminal)

        if non_terminal in self.productions:
            self.productions[non_terminal].extend(production_list)
        else:
            self.productions[non_terminal] = production_list

        # Mettre à jour les ensembles des terminaux et des non-terminaux
        for production in production_list:
            for char in production:
                if char.islower():  # Les lettres minuscules sont des terminaux
                    self.terminals.add(char)
                elif char.isupper() and char != 'E':  # Les lettres majuscules (sauf 'E') sont des non-terminaux
                    self.non_terminals.add(char)

    def add_production_with_validation(self, non_terminal, production_list):
        if not CFG.is_valid_non_terminal(non_terminal):
            raise ValueError(f"'{non_terminal}' n'est pas un non-terminal valide !")

        for production in production_list:
            if not CFG.is_valid_production(production):
                raise ValueError(f"'{production}' n'est pas une production valide !")

        self.add_production(non_terminal, production_list)

    def display(self):
        """
        Afficher l'ensemble des non-terminaux, des terminaux, du symbole de départ et des règles de production du CFG.
        """
        print("Ensemble des non-terminaux:", self.non_terminals)
        print("Ensemble des terminaux:", self.terminals)
        print("Symbole de départ:", self.axiome)
        print("Règles de production:")
        for non_terminal, productions in self.productions.items():
            print(f"  {non_terminal} -> {' | '.join(productions)}")

    @staticmethod
    def is_valid_non_terminal(symbol):
        """
        Vérifier si le symbole est un non-terminal valide.

        :param symbol: Symbole
        :return: Booléen
        """
        return len(symbol) == 1 and symbol.isupper() and symbol != 'E'

    @staticmethod
    def is_valid_terminal(symbol):
        """
        Vérifier si le symbole est un terminal valide.

        :param symbol: Symbole
        :return: Booléen
        """
        return len(symbol) == 1 and symbol.islower()

    @staticmethod
    def is_valid_production(production):
        """
        Vérifier si la production est valide (composée de non-terminaux, terminaux ou de la chaîne vide).

        :param production: Production
        :return: Booléen
        """
        return all(c.islower() or (c.isupper() and c != 'E') or c == 'E' for c in production)

    def chomsky(self):
        """
        Convertir le CFG en forme normale de Chomsky.
        """
        # Étape 1 : Extraire les terminaux dans des productions séparées
        self.extraire_terminaux_regles()

        # Étape 2 : Éliminer les productions de non-terminaux de longueur supérieure à 2
        self.eliminer_long_regles()

        # Étape 3 : Éliminer les productions epsilon
        self.eliminer_epsilon_regles()

        # Étape 4 : Éliminer les productions unitaires
        self.eliminer_unit_regles()

        # Étape 5 : Nettoyer les non-terminaux inutilisés
        self.supprimer_unused_non_terminal()

    def greibach(self):
        """
        Convertir le CFG en forme normale de Greibach.
        """
        # Étape 1 : Éliminer les productions unitaires et epsilon
        self.eliminer_epsilon_regles()
        self.eliminer_unit_regles()

        # Étape 2 : Éliminer la récursion à gauche
        self.eliminer_left_recursion()

        # Étape 3 : Assurer que toutes les productions commencent par un terminal
        self.assurer_terminal_premier()

        # Étape 4 : Nettoyer les non-terminaux inutilisés
        self.supprimer_unused_non_terminal()

    def eliminer_epsilon_regles(self):
        """
        Éliminer les productions epsilon (règles nullables) tout en gardant certaines règles spécifiées comme S->E.
        """
        # Trouver tous les non-terminaux qui peuvent générer la chaîne vide
        nullable = {nt for nt, productions in self.productions.items() if 'E' in productions}

        while True:
            new_nullable = nullable.copy()
            for nt, productions in self.productions.items():
                for prod in productions:
                    if all(symbol in nullable for symbol in prod):  # Si la partie droite de la production est entièrement nullable
                        new_nullable.add(nt)
            if new_nullable == nullable:
                break
            nullable = new_nullable

        # Mettre à jour les règles, supprimer les productions epsilon et ajouter toutes les combinaisons possibles non-nulles
        for nt in list(self.productions.keys()):
            new_productions = set()
            for prod in self.productions[nt]:
                if prod == 'E' and nt == self.axiome:
                    new_productions.add('E')  # Conserver S -> E si S est l'axiome
                    continue
                if prod == 'E':
                    continue  # Supprimer les autres chaînes vides
                options = [
                    [symbol, ''] if symbol in nullable else [symbol]
                    for symbol in prod
                ]
                from itertools import product
                for option in product(*options):
                    new_prod = ''.join(option)
                    if new_prod:  # Ajouter uniquement les combinaisons non-nulles
                        new_productions.add(new_prod)
            self.productions[nt] = list(new_productions)

        if 'E' not in self.productions[self.axiome] and self.axiome in nullable:
            self.productions[self.axiome].append('E')

    def eliminer_unit_regles(self):
        """
        Éliminer les productions unitaires (unit rules).
        """
        for nt in list(self.productions.keys()):
            unit_productions = [p for p in self.productions[nt] if len(p) == 1 and p in self.non_terminals]
            while unit_productions:
                unit = unit_productions.pop()
                self.productions[nt].remove(unit)
                self.productions[nt].extend(self.productions[unit])

    def eliminer_long_regles(self):
        """
        Éliminer les productions dont la partie droite a une longueur supérieure à 2.
        """
        new_rules = {}
        for nt in list(self.productions.keys()):
            new_productions = []
            for prod in self.productions[nt]:
                while len(prod) > 2:
                    new_nt = self.generer_new_non_terminal()
                    self.non_terminals.add(new_nt)
                    new_rules[new_nt] = [prod[:2]]
                    prod = new_nt + prod[2:]
                new_productions.append(prod)
            self.productions[nt] = new_productions
        self.productions.update(new_rules)

    def extraire_terminaux_regles(self):
        """
        Extraire les terminaux dans des productions séparées.
        """
        mapping = {}
        for nt in list(self.productions.keys()):
            new_productions = []
            for prod in self.productions[nt]:
                if len(prod) == 1 or all(c.isupper() for c in prod):
                    new_productions.append(prod)
                else:
                    new_prod = ''
                    for c in prod:
                        if c.islower():
                            if c not in mapping:
                                new_nt = self.generer_new_non_terminal()
                                self.non_terminals.add(new_nt)
                                self.productions[new_nt] = [c]
                                mapping[c] = new_nt
                            new_prod += mapping[c]
                        else:
                            new_prod += c
                    new_productions.append(new_prod)
            self.productions[nt] = new_productions


    def generer_new_non_terminal(self):
        """
        Générer un nouveau non-terminal.
        """
        # Essayer de générer de A à Z
        for c in string.ascii_uppercase:
            if c not in self.non_terminals and c != 'E':
                return c

        # Si A-Z est déjà utilisé, utiliser une combinaison lettre+chiffre
        for letter in string.ascii_uppercase:
            for number in range(1, 10):  # Limiter les chiffres de 1 à 9
                new_nt = f"{letter}{number}"
                if new_nt not in self.non_terminals and new_nt != 'E':
                    self.non_terminals.add(new_nt)
                    return new_nt

    def eliminer_left_recursion(self):
        """
        Éliminer la récursion directe et indirecte à gauche.
        """
        non_terminals = list(self.non_terminals)
        for i in range(len(non_terminals)):
            nt_i = non_terminals[i]
            new_productions = []

            # Remplacer la récursion indirecte à gauche
            for j in range(i):
                nt_j = non_terminals[j]
                updated_productions = []
                for prod in self.productions[nt_i]:
                    if prod.startswith(nt_j):
                        for beta in self.productions[nt_j]:
                            updated_productions.append(beta + prod[1:])
                    else:
                        updated_productions.append(prod)
                self.productions[nt_i] = updated_productions

            # Éliminer la récursion directe à gauche
            alpha_productions = []
            beta_productions = []
            for prod in self.productions[nt_i]:
                if prod.startswith(nt_i):
                    alpha_productions.append(prod[1:])
                else:
                    beta_productions.append(prod)

            if alpha_productions:
                new_nt = self.generer_new_non_terminal()
                self.non_terminals.add(new_nt)
                self.productions[new_nt] = [alpha + new_nt for alpha in alpha_productions] + ['E']
                self.productions[nt_i] = [beta + new_nt for beta in beta_productions]

    def assurer_terminal_premier(self):
        for nt in list(self.productions.keys()):
            updated_productions = set()  
            for prod in self.productions[nt]:
                if prod == 'E':  
                    if nt == self.axiome:
                        updated_productions.add(prod)
                    continue

                if prod[0].islower():  
                    updated_productions.add(prod)
                else:  
                    prefix = prod[0]
                    suffix = prod[1:]
                    if prefix not in self.productions:
                        raise KeyError(f"Le non-terminal '{prefix}' n'a pas de production définie.")
                    for replacement in self.productions[prefix]:
                        if replacement[0].islower():
                            updated_productions.add(replacement + suffix)
                        else:
                            for final_prod in self._expand_to_terminal_prefix(replacement + suffix):
                                updated_productions.add(final_prod)
            self.productions[nt] = list(updated_productions)

    def _expand_to_terminal_prefix(self, prod, cache=None):
        if cache is None:
            cache = {}
        if prod in cache:
            return cache[prod]

        if prod == 'E':
            return ['E']

        if prod[0].islower():
            return [prod]

        results = []
        prefix = prod[0]
        suffix = prod[1:]
        if prefix not in self.productions:
            raise KeyError(f"Le non-terminal '{prefix}' n'a pas de production définie.")

        for replacement in self.productions[prefix]:
            if replacement == 'E':
                if suffix:
                    results.extend(self._expand_to_terminal_prefix(suffix, cache))
            else:
                results.extend(self._expand_to_terminal_prefix(replacement + suffix, cache))

        cache[prod] = results
        return results


    def supprimer_unused_non_terminal(self):
        """
        Supprimer les non-terminaux inutilisés et les règles superflues.
        """
        used = {self.axiome}
        stack = [self.axiome]

        while stack:
            nt = stack.pop()
            for prod in self.productions.get(nt, []):
                for symbol in prod:
                    if symbol in self.non_terminals and symbol not in used:
                        used.add(symbol)
                        stack.append(symbol)

        # Supprimer les non-terminaux inutilisés
        self.non_terminals = used
        self.productions = {nt: prods for nt, prods in self.productions.items() if nt in used}
