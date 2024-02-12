import random
import common


SUB_TYPE_CHAR = "B"  # Used for generating tokens
MIN_IP_BYTES_DEV = 10  # Used for generating IP


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
    n_dev_bits = random.randint(2, 6)  # Number of device bits
    mask_byte = int("1" * (8 - n_dev_bits) + "0" * n_dev_bits, 2)
    gen_byte_1 = random.randint(1, (1 << (8 - n_dev_bits)) - 1) << n_dev_bits
    gen_byte = random.randint(1, (1 << n_dev_bits) - 1) + gen_byte_1

    mask_bytes = [255] * 3 + [mask_byte] 
    ip_bytes = []
    common.randomize_list(ip_bytes, 1, 254, 3, MIN_IP_BYTES_DEV)
    ip_bytes.append(gen_byte)

    use_third = random.choice([True, False])

    if use_third:
        ip_bytes[2], ip_bytes[3] = ip_bytes[3], ip_bytes[2]
        mask_bytes[2], mask_bytes[3] = mask_bytes[3], 0

    ans_3, ans_4 = ip_bytes[2] & mask_bytes[2], ip_bytes[3] & mask_bytes[3]

    ans = [ans_3, ans_4, ip_bytes[0], ip_bytes[1]]
    common.randomize_list(ans, 1, 255, 4, MIN_IP_BYTES_DEV)
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
    
    ip_str, mask_str = common.list2string(ip_bytes), common.list2string(mask_bytes)
    token = SUB_TYPE_CHAR + ip_str + "_" + mask_str

    ip_mask = "IP-адрес: " + ip_str + "\n" + "Маска: "\
             + mask_str
    task_text = padding1 + ip_mask + "\n" + padding2 + "\n" + out_table.get_str()
    return common.Task(task_text, "".join(c_ans), SUB_TYPE_CHAR), token


def generate_type_b(tokens):
    task, token = generate_task()
    while token in tokens:
        task, token = generate_task()
    tokens[token] = 1
    return task


if __name__ == "__main__":
    common.test_func(generate_type_b, {})
