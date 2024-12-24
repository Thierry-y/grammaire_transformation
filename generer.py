import sys
from lire import read_cfg_rules  

class CFGWordGenerator:
    def __init__(self, cfg):
        """
        初始化 CFGWordGenerator。
        :param cfg: 传入的 CFG 对象
        """
        self.cfg = cfg
        self.start_symbol = cfg.axiome

    def generate_words(self, max_length):
        """
        根据文法生成所有可能的词。
        :param max_length: 生成的词的最大长度
        :return: 满足条件的词列表
        """
        results = set()

        def expand(symbols):
            """
            递归展开符号列表。
            :param symbols: 当前展开的符号序列
            """
            # 如果长度超出最大长度限制，停止递归
            if len(symbols) > max_length:
                return

            # 如果符号序列全是终结符，记录为结果
            if all(symbol in self.cfg.terminals for symbol in symbols):
                results.add(''.join(symbols))
                return

            # 对当前符号序列的每个非终结符展开
            for i, symbol in enumerate(symbols):
                if symbol in self.cfg.non_terminals:  # 仅对非终结符展开
                    for production in self.cfg.productions.get(symbol, []):
                        new_symbols = symbols[:i] + list(production) + symbols[i + 1:]
                        expand(new_symbols)
                    break  # 只展开一个非终结符，避免重复组合

        # 从起始符号开始展开
        expand([self.start_symbol])
        return sorted(results)

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) != 3:
        print("用法: python3 generer.py <file_path> <max_length>")
        sys.exit(1)

    file_path = sys.argv[1]
    try:
        max_length = int(sys.argv[2])
        if max_length <= 0:
            raise ValueError
    except ValueError:
        print("错误: <max_length> 必须是正整数")
        sys.exit(1)

    # 读取CFG规则
    cfg_rules = read_cfg_rules(file_path)
    if cfg_rules is None:
        print("读取CFG规则失败，请检查文件内容。")
        sys.exit(1)

    # 生成词
    generator = CFGWordGenerator(cfg_rules)
    words = generator.generate_words(max_length)

    # 打印生成的词
    print(f"生成的词（长度不超过 {max_length}）:")
    for word in words:
        print(word)
