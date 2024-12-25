class CFG:
    def __init__(self, axiome='S'):
        """
        初始化一个CFG格式，包含非终结符集、终结符集、起始符号和产生式规则。

        :param axiome: 起始符号，默认为'S'
        """
        self.non_terminals = set()  # 非终结符集合
        self.terminals = set()  # 终结符集合
        self.productions = {}  # 产生式规则，格式为{非终结符: [产生式列表]}
        self.axiome = axiome  # 起始符号
        self.new_non_terminal_counter = 0  # 用于生成新非终结符

    def add_production(self, non_terminal, production_list):
        """
        添加产生式规则。

        :param non_terminal: 非终结符
        :param production_list: 产生式列表（list of str）
        """
        if non_terminal not in self.non_terminals:
            self.non_terminals.add(non_terminal)

        if non_terminal in self.productions:
            self.productions[non_terminal].extend(production_list)
        else:
            self.productions[non_terminal] = production_list

        # 更新终结符和非终结符集
        for production in production_list:
            for char in production:
                if char.islower():  # 小写字母是终结符
                    self.terminals.add(char)
                elif char.isupper() and char != 'E':  # 大写字母（非E）是非终结符
                    self.non_terminals.add(char)

    def add_production_with_validation(self, non_terminal, production_list):
        if not CFG.is_valid_non_terminal(non_terminal):
            raise ValueError(f"'{non_terminal}' 不是一个有效的非终结符！")

        for production in production_list:
            if not CFG.is_valid_production(production):
                raise ValueError(f"'{production}' 不是一个有效的产生式！")

        self.add_production(non_terminal, production_list)


    def display(self):
        """
        显示CFG的非终结符集、终结符集、起始符号和产生式规则。
        """
        print("非终结符集:", self.non_terminals)
        print("终结符集:", self.terminals)
        print("起始符号:", self.axiome)
        print("产生式规则:")
        for non_terminal, productions in self.productions.items():
            print(f"  {non_terminal} -> {' | '.join(productions)}")

    @staticmethod
    def is_valid_non_terminal(symbol):
        """
        检查符号是否是有效的非终结符。

        :param symbol: 符号
        :return: 布尔值
        """
        return len(symbol) == 1 and symbol.isupper() and symbol != 'E'

    @staticmethod
    def is_valid_terminal(symbol):
        """
        检查符号是否是有效的终结符。

        :param symbol: 符号
        :return: 布尔值
        """
        return len(symbol) == 1 and symbol.islower()

    @staticmethod
    def is_valid_production(production):
        """
        检查产生式是否有效（由非终结符、终结符或空串组成）。

        :param production: 产生式
        :return: 布尔值
        """
        return all(c.islower() or (c.isupper() and c != 'E') or c == 'E' for c in production)

    def to_chomsky_normal_form(self):
        """
        将CFG转换为Chomsky范式。
        """
        # Step 1: 消除空产生式
        self._eliminate_epsilon_rules()

        # Step 2: 消除单一产生式
        self._eliminate_unit_rules()

        # Step 3: 消除右部长度大于2的产生式
        self._eliminate_long_rules()

        # Step 4: 将终结符单独提取为产生式
        self._eliminate_mixed_rules()

    def to_greibach_normal_form(self):
        """
        将CFG转换为Greibach范式。
        """
        # Step 1: 消除单一产生式和空产生式
        self._eliminate_epsilon_rules()
        self._eliminate_unit_rules()

        # Step 2: 消除左递归
        self._eliminate_left_recursion()

        # Step 3: 确保所有产生式以终结符开头
        self._ensure_terminal_prefix()

        # Step 4: 清理未使用的非终结符
        self._remove_unused_non_terminals()

    def _eliminate_epsilon_rules(self):
        """
        消除空产生式（nullable rules）。
        """
        # 找出所有可以生成空串的非终结符
        nullable = {nt for nt, productions in self.productions.items() if 'E' in productions}

        while True:
            new_nullable = nullable.copy()
            for nt, productions in self.productions.items():
                for prod in productions:
                    if all(symbol in nullable for symbol in prod):  # 如果产生式右部全是 nullable
                        new_nullable.add(nt)
            if new_nullable == nullable:
                break
            nullable = new_nullable

        # 更新规则，移除空产生式并添加所有可能的非空组合
        for nt in list(self.productions.keys()):
            new_productions = set()
            for prod in self.productions[nt]:
                if prod == 'E':
                    continue  # 移除空串
                options = [
                    [symbol, ''] if symbol in nullable else [symbol]
                    for symbol in prod
                ]
                from itertools import product
                for option in product(*options):
                    new_prod = ''.join(option)
                    if new_prod:  # 只添加非空组合
                        new_productions.add(new_prod)
            self.productions[nt] = list(new_productions)

    def _eliminate_unit_rules(self):
        """
        消除单一产生式（unit rules）。
        """
        for nt in list(self.productions.keys()):
            unit_productions = [p for p in self.productions[nt] if len(p) == 1 and p in self.non_terminals]
            while unit_productions:
                unit = unit_productions.pop()
                self.productions[nt].remove(unit)
                self.productions[nt].extend(self.productions[unit])

    def _eliminate_long_rules(self):
        """
        消除右部长度大于2的产生式。
        """
        new_rules = {}
        for nt in list(self.productions.keys()):
            new_productions = []
            for prod in self.productions[nt]:
                while len(prod) > 2:
                    new_nt = self._generate_new_non_terminal()
                    self.non_terminals.add(new_nt)
                    new_rules[new_nt] = [prod[:2]]
                    prod = new_nt + prod[2:]
                new_productions.append(prod)
            self.productions[nt] = new_productions
        self.productions.update(new_rules)

    def _eliminate_mixed_rules(self):
        """
        将终结符单独提取为产生式。
        """
        mapping = {}
        for nt in list(self.productions.keys()):
            new_productions = []
            for prod in self.productions[nt]:
                if len(prod) == 1 or all(c.isupper() for c in prod):
                    new_productions.append(prod)
                else:
                    new_prod = ''
                    for c in prod:
                        if c.islower():
                            if c not in mapping:
                                new_nt = self._generate_new_non_terminal()
                                self.non_terminals.add(new_nt)
                                self.productions[new_nt] = [c]
                                mapping[c] = new_nt
                            new_prod += mapping[c]
                        else:
                            new_prod += c
                    new_productions.append(new_prod)
            self.productions[nt] = new_productions

    def _generate_new_non_terminal(self):
        """
        生成新的非终结符。
        """
        import string
        # 尝试从A到Z生成
        for c in string.ascii_uppercase:
            if c not in self.non_terminals and c != 'E':
                return c

        # 如果A-Z已用尽，使用字母+数字组合
        while True:
            new_nt = f"X{self.new_non_terminal_counter}"
            self.new_non_terminal_counter += 1
            if new_nt not in self.non_terminals:
                return new_nt
            
    def _eliminate_left_recursion(self):
        """
        消除直接和间接左递归。
        """
        non_terminals = list(self.non_terminals)
        for i in range(len(non_terminals)):
            nt_i = non_terminals[i]
            new_productions = []

            # 替换间接左递归
            for j in range(i):
                nt_j = non_terminals[j]
                updated_productions = []
                for prod in self.productions[nt_i]:
                    if prod.startswith(nt_j):
                        for beta in self.productions[nt_j]:
                            updated_productions.append(beta + prod[1:])
                    else:
                        updated_productions.append(prod)
                self.productions[nt_i] = updated_productions

            # 消除直接左递归
            alpha_productions = []
            beta_productions = []
            for prod in self.productions[nt_i]:
                if prod.startswith(nt_i):
                    alpha_productions.append(prod[1:])
                else:
                    beta_productions.append(prod)

            if alpha_productions:
                new_nt = self._generate_new_non_terminal()
                self.non_terminals.add(new_nt)
                self.productions[new_nt] = [alpha + new_nt for alpha in alpha_productions] + ['E']
                self.productions[nt_i] = [beta + new_nt for beta in beta_productions]

    def _ensure_terminal_prefix(self):
        """
        确保每个产生式都以终结符开头，同时避免冗余规则。
        """
        for nt in list(self.productions.keys()):
            updated_productions = []
            for prod in self.productions[nt]:
                if prod[0].islower():  # 已经以终结符开头
                    updated_productions.append(prod)
                else:  # 需要处理以非终结符开头的规则
                    prefix = prod[0]
                    suffix = prod[1:]
                    for replacement in self.productions[prefix]:
                        # 如果replacement已经以终结符开头，直接组合
                        if replacement[0].islower():
                            candidate = replacement + suffix
                            if candidate not in updated_productions:
                                updated_productions.append(candidate)
                        else:
                            # 避免生成多余的中间非终结符
                            for final_prod in self._expand_to_terminal_prefix(replacement + suffix):
                                if final_prod not in updated_productions:
                                    updated_productions.append(final_prod)
            self.productions[nt] = list(set(updated_productions))  # 去重

    def _expand_to_terminal_prefix(self, prod):
        """
        展开产生式直到以终结符开头。

        :param prod: 输入的产生式
        :return: 以终结符开头的产生式列表
        """
        if prod[0].islower():
            return [prod]

        results = []
        prefix = prod[0]
        suffix = prod[1:]
        for replacement in self.productions[prefix]:
            results.extend(self._expand_to_terminal_prefix(replacement + suffix))
        return results

    def _remove_unused_non_terminals(self):
        """
        移除未使用的非终结符和多余规则。
        """
        used = {self.axiome}
        stack = [self.axiome]

        while stack:
            nt = stack.pop()
            for prod in self.productions.get(nt, []):
                for symbol in prod:
                    if symbol in self.non_terminals and symbol not in used:
                        used.add(symbol)
                        stack.append(symbol)

        # 移除未使用的非终结符
        self.non_terminals = used
        self.productions = {nt: prods for nt, prods in self.productions.items() if nt in used}


