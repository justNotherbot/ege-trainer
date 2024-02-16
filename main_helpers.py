CMD_DESC_HDRS = ["Название команды", "Аргументы", "Описание"]

"""
Function: list2string
@param ls: list
@param sep: separator(inserted between values)

@Return(str): string representation of the list
"""

def list2string(ls, sep=" "):
    out = ""
    for i in range(len(ls)):
        out += str(ls[i])
        if i < len(ls) - 1:
            out += sep
    return out


def check_task_string(t_s):
    s_words = t_s.split()
    total = 0
    for i in s_words:
        if len(i) > 1 and i[0].isalpha() and i[0].isupper() and i[1:].isnumeric():
            total += int(i[1:])
        else:
            return 1, 0
    return 0, total


def add_to_table(to_add, table):
    for j in to_add.keys():
        if to_add[j] == "":
            to_add[j] = "None"
        
        table[j].append(to_add[j])
        to_add[j] = ""


def load_cmd_desc(path, space_char="$"):
    tmp_data = {"Название команды": "", "Аргументы": "", "Описание": ""}
    data = {"Название команды": [], "Аргументы": [], "Описание": []}
    n_rows = 0

    f = None
    try:
        f = open(path, "r", encoding="utf-8")
    except Exception:
        return {}, 0, 1
    
    f_lines = f.readlines()

    for i in range(len(f_lines)):
        c_line = f_lines[i].strip()

        if len(c_line) == 0 or c_line[0] == "#":
            continue

        s_words = c_line.split()
        if len(s_words) != 2:
            return {}, 0, 1
        if s_words[0] == "c":
            if tmp_data["Название команды"] != "":
                add_to_table(tmp_data, data)
                n_rows += 1

            tmp_data["Название команды"] = s_words[1]

        elif s_words[0] == "a":
            tmp_data["Аргументы"] += s_words[1].replace(space_char, " ") + " "
        elif s_words[0] == "d":
            tmp_data["Описание"] += s_words[1].replace(space_char, " ") + " "

    if tmp_data["Название команды"] != "":
        add_to_table(tmp_data, data)
        n_rows += 1
    
    return data, n_rows, 0


if __name__ == "__main__":
    data, n_rows, err = load_cmd_desc("cmd_desc.txt")
    print(data, err)
