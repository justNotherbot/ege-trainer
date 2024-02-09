import random
import common


COMMON_TEXT = "В терминологии сетей TCP/IP маской сети называют двоичное число, "\
    "которое показывает, какая часть IP-адреса узла сети относится к адресу сети, "\
    "а какая - к адресу узла в этой сети. Адрес сети получается в результате "\
    "применения поразрядной конъюнкции к заданному адресу узла и маске сети."

N_MAX_MASK_BITS = 4
MIN_IP_NUM_DEV = 10
IP_MASK_OFFSET_MAX = 2
N_MIN_IP_BITS = 3


def get_task_text(ip_addr, net_addr, misc_text):
    global COMMON_TEXT

    ip_str = common.list2string(ip_addr)
    net_str = common.list2string(net_addr)
    ip_s = f"Для узла с IP-адресом {ip_str} адрес сети равен {net_str}."

    return COMMON_TEXT + " " + ip_s + " " + misc_text


def get_max_mask_byte(b1, b2):
    tmp = 1 << 7

    while (tmp >> 1) & b1 == (tmp >> 1) & b2:
        tmp = tmp >> 1

    all_ones = (1 << 8) - 1
    return all_ones - (tmp - 1)


def generate_ip_net_addr(min_ip, min_mask_bits, min_ip_bits, min_offset):
    n_mask_bits = random.randint(min_mask_bits, N_MAX_MASK_BITS)
    n_offset = random.randint(min_offset, IP_MASK_OFFSET_MAX)
    n_bits_avail = 8 - n_mask_bits - n_offset
    if n_bits_avail < min_ip_bits:
        n_offset -= min_ip_bits - n_bits_avail
    
    assert n_offset >= 0, f"Non-negative number expected, got: {n_offset}"

    net_val, ip_val, true_offset = common.generate_random_byte(n_mask_bits, n_offset, min_ip)

    ip_bytes = []
    common.randomize_list(ip_bytes, 0, 255, 3, MIN_IP_NUM_DEV)
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
                                                                      N_MIN_IP_BITS, 0)

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
    
    txt_main = get_task_text(ip_bytes, net_bytes, misc)

    return common.Task(txt_main, str(ans))


def get_min_max_count_task():
    val_options = {False: "нулей",
                    True: "единиц"}
    task_options = {False: "наименьшее",
                    True: "наибольшее"}
    
    ip_bytes, net_bytes, n_mask_bits, n_offset = generate_ip_net_addr(1, 1,
                                                                      N_MIN_IP_BITS, 0)
    
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
    txt_main = get_task_text(ip_bytes, net_bytes, misc)

    return common.Task(txt_main, str(ans))


def get_n_variants_task():
    ip_bytes, net_bytes, n_mask_bits, n_offset = generate_ip_net_addr(1, 1,
                                                                      N_MIN_IP_BITS, 0)
    ans = n_offset + 1
    misc = "Для скольких различных значений маски это возможно?"
    txt_main = get_task_text(ip_bytes, net_bytes, misc)

    return common.Task(txt_main, str(ans))


def get_two_devices_task():
    byte_options = {False: "третьего слева",
                    True: "последнего (самого правого)"}
    
    tmp = []
    common.randomize_list(tmp, 0, 254, 6, MIN_IP_NUM_DEV)
    ip_1_bytes = tmp[:4]
    ip_2_bytes = tmp[:2] + tmp[4:6]
    
    ask_last = random.choice([True, False])

    ans = 0
    if ask_last:
        if ip_1_bytes[-1] & ip_2_bytes[-1] < 128 and ip_1_bytes[-1] | ip_2_bytes[-1] >= 128:
            ip_1_bytes[-1] = ip_1_bytes[-1] | 128
            ip_2_bytes[-1] = ip_2_bytes[-1] | 128
        ans = get_max_mask_byte(ip_1_bytes[-1], ip_2_bytes[-1])
        ip_2_bytes[-2] = ip_1_bytes[-2]
    else:
        if ip_1_bytes[-2] & ip_2_bytes[-2] < 128 and ip_1_bytes[-2] | ip_2_bytes[-2] >= 128:
            ip_1_bytes[-2] = ip_1_bytes[-2] | 128
            ip_2_bytes[-2] = ip_2_bytes[-2] | 128
        ans = get_max_mask_byte(ip_1_bytes[-2], ip_2_bytes[-2])
    
    ip_1_s = common.list2string(ip_1_bytes)
    ip_2_s = common.list2string(ip_2_bytes)

    txt = f"Два узла, находящиеся в одной сети, имеют IP-адреса {ip_1_s} и {ip_2_s}."\
           f"Укажите наибольшее возможное значение {byte_options[ask_last]} байта маски сети."\
            " Ответ запишите в виде десятичного числа."
    
    return common.Task(txt, str(ans))


if __name__ == "__main__":
    common.test_func(get_two_devices_task)
