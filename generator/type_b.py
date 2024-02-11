import random
import common


SUB_TYPE_CHAR = "B"  # Used for generating tokens


class Table:

    def __init__(self, length):
        self.values = [0] * length
        self.max_val = 0

    def set_values(self, v_in):
        if len(v_in):
            self.max_val = v_in[0]
            for i in range(min(len(self.values), len(v_in))):
                if v_in[i] > self.max_val:
                    self.max_val = v_in[i]
                self.values[i] = v_in[i]
    
    def get_str(self, p_s=1):
        m_length = len(str(self.max_val))
        cell_width = m_length + (m_length + 1) % 2 + 2 * p_s

        h_line_dash = ("+" + "-" * cell_width) * len(self.values) + "+"
        h_line_blank = ("|" + " " * cell_width) * len(self.values) + "|"
        letter_line = h_line_blank

        c = 0

        for i in range(1 + cell_width//2, len(letter_line), cell_width + 1):
            letter_line = letter_line[:i] + chr(ord("A")+c % 26) + letter_line[i+1:]
            c += 1
        number_line = ""

        for i in range(len(self.values)):
            n_s = str(self.values[i])
            n_pad_offset = cell_width // 2 - len(n_s) // 2
            number_line += "|" + " " * (n_pad_offset + (len(n_s)+1) % 2) + n_s + " " * n_pad_offset
        number_line += "|"

        b_lines = (h_line_blank + "\n") * p_s
        table = h_line_dash + "\n" + b_lines + letter_line + "\n" + b_lines \
                + h_line_dash + "\n" + b_lines + number_line + "\n" + b_lines + h_line_dash
        return table


def generate_task():
    n_bits_left = random.randint(-5, -1)
    n_bits_right = random.randint(2, 4)
    tgt = random.choice([n_bits_left, n_bits_right])

    mask_3, mask_4 = 255, 0  # Octet #3 and #4
    if tgt == n_bits_left:
        mask_3 -= int("1" * -tgt, 2)
    else:
        mask_4 += int("1" * tgt + "0" * (8 - tgt), 2)

    ip_bytes = []

    for i in range(4):
        curr = random.randint(1, 256)
        while curr in ip_bytes:
            curr = random.randint(1, 256)
        ip_bytes.append(curr)

    ans_3, ans_4 = ip_bytes[-2] & mask_3, ip_bytes[-1] & mask_4

    ans = [ans_3, ans_4, ip_bytes[0], ip_bytes[1]]
    common.randomize_list(ans, 1, 255, 4, 10)
    c_ans = [""] * 4

    for i in range(len(ans)):
        if ans[i] == ip_bytes[0]:
            c_ans[0] = chr(ord("A")+i)
        elif ans[i] == ip_bytes[1]:
            c_ans[1] = chr(ord("A")+i)
        elif ans[i] == ans_3:
            c_ans[2] = chr(ord("A")+i)
        elif ans[i] == ans_4:
            c_ans[3] = chr(ord("A")+i)

    out_table = Table(8)
    out_table.set_values(ans)
    padding1 = "По заданным IP-адресу узла сети и маске определите адрес сети:\n"
    padding2 = "При записи ответа выберите из приведенных в таблице чисел 4 " \
                "фрагмента - 4 элемента IP-адреса и запишите в нужном порядке " \
                "соответствующие им буквы без точек."
    
    ip_str, mask_str = common.list2string(ip_bytes), common.list2string([255, 255, mask_3, mask_4])
    token = SUB_TYPE_CHAR + ip_str + "_" + mask_str

    ip_mask = "IP-адрес: " + ip_str + "\n" + "Маска: "\
             + mask_str
    task_text = padding1 + ip_mask + "\n" + padding2 + "\n" + out_table.get_str()
    return common.Task(task_text, "".join(c_ans)), token


def generate_type_b(tokens):
    task, token = generate_task()
    while token in tokens:
        task, token = generate_task()
    tokens[token] = 1
    return task


if __name__ == "__main__":
    common.test_func(generate_type_b, {})
