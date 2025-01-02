import sys
from lire import read_cfg_rules

class CFGWordGenerator:
    def __init__(self, cfg):
        """
        Initialiser CFGWordGenerator.
        :param cfg: L'objet CFG passé en paramètre
        """
        self.cfg = cfg
        self.start_symbol = cfg.axiome

    def generate_words(self, max_length):
        """
        Générer tous les mots possibles selon la grammaire.
        :param max_length: Longueur maximale des mots générés
        :return: Liste des mots satisfaisant les conditions
        """
        results = set()

        def expand(symbols):
            """
            Développer récursivement une liste de symboles.
            :param symbols: La séquence de symboles actuelle
            """
            # Si la longueur dépasse la limite maximale, arrêter la récursion
            if len(symbols) > max_length:
                return

            # Si所有符号是终结符 ou 空串, ajouter le mot aux résultats
            if all(symbol in self.cfg.terminals or symbol == 'E' for symbol in symbols):
                # 移除E并加入结果集
                word = ''.join(symbol for symbol in symbols if symbol != 'E')
                results.add(word)
                return

            # Développer chaque non-terminal dans la séquence actuelle
            for i, symbol in enumerate(symbols):
                if symbol in self.cfg.non_terminals:  # Développer uniquement les non-terminaux
                    for production in self.cfg.productions.get(symbol, []):
                        new_symbols = symbols[:i] + list(production) + symbols[i + 1:]
                        expand(new_symbols)
                    break  # Développer un seul非终结符 pour éviter les combinaisons redondantes

        # Commencer le développement à partir du symbole de départ
        expand([self.start_symbol])

        # 确保空串 (E) 优先
        sorted_results = sorted(results)
        if '' in sorted_results:  # 如果结果中包含空串
            sorted_results.remove('')  # 移除空串
            sorted_results.insert(0, '')  # 将空串放在第一个
        return sorted_results

if __name__ == "__main__":
    # Vérifier les arguments de la ligne de commande
    if len(sys.argv) != 3:
        print("Utilisation : python3 generer.py <file_path> <max_length>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        max_length = int(sys.argv[2])
        if max_length <= 0:
            raise ValueError
    except ValueError:
        print("Erreur : <max_length> doit être un entier positif")
        sys.exit(1)

    # Lire les règles CFG
    cfg_rules = read_cfg_rules(file_path)
    if cfg_rules is None:
        print("Échec de la lecture des règles CFG, veuillez vérifier le contenu du fichier.")
        sys.exit(1)

    # Générer les mots
    generator = CFGWordGenerator(cfg_rules)
    words = generator.generate_words(max_length)

    # Afficher les mots générés
    print(f"Mots générés (longueur maximale {max_length}) :")
    for word in words:
        print(word if word != '' else 'E')  # 用'E'显示空串
