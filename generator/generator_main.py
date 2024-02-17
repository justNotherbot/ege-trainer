import type_b
import type_d
import type_e
import common
import os


def parse_str(s):
    tp, n = "", 0

    if len(s) >= 2:
        tp = s[0]
        n = int(s[1:]) if s[1:].isnumeric() else 0

    return tp, n


tokens = {}
tasks = {"B": type_b.generate_type_b,
         "D": type_d.generate_type_d,
         "E": type_e.generate_type_e}

s = input()
tgt = s.strip().split()

expr_gen = None

if "E" in s:
    curr_dir = os.path.dirname(os.path.realpath(__file__))  # Directory where this .py file is located
    tgt_dir = os.path.join(curr_dir, "expr_data.txt")
    expr_gen = type_e.ExpressionGenerator(tgt_dir, "$")

    if expr_gen.err_code:
        exit(expr_gen.err_code)


for i in tgt:
    tp, n = parse_str(i)
    if tp in tasks:
        for j in range(n):
            if tp == "E":
                print(tasks[tp](expr_gen, tokens), end=common.TASK_SEP)
            else:
                print(tasks[tp](tokens), end=common.TASK_SEP)
