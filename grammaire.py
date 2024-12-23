def read_cfg_rules(file_path):
    """
    读取给定文件中的CFG规则，删除空格并解析规则。

    :param file_path: 文法规则的txt文件路径
    :return: 解析后的文法规则，格式为{非终结符: [产生式列表]}
    """
    cfg_rules = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()  # 去掉行首尾的空白符
                if not line:
                    continue  # 跳过空行

                # 删除所有空格
                line = line.replace(" ", "")

                # 按照'->'分割非终结符和产生式部分
                if '->' not in line:
                    raise ValueError(f"规则格式错误: {line}")

                non_terminal, productions = line.split('->')

                # 按照'|'分割多个产生式
                production_list = productions.split('|')

                # 添加到结果字典
                if non_terminal in cfg_rules:
                    cfg_rules[non_terminal].extend(production_list)
                else:
                    cfg_rules[non_terminal] = production_list

    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
    except Exception as e:
        print(f"发生错误: {e}")

    return cfg_rules

# 示例使用
if __name__ == "__main__":
    file_path = "cfg.txt"  # 替换为你的文件路径
    cfg = read_cfg_rules(file_path)
    print(cfg)
