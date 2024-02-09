class Word:

    def __init__(self, i_p, r_p, d_p, v_p, t_p, p_p):
        self.forms = {"i_p": i_p, "r_p": r_p, "d_p": d_p, 
                      "v_p": v_p, "t_p": t_p, "p_p": p_p}


class Operand:

    def __init__(self, name, word=None):
        self.var_name = name
        self.word_repr = word

    def get_str(self, form):
        if self.word_repr == None:
            return self.var_name
        return self.word_repr.forms[form]
    

class Operator:

    def __init__(self, f1, f2, s_rep, w_rep):
        self.op1_form = f1
        self.op2_form = f2
        self.str_rep = s_rep
        self.word_repr = w_rep

    def evaluate(self, op1, op2):
        s_eval = op1.var_name + " " + self.str_rep + " " + op2.var_name
        return eval(s_eval)
    
    def get_str(self, op1, op2):
        return op1.get_str(self.op1_form) + " " + self.word_repr + " "\
              + op2.get_str(self.op2_form)
