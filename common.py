import random


class Task:
    def __init__(self, text, a):
        self.body = text
        self.ans = a


"""
Function: list2string
@param ls: list
@param sep: separator(inserted between values)

@Return(str): string representation of the list
"""

def list2string(ls, sep="."):
    out = ""
    for i in range(len(ls)):
        out += str(ls[i])
        if i < len(ls) - 1:
            out += sep
    return out


"""
Function: get_rand_num_with_dev
Description:
Generates a random number within a range from target value.
@param v: target value
@param min_val: minimum acceptable value
@param max_val: maximum acceptable value
@param min_dev: minimum deviation of a generated number from target

@Return(int): pseudo-random number
"""

def get_rand_num_with_dev(v, min_val, max_val, min_dev=2):
    lb = v - min_dev
    ub = v + min_dev
    l_val, h_val = min_val, max_val
    if lb > min_val:
        l_val = random.randint(min_val, lb)
    if ub < max_val:
        h_val = random.randint(ub, max_val + 1)
    
    return random.choice([l_val, h_val])


"""
Function: randomize_list
Description:
Adds random values to a list and shuffles it. All random values are guaranteed
to be different.
@param ls: target list(will be modified after the function is invoked)
@param min_val: minimum acceptable random value
@param max_val: maximum acceptable random value
@param n_el_add: number of elements to be added
@param min_dev: minimum deviation of a generated number from last element
"""

def randomize_list(ls, min_val, max_val, n_el_add, min_dev=2):
    if len(ls) == 0:
        ls.append(random.randint(min_val, max_val))
        n_el_add -= 1
    
    for i in range(n_el_add):
        tmp = get_rand_num_with_dev(ls[-1], min_val, max_val, min_dev)
        while tmp in ls:
            tmp = get_rand_num_with_dev(ls[-1], min_val, max_val, min_dev)
        ls.append(tmp)
    
    random.shuffle(ls)


"""
Function: generate_random_byte
@param n_mask_bits: number of mask bits equal to 1(for given byte)
@param n_offset: minimal distance(in null bits) between device value 
and network value
@param min_sub: minumal network value
@param min_l: minimal device value

@Return(int): network byte and device byte
"""

def generate_random_byte(n_mask_bits, n_offset, min_l=1):
    assert n_mask_bits + n_offset < 9, \
        f"Number less than 9 expected, got: {n_mask_bits + n_offset}"

    sub_val = 0
    if n_mask_bits:
        v_max = 2 ** (n_mask_bits-1) - 1
        if n_mask_bits > 1:
            v_max -= 1  # Don't let the network byte be equal to the mask byte
        sub_val = random.randint(0, v_max)
        sub_val = (sub_val << 1) + 1

    device_bits = 8 - n_mask_bits - n_offset
    l_max = 2 ** (8 - n_mask_bits - n_offset) - 2  # IP of a device cannot be a broadcast address
    l_val = 0
    l_zeroes = 1
    if l_max >= min_l:
        l_val = random.randint(min_l, l_max)
        l_zeroes = device_bits - (len(bin(l_val)) - 2)
    net_byte = (sub_val << (8 - n_mask_bits))

    assert net_byte != 0, f"Non-zero net byte expected, got {net_byte}"
    
    return net_byte, net_byte + l_val, l_zeroes + n_offset


"""
Function: test_func
Description:
Tests a desired task generation function.
@param tgt_func: desired task generation function(must return a Task object)
"""

def test_func(tgt_func):
    task = tgt_func()
    print(task.body)
    if input() == task.ans:
        print("Correct")
    else:
        print("Wrong", task.ans)
