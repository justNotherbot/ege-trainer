import random
from ipaddress import ip_network
import common


SUB_TYPE_CHAR = "E"  # Used for generating tokens
ERR_EXPR_NOT_FOUND = 1
ERR_EXPR_FILE_CORRUPT = 2


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

    def get_eval_str(self, op1_name, op2_name):
        s_eval = op1_name + " " + self.str_rep + " " + op2_name + " " + self.misc_str
        return s_eval
    
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

    def get_eval_str(self):
        return self.operator.get_eval_str(self.op1_name, self.op2_name)
    
    def get_str(self):
        return self.operator.get_str(self.op1, self.op2, self.op1_name, self.op2_name)


class ExpressionGenerator:

    def __init__(self, f_path, s_char):
        self.space_char = s_char
        self.lang_data_path = f_path
        self.words = []
        self.operands = {"num": Operand("C"), "min": Operand("E"), "max": Operand("E")}
        # Some operands cannot be used in one operation. 
        # operand_restr dictionary defines what can be used with what.
        self.operand_restr = {}
        self.operators = []
        self.line_parse = 0
        self.err_code = 0

        self.load_file()

    def get_random_expression(self):
        op1_avail, op2_avail = [], []
        while len(op1_avail) * len(op2_avail) == 0:
            operator = random.choice(self.operators)
            op1_avail = self.get_operands_by_type(operator.op1_types)
            op1 = random.choice(op1_avail)
            op2_avail = self.get_operands_by_type(operator.op2_types, self.operand_restr[op1])

        # DEBUG
        # print(op2_avail, self.operand_restr[op1], operator.op2_types)
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
        f = None
        try:
            f = open(self.lang_data_path, "r", encoding='utf-8')
        except FileNotFoundError:
            self.err_code = ERR_EXPR_NOT_FOUND
            return
        f_lines = f.readlines()

        if self.read_words_from_file(f_lines):
            self.err_code = ERR_EXPR_FILE_CORRUPT
            f.close()
            return

        if self.read_operands_from_file(f_lines):
            self.err_code = ERR_EXPR_FILE_CORRUPT
            f.close()
            return
        
        if self.read_operators_from_file(f_lines):
            self.err_code = ERR_EXPR_FILE_CORRUPT
            f.close()
            return
        print(self.words)
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
            if len(curr_words) == 3:
                w_i = int(curr_words[1]) - 1
                tmp = Operand(curr_words[-1], self.words[w_i])
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


def get_task_text(ip_str, mask_str, misc_text):
    ip_s = f"Сеть задана адресом {ip_str} и маской {mask_str}."

    return common.COMMON_TEXT + " " + ip_s + " " + misc_text


def get_ip_statistics(ip):
    n_zero_curr = ip.count("0")
    n_zero_right_curr = ip[16:].count("0")
    n_one_curr = ip.count("1")
    n_one_right_curr = ip[16:].count("1")

    return n_zero_curr, n_zero_right_curr, n_one_curr, n_one_right_curr


def get_n_ips_by_condition(ip_str, n_ip_bits, expr):
    n = 0
    net = ip_network(ip_str + "/" + str(32 - n_ip_bits))
    for ip in net:
        print(ip)
        curr_bits = f"{ip:b}"
        n_zeroes_total, n_zeroes_right, n_ones_total, n_ones_right = get_ip_statistics(curr_bits)
        n_zeroes_left = n_zeroes_total - n_zeroes_right
        n_ones_left = n_ones_total - n_ones_right
        e_str = expr.get_eval_str()
        if eval(e_str):
            n += 1
    return n


def get_ip_and_mask():
    n_ip_bits = random.randint(common.N_MIN_IP_BITS, 15)
    mask_bytes = "1" * (16 - n_ip_bits) + "0" * n_ip_bits
    mask_bytes = [255, 255, int(mask_bytes[:8], 2), int(mask_bytes[8:], 2)]
    ip_bytes = []
    common.randomize_list(ip_bytes, 0, 254, 2, common.MIN_IP_NUM_DEV)
    offset_3 = common.clamp(16 - n_ip_bits, 1, 8)
    ip_byte_3 = random.randint(0, (1 << offset_3) - 1) << (8 - offset_3)
    offset_4 = common.clamp(8 - n_ip_bits, 0, 8)
    ip_byte_4 = random.randint(0, (1 << offset_4) - 1) << (8 - offset_4)
    ip_bytes += [ip_byte_3, ip_byte_4]
    ip_str = common.list2string(ip_bytes)
    mask_str = common.list2string(mask_bytes)

    return ip_str, mask_str, n_ip_bits


def generate_type_e(e_generator, tokens):
    r_ex = e_generator.get_random_expression()
    
    ip_str, mask_str, n_ip_bits = get_ip_and_mask()
    token = SUB_TYPE_CHAR + ip_str + "_" + mask_str
    while token in tokens:
        ip_str, mask_str, n_ip_bits = get_ip_and_mask()
        token = SUB_TYPE_CHAR + ip_str + "_" + mask_str
    tokens[token] = 1

    # Obtain the right answer
    ans = -1
    misc_txt = ""
    if r_ex.op2.type in ["E", "C"]:
        # obtain ranges of variables
        net = ip_network(ip_str+"/"+str(32 - n_ip_bits))
        net_bin_str = f"{net[0]:b}"
        n_zero_curr, n_zero_right_curr, n_one_curr, n_one_right_curr = get_ip_statistics(net_bin_str)
        ranges = {"n_zeroes_total": [n_zero_curr - n_ip_bits, n_zero_curr], 
                  "n_ones_total": [n_one_curr, n_one_curr + n_ip_bits],
                  "n_zeroes_right": [n_zero_right_curr - n_ip_bits, n_zero_right_curr],
                  "n_ones_right": [n_one_right_curr, n_one_right_curr + n_ip_bits]}
        if r_ex.op2.type == "E":  # type "E" means extreme value i.e. min/max
            i_map = {"min": 0, "max": 1}
            n_map = {"min": "минимальное", "max": "максимальное"}
            tgt_word = r_ex.op1.get_str(r_ex.op1_name, r_ex.operator.op1_form)
            misc_txt = "Определите " + n_map[r_ex.op2_name] + " " + tgt_word + "."
            ans = ranges[r_ex.op1_name][i_map[r_ex.op2_name]]
        else:
            l = common.clamp(ranges[r_ex.op1_name][0], 2, None)
            r = common.clamp(ranges[r_ex.op1_name][1], l, None)
            r_ex.op2_name = str(random.randint(l, r))
    
    if ans == -1:
        misc_txt = "Сколько в этой сети IP-адресов, для которых " + r_ex.get_str() + "?"
        ans = get_n_ips_by_condition(ip_str, n_ip_bits, r_ex)

    task_text = get_task_text(ip_str, mask_str, misc_txt)

    return common.Task(task_text, str(ans), SUB_TYPE_CHAR)


if __name__ == "__main__":
    test_gen = ExpressionGenerator("expr_data.txt", "$")
    common.test_func(generate_type_e, test_gen, {})
