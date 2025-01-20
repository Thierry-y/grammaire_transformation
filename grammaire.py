import lire
import ecrire

if __name__ == "__main__":
    # Peut supprimer les commentaires pour afficher plus clairement la structure de la grammaire
    file_path = "cfg.general"  
    algebre = lire.read_cfg_rules(file_path)
    # print("Grammaires algébriques:")
    # algebre.display()     
    algebre.chomsky()
    print("-" * 50)
    print("Forme normale de Chomsky:")
    # algebre.display()
    ecrire.write_to_file(algebre,"alg.chomsky")
    algebre.greibach()
    print("-" * 50)
    print("Forme normale de Greibach:")
    #algebre.display()
    ecrire.write_to_file(algebre,"alg.greibach")
    print("-" * 50)
    
    