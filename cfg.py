import string
import re

class CFG:
    def __init__(self, axiome=None):
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
        if not self.axiome:  # Si axiome n'est pas encore défini, définir le premier non-terminal ajouté comme axiome
            self.add_axiome(non_terminal)

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
                elif CFG.is_valid_non_terminal(char):  # Les lettres majuscules (sauf 'E') sont des non-terminaux
                    self.non_terminals.add(char)

    def add_axiome(self, non_terminal):
        """
        Définir le symbole de départ (axiome).

        :param non_terminal: Le non-terminal à définir comme axiome
        """
        if self.axiome is None:  
            self.axiome = non_terminal
        else:
            raise ValueError(f"L'axiome est déjà défini comme '{self.axiome}'.")

    def add_production_avec_validation(self, non_terminal, production_list):
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
        pattern = r'^[A-DF-Z][0-9]$'
        return bool(re.match(pattern, symbol))

    @staticmethod
    def is_valid_terminal(symbol):
        """
        Vérifier si le symbole est un terminal valide.

        :param symbol: Symbole
        :return: Booléen
        """
        return len(symbol) == 1 and symbol.islower()
    

    @staticmethod
    def split_production(production):
        """
        Découper une production en une liste de symboles (terminaux et non-terminaux).

        :param production: Production à découper
        :return: Liste des symboles
        """
        pattern = r'[A-DF-Z][0-9]|[a-z]|E'  # Non-terminaux (A1, S0), terminaux (a-z), ou vide (E)
        matches = re.findall(pattern, production)
        return matches

    @staticmethod
    def is_valid_production(production):
        """
        Vérifier si la production est valide (composée de non-terminaux, terminaux ou de la chaîne vide).

        :param production: Production
        :return: Booléen
        """
        # Découper la production en symboles
        symbols = CFG.split_production(production)

        # Reconstruire la production depuis les symboles pour vérifier si tout a été traité
        reconstructed = ''.join(symbols)
        if reconstructed != production:  # S'assurer qu'aucun caractère invalide n'a été ignoré
            return False

        # Vérifier chaque symbole
        return all(
            c.islower() or CFG.is_valid_non_terminal(c) or c == 'E'
            for c in symbols
        )

    def chomsky(self):
        """
        Convertir le CFG(grammaire algébrique) en forme normale de Chomsky.
        """
        # Étape 1 : Extraire les terminaux dans des productions séparées
        self.extraire_terminaux_regles()
        # self.display()

        # Étape 2 : Éliminer les productions de non-terminaux de longueur supérieure à 2
        self.eliminer_long_regles()
        # self.display()

        # Étape 3 : Éliminer les productions epsilon
        self.eliminer_epsilon_regles()
        # self.display()

        # # Étape 4 : Éliminer les productions unitaires
        self.eliminer_unit_regles()
        # self.display()

        # Étape 5 : Nettoyer les non-terminaux inutilisés
        self.supprimer_unused_non_terminal()
        # self.display()

    def greibach(self):
        """
        Convertir le CFG en forme normale de Greibach.
        """
        # Étape 1 : Éliminer la récursion à gauche
        self.eliminer_left_recursion()

        # Étape 2 : Éliminer les productions unitaires et epsilon
        self.eliminer_epsilon_regles()
        self.eliminer_unit_regles()

        # Étape 3 : Assurer que toutes les productions commencent par un terminal
        self.assurer_terminal_premier()

        # Étape 4 : Nettoyer les non-terminaux inutilisés
        self.supprimer_unused_non_terminal()

    def eliminer_epsilon_regles(self):
        """
        Éliminer les productions epsilon (règles nullables) tout en gardant certaines règles spécifiées comme S0->E.
        """
        # Trouver tous les non-terminaux qui peuvent générer la chaîne vide
        nullable = {nt for nt, productions in self.productions.items() if 'E' in productions}

        while True:
            new_nullable = nullable.copy()
            for nt, productions in self.productions.items():
                for prod in productions:
                    symbols = CFG.split_production(prod)
                    if all(symbol in nullable for symbol in symbols):  # Si la partie droite est entièrement nullable
                        new_nullable.add(nt)
            if new_nullable == nullable:
                break
            nullable = new_nullable

        # Mettre à jour les règles, supprimer les productions epsilon et ajouter toutes les combinaisons possibles non-nulles
        for nt in list(self.productions.keys()):
            new_productions = set()
            for prod in self.productions[nt]:
                if prod == 'E' and nt == self.axiome:
                    new_productions.add('E')  # Conserver S0 -> E si S0 est l'axiome
                    continue
                if prod == 'E':
                    continue  # Supprimer les autres chaînes vides

                symbols = CFG.split_production(prod)
                options = [
                    [symbol, ''] if symbol in nullable else [symbol]
                    for symbol in symbols
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
            # Identifier les productions unitaires
            unit_productions = [p for p in self.productions[nt] 
                                if len(CFG.split_production(p)) == 1 and p in self.non_terminals]

            # Tant qu'il existe des productions unitaires
            while unit_productions:
                unit = unit_productions.pop()

                # Supprimer la règle unitaire
                self.productions[nt].remove(unit)

                # Ajouter les règles de production du non-terminal cible, sans doublons
                for prod in self.productions[unit]:
                    if prod not in self.productions[nt]:
                        self.productions[nt].append(prod)
                        if len(CFG.split_production(prod)) == 1 and prod in self.non_terminals:
                            unit_productions.append(prod)

    def eliminer_long_regles(self):
        """
        Éliminer les productions dont la partie droite a une longueur supérieure à 2.
        """
        new_rules = {}

        for nt in list(self.productions.keys()):
            new_productions = []
            for prod in self.productions[nt]:
                # Découper la production en une liste de symboles
                symbols = CFG.split_production(prod)

                # Tant que la production contient plus de 2 symboles
                while len(symbols) > 2:
                    # Générer un nouveau non-terminal
                    new_nt = self.generer_new_non_terminal()
                    self.non_terminals.add(new_nt)

                    # Créer une règle pour les 2 premiers symboles
                    new_rules[new_nt] = [''.join(symbols[:2])]

                    # Réduire la production à partir du nouveau non-terminal
                    symbols = [new_nt] + symbols[2:]

                # Ajouter la production réduite
                new_productions.append(''.join(symbols))

            # Mettre à jour les productions pour le non-terminal actuel
            self.productions[nt] = new_productions

        # Ajouter les nouvelles règles générées
        self.productions.update(new_rules)

    def extraire_terminaux_regles(self):
        """
        Extraire les terminaux dans des productions séparées.
        """
        mapping = {}  # Associe chaque terminal à un nouveau non-terminal
        for nt in list(self.productions.keys()):
            new_productions = []
            for prod in self.productions[nt]:
                # Découper la production en une liste de symboles
                symbols = CFG.split_production(prod)

                # Si la production ne contient que des non-terminaux ou est de longueur 1, ne pas la modifier
                if len(symbols) == 1 or all(CFG.is_valid_non_terminal(c) for c in symbols):
                    new_productions.append(prod)
                else:
                    new_prod = []
                    for c in symbols:
                        if c.islower():  # Si c'est un terminal
                            if c not in mapping:
                                # Générer un nouveau non-terminal pour le terminal
                                new_nt = self.generer_new_non_terminal()
                                self.non_terminals.add(new_nt)
                                self.productions[new_nt] = [c]
                                mapping[c] = new_nt
                            new_prod.append(mapping[c])  # Remplacer le terminal par le nouveau non-terminal
                        else:
                            new_prod.append(c)  # Conserver les non-terminaux
                    new_productions.append(''.join(new_prod))  # Reconstruire la production
            self.productions[nt] = new_productions

    def generer_new_non_terminal(self):
        """
        Générer un nouveau non-terminal.
        """
        for number in range(0, 10):
            for letter in string.ascii_uppercase:
                if letter != 'E':
                    new_nt = f"{letter}{number}"
                    if new_nt not in self.non_terminals:
                        self.non_terminals.add(new_nt)
                        return new_nt

    def eliminer_left_recursion(self):
        """
        Éliminer la récursion directe et indirecte à gauche.
        """
        non_terminals = list(self.non_terminals)
        for i in range(len(non_terminals)):
            nt_i = non_terminals[i]

            # Remplacer la récursion indirecte à gauche
            for j in range(i):
                nt_j = non_terminals[j]
                updated_productions = []
                for prod in self.productions[nt_i]:
                    # Découper la production en symboles
                    symbols = CFG.split_production(prod)
                    if symbols[0] == nt_j:  # Si le premier symbole est nt_j
                        for beta in self.productions[nt_j]:
                            updated_productions.append(beta + ''.join(symbols[1:]))
                    else:
                        updated_productions.append(prod)
                self.productions[nt_i] = updated_productions

            # Éliminer la récursion directe à gauche
            alpha_productions = []
            beta_productions = []
            for prod in self.productions[nt_i]:
                # Découper la production en symboles
                symbols = CFG.split_production(prod)
                if symbols[0] == nt_i:  # Si le premier symbole est nt_i
                    alpha_productions.append(''.join(symbols[1:]))
                else:
                    beta_productions.append(prod)

            if alpha_productions:
                # Générer un nouveau non-terminal
                new_nt = self.generer_new_non_terminal()
                self.non_terminals.add(new_nt)
                # Alpha productions : alpha + nouveau non-terminal
                self.productions[new_nt] = [alpha + new_nt for alpha in alpha_productions] + ['E']
                # Beta productions : beta + nouveau non-terminal
                self.productions[nt_i] = [beta + new_nt for beta in beta_productions]

    def assurer_terminal_premier(self):
        """
        Assurer que toutes les productions commencent par un terminal.
        
        :raises KeyError: Si un non-terminal référencé dans une production n'a pas de règles définies.
        """
        for nt in list(self.productions.keys()):
            updated_productions = set()  # Ensemble pour stocker les nouvelles productions mises à jour
            for prod in self.productions[nt]:
                symbols = CFG.split_production(prod)  # Découper la production en symboles
                if symbols[0] == 'E':  # Ignorer la chaîne vide sauf si c'est pour l'axiome
                    if nt == self.axiome:
                        updated_productions.add('E')
                    continue

                if symbols[0].islower():  # Si la production commence par un terminal, elle est déjà valide
                    updated_productions.add(prod)
                else:  # La production commence par un non-terminal
                    prefix = symbols[0]
                    suffix = ''.join(symbols[1:])
                    if prefix not in self.productions:
                        raise KeyError(f"Le non-terminal '{prefix}' n'a pas de production définie.")
                    for replacement in self.productions[prefix]:
                        replacement_symbols = CFG.split_production(replacement)
                        if replacement_symbols[0].islower():
                            updated_productions.add(replacement + suffix)
                        else:
                            # Développer récursivement jusqu'à obtenir un préfixe terminal
                            for final_prod in self.developpe_production(replacement + suffix):
                                updated_productions.add(final_prod)
            self.productions[nt] = list(updated_productions)

    def developpe_production(self, prod, cache=None):
        """
        Développer récursivement une production pour garantir qu'elle commence par un terminal.
        
        :param prod: La production à développer.
        :param cache: Dictionnaire optionnel pour mémoriser les résultats des développements déjà effectués.
        :return: Liste des productions qui commencent par un terminal.
        :raises KeyError: Si un non-terminal référencé dans une production n'a pas de règles définies.
        """
        if cache is None:
            cache = {}
        if prod in cache:  # Vérifier si le résultat est déjà en cache
            return cache[prod]

        if prod == 'E':  # Retourner directement la chaîne vide si elle est rencontrée
            return ['E']

        symbols = CFG.split_production(prod)  # Découper la production en symboles
        if symbols[0].islower():  # Si le premier symbole est un terminal, la production est valide
            return [prod]

        results = []
        prefix = symbols[0]  # Premier symbole de la production
        suffix = ''.join(symbols[1:])  # Reste de la production
        if prefix not in self.productions:
            raise KeyError(f"Le non-terminal '{prefix}' n'a pas de production définie.")

        # Parcourir les remplacements possibles pour le préfixe (non-terminal)
        for replacement in self.productions[prefix]:
            replacement_symbols = CFG.split_production(replacement)
            if replacement_symbols[0] == 'E':  # Si le remplacement est la chaîne vide
                if suffix:  # Continuer avec le suffixe s'il existe
                    results.extend(self.developpe_production(suffix, cache))
            else:  # Ajouter le remplacement et continuer avec le suffixe
                results.extend(self.developpe_production(replacement + suffix, cache))

        cache[prod] = results  # Stocker les résultats dans le cache pour éviter les calculs redondants
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
                for symbol in self.split_production(prod):  
                    if symbol in self.non_terminals and symbol not in used:
                        used.add(symbol)
                        stack.append(symbol)

        # Supprimer les non-terminaux inutilisés
        self.non_terminals = used
        self.productions = {nt: prods for nt, prods in self.productions.items() if nt in used}
