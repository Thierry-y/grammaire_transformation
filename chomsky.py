import re
import string

def normalize_grammar_rule(rule):
    """规范化文法规则，去除多余空格，并确保格式一致。"""
    rule = re.sub(r"\s*->\s*", " -> ", rule)  # 确保 "->" 两边有且只有一个空格
    rule = re.sub(r"\s*\|\s*", " | ", rule)   # 确保 "|" 两边有且只有一个空格
    rule = re.sub(r"\s+", " ", rule).strip()  # 去除多余空格并修剪首尾
    return rule

def cfg_to_cnf(grammar_rules):
    """将 CFG 规则转换为 CNF。使用 E 表示空串。并按要求排序。"""
    # 1. 规范化文法规则
    normalized_grammar_rules = [normalize_grammar_rule(rule) for rule in grammar_rules]

    # 2. 将规则按左侧非终结符分组
    grouped_rules = {}
    for rule in normalized_grammar_rules:
        left, right = rule.split(" -> ")
        if left not in grouped_rules:
            grouped_rules[left] = []
        grouped_rules[left].extend(right.split(" | "))

    # 3. 消除 E 规则
    for left in grouped_rules:
        new_parts = []
        for part in grouped_rules[left]:
            temp_parts = [part]
            if "S" in part and left == "S": # 只对起始符号 S 进行 E 消除
                while temp_parts:
                    current_part = temp_parts.pop(0)
                    if "S" in current_part:
                        new_part = current_part.replace("S", "", 1)
                        if new_part not in new_parts and new_part != "":
                            new_parts.append(new_part)
                            temp_parts.append(new_part)
            new_parts.append(part) # 添加原始部分
        grouped_rules[left] = list(set(new_parts)) # 去重

    # 4. 转换为 CNF 形式
    cnf_rules = []
    nonterminals = set()
    terminals = set()
    available_nonterminals = list(set(string.ascii_uppercase) - {"S", "E"})
    new_nonterminal_counter = 0

    for left in grouped_rules:
        for part in grouped_rules[left]:
            symbols = part.split()
            if len(symbols) == 1:
                if symbols[0].islower():
                    if symbols[0].upper() not in nonterminals:
                        cnf_rules.append(f"{symbols[0].upper()} -> {symbols[0]}")
                        nonterminals.add(symbols[0].upper())
                    cnf_rules.append(f"{left} -> {symbols[0].upper()}")
                    terminals.add(symbols[0])
            elif len(symbols) > 1:
                current_left = left
                for i in range(len(symbols)):
                    if symbols[i].islower():
                        new_nonterminal = symbols[i].upper()
                        if new_nonterminal not in nonterminals:
                            cnf_rules.append(f"{new_nonterminal} -> {symbols[i]}")
                            nonterminals.add(new_nonterminal)
                        symbols[i] = new_nonterminal
                for i in range(len(symbols) - 1):
                    if i < len(symbols) - 2:
                        if available_nonterminals:
                            new_nonterminal = available_nonterminals.pop(0)
                        else:
                            new_nonterminal = f"A{new_nonterminal_counter}"
                            new_nonterminal_counter += 1
                        cnf_rules.append(f"{current_left} -> {symbols[i]} {new_nonterminal}")
                        current_left = new_nonterminal
                    else:
                        cnf_rules.append(f"{current_left} -> {symbols[i]} {symbols[i+1]}")

    # 5. 排序规则
    s_rules = [rule for rule in cnf_rules if rule.startswith("S ->")]
    terminal_rules = [rule for rule in cnf_rules if rule.split(" -> ")[1].islower()]
    other_rules = [rule for rule in cnf_rules if rule not in s_rules and rule not in terminal_rules]

    sorted_rules = s_rules + other_rules + terminal_rules

    return sorted_rules

# 测试用例
grammars = [
    ["S -> a S b| a b"],
    ["S->aSb|ab"],
    ["S -> a S b | E"],
    ["S->aSb|E"],
    ["S -> a S b S | E"]
]

for grammar in grammars:
    cnf_grammar = cfg_to_cnf(grammar)
    print(f"原始文法：{grammar}")
    print("转换后的 CNF 规则：")
    for rule in cnf_grammar:
        print(rule)
    print("-" * 20)
