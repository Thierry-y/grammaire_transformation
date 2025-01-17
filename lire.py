import cfg 

def read_cfg_rules(file_path):
    """
    Lire les règles CFG dans le fichier donné et retourner un objet CFG.
    """
    rule = cfg.CFG()  # Créer un objet CFG

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip().replace(" ", "")
                if not line or '->' not in line:
                    continue

                non_terminal, productions = line.split('->')
                production_list = productions.split('|')
                rule.add_production_avec_validation(non_terminal, production_list) # Utiliser l'objet CFG pour ajouter des règles

    except FileNotFoundError:
        print(f"Fichier introuvable : {file_path}")
        return None # Retourne None pour que l'appelant puisse gérer l'erreur
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return None

    return rule  # Retourner l'objet CFG
