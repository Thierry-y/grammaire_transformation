import cfg

def write_to_file(cfg, file_path):
    """
    Écrire un CFG dans un fichier.

    :param cfg: L'objet CFG à écrire
    :param file_path: Chemin du fichier
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for non_terminal, productions in cfg.productions.items():
                file.write(f"{non_terminal} -> {' | '.join(productions)}\n")
        print(f"Le CFG a été écrit avec succès dans {file_path}")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'écriture du fichier : {e}")
