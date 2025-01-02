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

    def to_chomsky_normal_form(self):
        """
        Convertir le CFG en forme normale de Chomsky.
        """
        # Étape 1 : Éliminer les productions epsilon
        self._eliminate_epsilon_rules()

        # Étape 2 : Éliminer les productions unitaires
        self._eliminate_unit_rules()

        # Étape 3 : Éliminer les productions de longueur supérieure à 2
        self._eliminate_long_rules()

        # Étape 4 : Extraire les terminaux dans des productions séparées
        self._eliminate_mixed_rules()
        self._remove_unused_non_terminals()

    def to_greibach_normal_form(self):
        """
        Convertir le CFG en forme normale de Greibach.
        """
        # Étape 1 : Éliminer les productions unitaires et epsilon
        self._eliminate_epsilon_rules()
        self._eliminate_unit_rules()

        # Étape 2 : Éliminer la récursion à gauche
        self._eliminate_left_recursion()

        # Étape 3 : Assurer que toutes les productions commencent par un terminal
        self._ensure_terminal_prefix()

        # Étape 4 : Nettoyer les non-terminaux inutilisés
        self._remove_unused_non_terminals()

    def _eliminate_epsilon_rules(self):
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

        if 'E' not in self.productions[self.axiome]:
            for nt in nullable:
                if nt == self.axiome:
                    self.productions[self.axiome].append('E')
                    break

    def _eliminate_unit_rules(self):
        """
        Éliminer les productions unitaires (unit rules).
        """
        for nt in list(self.productions.keys()):
            unit_productions = [p for p in self.productions[nt] if len(p) == 1 and p in self.non_terminals]
            while unit_productions:
                unit = unit_productions.pop()
                self.productions[nt].remove(unit)
                self.productions[nt].extend(self.productions[unit])

    def _eliminate_long_rules(self):
        """
        Éliminer les productions dont la partie droite a une longueur supérieure à 2.
        """
        new_rules = {}
        for nt in list(self.productions.keys()):
            new_productions = []
            for prod in self.productions[nt]:
                while len(prod) > 2:
                    new_nt = self._generate_new_non_terminal()
                    self.non_terminals.add(new_nt)
                    new_rules[new_nt] = [prod[:2]]
                    prod = new_nt + prod[2:]
                new_productions.append(prod)
            self.productions[nt] = new_productions
        self.productions.update(new_rules)

    def _eliminate_mixed_rules(self):
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
                                new_nt = self._generate_new_non_terminal()
                                self.non_terminals.add(new_nt)
                                self.productions[new_nt] = [c]
                                mapping[c] = new_nt
                            new_prod += mapping[c]
                        else:
                            new_prod += c
                    new_productions.append(new_prod)
            self.productions[nt] = new_productions


    def _generate_new_non_terminal(self):
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

    def _eliminate_left_recursion(self):
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
                new_nt = self._generate_new_non_terminal()
                self.non_terminals.add(new_nt)
                self.productions[new_nt] = [alpha + new_nt for alpha in alpha_productions] + ['E']
                self.productions[nt_i] = [beta + new_nt for beta in beta_productions]

    def _ensure_terminal_prefix(self):
        """
        Assurer que chaque production commence par un terminal, tout en évitant les règles redondantes.
        """
        for nt in list(self.productions.keys()):
            updated_productions = []
            for prod in self.productions[nt]:
                if prod == 'E':  # Si la production est epsilon, la conserver telle quelle
                    updated_productions.append(prod)
                    continue

                if prod[0].islower():  # Si la production commence déjà par un terminal
                    updated_productions.append(prod)
                else:  # Si la production commence par un non-terminal
                    prefix = prod[0]
                    suffix = prod[1:]
                    if prefix not in self.productions:
                        raise KeyError(f"Le non-terminal '{prefix}' n'a pas de production définie.")
                    for replacement in self.productions[prefix]:
                        # Si replacement commence déjà par un terminal, concaténer directement
                        if replacement[0].islower():
                            candidate = replacement + suffix
                            if candidate not in updated_productions:
                                updated_productions.append(candidate)
                        else:
                            # Éviter de générer des non-terminaux intermédiaires superflus
                            for final_prod in self._expand_to_terminal_prefix(replacement + suffix):
                                if final_prod not in updated_productions:
                                    updated_productions.append(final_prod)
            self.productions[nt] = list(set(updated_productions))  # Éviter les doublons

    def _expand_to_terminal_prefix(self, prod):
        """
        Développer la production jusqu'à ce qu'elle commence par un terminal.

        :param prod: Production d'entrée
        :return: Liste de productions qui commencent par un terminal
        """
        if prod == 'E':  # Retourner directement epsilon si c'est une production
            return ['E']

        if prod[0].islower():  # Si le premier symbole est un terminal
            return [prod]

        results = []
        prefix = prod[0]
        suffix = prod[1:]
        if prefix not in self.productions:
            raise KeyError(f"Le non-terminal '{prefix}' n'a pas de production définie.")

        for replacement in self.productions[prefix]:
            results.extend(self._expand_to_terminal_prefix(replacement + suffix))
        return results

    def _remove_unused_non_terminals(self):
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
