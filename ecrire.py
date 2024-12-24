import cfg

def write_to_file(cfg, file_path):
    """
    将 CFG 写入到文件中。

    :param cfg: 要写入的 CFG 对象
    :param file_path: 文件路径
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for non_terminal, productions in cfg.productions.items():
                file.write(f"{non_terminal} -> {' | '.join(productions)}\n")
        print(f"CFG 已成功写入到 {file_path}")
    except Exception as e:
        print(f"写入文件时发生错误: {e}")
        
