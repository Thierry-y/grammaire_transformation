# cfg_parser.py
import cfg # 导入 cfg_utils 模块

def read_cfg_rules(file_path):
    """
    读取给定文件中的CFG规则，并返回一个 CFG 对象。
    """
    rule = cfg.CFG()  # 创建 CFG 对象

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip().replace(" ", "")
                if not line or '->' not in line:
                    continue

                non_terminal, productions = line.split('->')
                production_list = productions.split('|')
                rule.add_production(non_terminal, production_list) #使用cfg对象添加规则

    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return None #返回none，方便调用者进行错误处理
    except Exception as e:
        print(f"发生错误: {e}")
        return None

    return rule  # 返回 CFG 对象