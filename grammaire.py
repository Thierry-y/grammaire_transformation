import lire
import ecrire

if __name__ == "__main__":
    file_path = "cfg.general"  
    algebre = lire.read_cfg_rules(file_path)
    algebre.display()
    algebre.to_chomsky_normal_form()
    print("---------------------------------")
    algebre.display()
    ecrire.write_to_file(algebre,"alg.chomsky")
    algebre.to_greibach_normal_form()
    print("---------------------------------")
    algebre.display()
    ecrire.write_to_file(algebre,"alg.greibach")
    
    