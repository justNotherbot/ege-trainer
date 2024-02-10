import common
import random


class Word:

    def __init__(self, i_p="", r_p="", d_p="", v_p="", t_p="", p_p=""):
        self.forms = {"i_p": i_p, "r_p": r_p, "d_p": d_p, 
                      "v_p": v_p, "t_p": t_p, "p_p": p_p}

    def __repr__(self):
        return self.get_debug_str()

    def __str__(self):
        return self.get_debug_str()
    
    def get_debug_str(self):
        s = ""
        for i in self.forms.keys():
            s = s + f"{i}: {self.forms[i]} "
        return f"Word<{s[:-1]}>"
        
    def derive(self, w_list, s_add=""):
        if len(w_list) == 0:
            return
        
        for i in w_list[0].forms.keys():
            s = ""
            for j in w_list:
                s += j.forms[i] + " "
            s += s_add

            self.forms[i] = s


class Operand:

    def __init__(self, tp, word=None):
        self.type = tp
        self.word_repr = word

    def get_str(self, var_name, form):
        if self.word_repr == None:
            return var_name
        return self.word_repr.forms[form]
    

class Operator:

    def __init__(self, f1, f2, op1_types, op2_types, s_rep, w_rep, misc=""):
        self.op1_form = f1
        self.op2_form = f2
        self.op1_types = op1_types
        self.op2_types = op2_types
        self.str_rep = s_rep
        self.word_repr = w_rep
        self.misc_str = misc

    def evaluate(self, op1_name, op2_name):
        s_eval = op1_name + " " + self.str_rep + " " + op2_name + " " + self.misc_str
        return eval(s_eval)
    
    def get_str(self, op1, op2, op1_name, op2_name):
        return op1.get_str(op1_name, self.op1_form) + " " + self.word_repr + " "\
              + op2.get_str(op2_name, self.op2_form)


class Expression:

    def __init__(self, operator, op1, op2, op1_name, op2_name):
        self.operator = operator
        self.op1 = op1
        self.op2 = op2
        self.op1_name = op1_name
        self.op2_name = op2_name

    def evaluate(self):
        return self.operator.evaluate(self.op1_name, self.op2_name)
    
    def get_str(self):
        return self.operator.get_str(self.op1, self.op2, self.op1_name, self.op2_name)


class ExpressionGenerator:

    def __init__(self, f_path, s_char):
        self.space_char = s_char
        self.lang_data_path = f_path
        self.words = []
        self.operands = {"num": Operand("C")}
        # Some operands cannot be used in one operation. 
        # operand_restr dictionary defines what can be used with what.
        self.operand_restr = {}
        self.operators = []
        self.line_parse = 0

        self.load_file()

    def get_random_expression(self):
        operator = random.choice(self.operators)
        op1_avail = self.get_operands_by_type(operator.op1_types)
        op1 = random.choice(op1_avail)
        op2_avail = self.get_operands_by_type(operator.op2_types, self.operand_restr[op1])
        print(op2_avail, self.operand_restr[op1], operator.op2_types)
        op2 = random.choice(op2_avail)

        return Expression(operator, self.operands[op1], self.operands[op2], op1, op2)

    def get_operands_by_type(self, types, op_allow=[]):
        out = []
        for i in self.operands.keys():
            in_allow = True
            if len(op_allow):
                in_allow = i in op_allow
            if self.operands[i].type in types and in_allow:
                out.append(i)

        return out

    def load_file(self):
        f = open(self.lang_data_path, "r")
        f_lines = f.readlines()
        err = self.read_words_from_file(f_lines)
        print(err)
        err = self.read_operands_from_file(f_lines)
        print(err)
        err = self.read_operators_from_file(f_lines)
        print(err)
        f.close()

    def read_words_from_file(self, f_lines):
        read_word = False
        word_inst = []  # Instances of the word being read
        for i in range(len(f_lines)):
            curr_line = f_lines[i].strip()

            if curr_line == "e_w":                
                self.line_parse = i + 1
                break
            if curr_line == "" or curr_line[0] == "#":
                continue

            curr_words = curr_line.split()
            common.list_replace(curr_words, "X", "")
            common.replace_in_list_str(curr_words, self.space_char, " ")
            if read_word:
                if len(word_inst) == 6:
                    self.words.append(Word(word_inst[0], word_inst[1], word_inst[2],
                                           word_inst[3], word_inst[4], word_inst[5]))
                    read_word = False
                    word_inst = []
                elif len(word_inst) < 6 and len(curr_words) == 1:
                    word_inst.append(curr_words[0])
                else:
                    return 1
            
            if len(curr_words) >= 1 and curr_words[0] in ["i", "d"]:
                if curr_words[0] == "i":
                    read_word = True
                elif curr_words[0] == "d" and len(curr_words) == 3:
                    i_d = map(int, curr_words[1].split())
                    s_add = curr_words[-1]
                    tmp = Word()
                    tmp.derive([self.words[j-1] for j in i_d], s_add)
                    self.words.append(tmp)
                else:
                    return 2

        return 0
    
    def read_operands_from_file(self, f_lines):
        for i in range(self.line_parse, len(f_lines)):
            curr_line = f_lines[i].strip()

            if curr_line == "e_od":
                self.line_parse = i + 1
                break
            if curr_line == "" or curr_line[0] == "#":
                continue

            curr_words = curr_line.split()
            common.list_replace(curr_words, "X", "")
            common.replace_in_list_str(curr_words, self.space_char, " ")
            if len(curr_words) == 2:
                w_i = int(curr_words[-1]) - 1
                tmp = Operand("V", self.words[w_i])
                self.operands[curr_words[0]] = tmp
            elif len(curr_words) >= 3 and curr_words[0] == "r":
                self.operand_restr[curr_words[1]] = curr_words[2:]
            else:
                return 1
        return 0
    
    def read_operators_from_file(self, f_lines):
        for i in range(self.line_parse, len(f_lines)):
            curr_line = f_lines[i].strip()

            if curr_line == "e_or":
                self.line_parse = i + 1
                break
            if curr_line == "" or curr_line[0] == "#":
                continue

            curr_words = curr_line.split()
            common.list_replace(curr_words, "X", "")
            common.replace_in_list_str(curr_words, self.space_char, " ")

            if len(curr_words) == 7:
                op1_types = curr_words[2].split()
                op2_types = curr_words[3].split()
                tmp = Operator(curr_words[0], curr_words[1], op1_types, op2_types, 
                               curr_words[4], curr_words[5], curr_words[6])
                self.operators.append(tmp)
            else:
                return 1

        return 0


test_gen = ExpressionGenerator("expr_data.txt", "$")
r_ex = test_gen.get_random_expression()

print(r_ex.get_str(), r_ex.op1_name, r_ex.op2_name)
