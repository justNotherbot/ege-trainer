import random
import common


SUB_TYPE_CHAR = "D"  # Used for generating tokens


def get_task_text(ip_addr, net_addr, misc_text):
    ip_str = common.list2string(ip_addr)
    net_str = common.list2string(net_addr)
    ip_s = f"Для узла с IP-адресом {ip_str} адрес сети равен {net_str}."

    token = ip_str + "_" + net_str

    return common.COMMON_TEXT + " " + ip_s + " " + misc_text, token


def get_max_mask_byte(b1, b2):
    tmp = 1 << 7

    while (tmp >> 1) & b1 == (tmp >> 1) & b2:
        tmp = tmp >> 1

    all_ones = (1 << 8) - 1
    return all_ones - (tmp - 1)


def generate_ip_net_addr(min_ip, min_mask_bits, min_ip_bits, min_offset):
    n_mask_bits = random.randint(min_mask_bits, common.N_MAX_MASK_BITS)
    n_offset = random.randint(min_offset, common.IP_MASK_OFFSET_MAX)
    n_bits_avail = 8 - n_mask_bits - n_offset
    if n_bits_avail < min_ip_bits:
        n_offset -= min_ip_bits - n_bits_avail
    
    assert n_offset >= 0, f"Non-negative number expected, got: {n_offset}"

    net_val, ip_val, true_offset = common.generate_random_byte(n_mask_bits, n_offset, min_ip)

    ip_bytes = []
    common.randomize_list(ip_bytes, 0, 254, 3, common.MIN_IP_NUM_DEV)
    net_bytes = ip_bytes.copy()
    ip_bytes.append(ip_val)
    net_bytes.append(net_val)

    return ip_bytes, net_bytes, n_mask_bits, true_offset


def get_min_max_val_task():
    byte_options = {False: "третьего слева",
                    True: "последнего (самого правого)"}
    task_options = {False: "наименьшее",
                    True: "наибольшее"}

    ip_bytes, net_bytes, n_mask_bits, n_offset = generate_ip_net_addr(1, 1,
                                                                    common.N_MIN_IP_BITS, 0)

    ask_max = random.choice([True, False])
    
    ans = (2 ** n_mask_bits - 1) << (8 - n_mask_bits)
    if ask_max and n_offset:
        ans += (2 ** n_offset - 1) << (8 - n_mask_bits - n_offset)

    ask_last = random.choice([True, False])
    misc = f"Чему равно {task_options[ask_max]} возможное значение {byte_options[ask_last]}"\
            " байта маски?"
    if not ask_last:
        ip_bytes[-1], ip_bytes[-2] = ip_bytes[-2], ip_bytes[-1]
        net_bytes[-1], net_bytes[-2] = 0, net_bytes[-1]
    
    txt_main, token = get_task_text(ip_bytes, net_bytes, misc)

    return common.Task(txt_main, str(ans), SUB_TYPE_CHAR), token


def get_min_max_count_task():
    val_options = {False: "нулей",
                    True: "единиц"}
    task_options = {False: "наименьшее",
                    True: "наибольшее"}
    
    ip_bytes, net_bytes, n_mask_bits, n_offset = generate_ip_net_addr(1, 1,
                                                                    common.N_MIN_IP_BITS, 0)
    
    ask_max = random.choice([True, False])
    ask_ones = random.choice([True, False])
    
    
    zero_avail = 0
    ones_avail = 24
    ask_last = random.choice([True, False])
    if not ask_last:
        ip_bytes[-1], ip_bytes[-2] = ip_bytes[-2], ip_bytes[-1]
        net_bytes[-1], net_bytes[-2] = 0, net_bytes[-1]
        ones_avail -= 8
        zero_avail += 8
    
    ans = 0

    if not ask_max:
        if not ask_ones:
            ans = 8 - n_mask_bits - n_offset + zero_avail
        else:
            ans = ones_avail + n_mask_bits
    else:
        if not ask_ones:
            ans = 8 - n_mask_bits + zero_avail
        else:
            ans = ones_avail + n_mask_bits + n_offset
    misc = f"Чему равно {task_options[ask_max]} возможное количество {val_options[ask_ones]}"\
            " в двоичной записи маски?"
    txt_main, token = get_task_text(ip_bytes, net_bytes, misc)

    return common.Task(txt_main, str(ans), SUB_TYPE_CHAR), token


def get_n_variants_task():
    ip_bytes, net_bytes, n_mask_bits, n_offset = generate_ip_net_addr(1, 1,
                                                                    common.N_MIN_IP_BITS, 0)
    ans = n_offset + 1
    misc = "Для скольких различных значений маски это возможно?"
    txt_main, token = get_task_text(ip_bytes, net_bytes, misc)

    return common.Task(txt_main, str(ans), SUB_TYPE_CHAR), token


def get_two_devices_task():
    byte_options = {False: "третьего слева",
                    True: "последнего (самого правого)"}
    
    tmp = []
    common.randomize_list(tmp, 0, 254, 6, common.MIN_IP_NUM_DEV)
    ip_1_bytes = tmp[:4]
    ip_2_bytes = tmp[:2] + tmp[4:6]
    
    ask_last = random.choice([True, False])

    ans = 0
    if ask_last:
        # Make sure the task actually has a non-trivial solution
        if ip_1_bytes[-1] & ip_2_bytes[-1] < 128 and ip_1_bytes[-1] | ip_2_bytes[-1] >= 128:
            ip_1_bytes[-1] = ip_1_bytes[-1] | 128
            ip_2_bytes[-1] = ip_2_bytes[-1] | 128
        ans = get_max_mask_byte(ip_1_bytes[-1], ip_2_bytes[-1])
        ip_2_bytes[-2] = ip_1_bytes[-2]
    else:
        # Make sure the task actually has a non-trivial solution
        if ip_1_bytes[-2] & ip_2_bytes[-2] < 128 and ip_1_bytes[-2] | ip_2_bytes[-2] >= 128:
            ip_1_bytes[-2] = ip_1_bytes[-2] | 128
            ip_2_bytes[-2] = ip_2_bytes[-2] | 128
        ans = get_max_mask_byte(ip_1_bytes[-2], ip_2_bytes[-2])
    
    ip_1_s = common.list2string(ip_1_bytes)
    ip_2_s = common.list2string(ip_2_bytes)

    token = ip_1_s + "_" + ip_2_s

    txt = f"Два узла, находящиеся в одной сети, имеют IP-адреса {ip_1_s} и {ip_2_s}."\
           f"Укажите наибольшее возможное значение {byte_options[ask_last]} байта маски сети."\
            " Ответ запишите в виде десятичного числа."
    
    return common.Task(txt, str(ans), SUB_TYPE_CHAR), token


def generate_task():
    types = {"A": get_min_max_val_task,
             "B": get_min_max_count_task,
             "C": get_n_variants_task,
             "D": get_two_devices_task}
    
    sub_type, func = random.choice(list(types.items()))
    task, token = func()
    return task, SUB_TYPE_CHAR + sub_type + token


def generate_type_d(tokens):
    task, token = generate_task()
    while token in tokens:
        task, token = generate_task()
    
    tokens[token] = 1
    return task


if __name__ == "__main__":
    common.test_func(generate_type_d, {})
