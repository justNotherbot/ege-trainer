import subprocess
import os
import random
import time
import main_helpers
import pyqt_helpers


B_SOLVED_IDX = 0
B_ALL_IDX = 1
D_SOLVED_IDX = 2
D_ALL_IDX = 3
E_SOLVED_IDX = 4
E_ALL_IDX = 5
ERR_STATS_NOT_FOUND = 1
ERR_STATS_CORRUPT = 2
N_STATS_WORDS_IN_LINE = 7
N_TASKS_PER_TEST = 15

WRONG_CMD_MSG = "Неверный формат команды"
INVALID_LOGIN_MSG = "Невозможно сменить пользователя. Используйте logout, "\
                    "или введите корректное имя пользователя."
STATS_CORRUPT_MSG = "При чтении файла stats.txt возникла ошибка. Этот файл " \
                    "будет пересохранён после завершения программы."
DESC_CORRUPT_MSG = "Справка о командах не будет отображаться."
TASK_GEN_MSG = "При генерации заданий возникла ошибка. "


class StatisticsManager:

    def __init__(self, f_path):
        self.err_code = 0
        self.stats_by_user = {}  # Statistics that are used by the program
        self.useronly_by_user = {}  # Statistics that are stored, but not used for task generation
        self.stats_path = f_path

        self.read_stats()

    def add_user(self, u_id):
        self.stats_by_user[u_id] = [0] * (N_STATS_WORDS_IN_LINE - 1)
        self.useronly_by_user[u_id] = [[], []]

    def add_useronly_stats(self, u_id, time_min, r_solved):
        if u_id in self.useronly_by_user:
            self.useronly_by_user[u_id][0].append(time_min)
            self.useronly_by_user[u_id][1].append(r_solved)

    def read_stats(self):
        f = None
        try:
            f = open(self.stats_path, "r")
        except FileNotFoundError:
            self.err_code = ERR_STATS_NOT_FOUND
            return
        f_lines = f.readlines()

        tmp = {}
        tmp_useronly = {}  # Statistics that aren't used by the program
        for i in f_lines:
            curr_words = i.split()
            if len(curr_words) >= N_STATS_WORDS_IN_LINE and len(curr_words) % 2 == 1:
                n_numeric = 0
                for j in range(1, len(curr_words)):
                    curr_word = curr_words[j].replace(".", "0")
                    n_numeric += curr_word.isnumeric()
                
                n_crucial = N_STATS_WORDS_IN_LINE - 1
                if n_numeric >= n_crucial and n_numeric == len(curr_words)-1:
                    tmp[curr_words[0]] = list(map(int, curr_words[1:n_crucial+1]))
                    tmp_useronly[curr_words[0]] = [[], []]
                    for j in range(n_crucial+1, len(curr_words)):
                        cnt = j - n_crucial-1
                        tmp_useronly[curr_words[0]][cnt % 2].append(float(curr_words[j]))
                else:
                    self.err_code = ERR_STATS_CORRUPT
                    f.close()
                    return
            else:
                self.err_code = ERR_STATS_CORRUPT
                f.close()
                return
        # DEBUG
        print(tmp_useronly)
        self.stats_by_user = tmp
        self.useronly_by_user = tmp_useronly
        f.close()

    def save_stats(self):
        f = open(self.stats_path, "w")
        for i in self.stats_by_user:
            s_add = ""
            for j in range(len(self.useronly_by_user[i][0])):
                s_add += str(round(self.useronly_by_user[i][0][j], 4)) + " " +\
                      str(round(self.useronly_by_user[i][1][j], 4)) + " "
            s = i + " " + main_helpers.list2string(self.stats_by_user[i]) + " " + s_add + "\n"
            f.write(s)
        
        f.close()


class TaskGenerator:

    def __init__(self, s_path, stats_mngr, task_types):
        self.script_path = s_path
        self.stats_mngr = stats_mngr
        self.task_types = task_types

        self.has_started = False  # True if the test has started. Otherwise, False. Will inhibit submission when False.
        self.save_stats = True
        self.time_start = 0
        self.u_id = ""
        self.tasks = []
        self.user_answers = []

    def generate_tasks(self, n_total, t_distr=None):
        if n_total == 0:
            return 1
        # Clear data from previous tests
        self.tasks = []
        self.user_answers = [""] * n_total

        # Get amounts of tasks per subtype
        task_distr = ""
        if t_distr != None:
            gen_distr = False
            task_distr = t_distr
            self.save_stats = False
        if self.save_stats:
            task_distr = self.get_task_distribution(n_total)
        # DEBUG
        print(task_distr)

        # Get response from the target generation program

        out = None
        try:
            proc = subprocess.Popen(['python3', self.script_path], stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
            proc.communicate(task_distr.encode("utf-8"))
            out = proc.communicate()[0]
        except Exception:
            return 1
        s_out = out.decode("utf-8").split("<task>")
        if len(s_out) - 1 != n_total * 3:
            return 1
                
        for i in range(0, len(s_out) - 1, 3):
            tmp = (s_out[i+1], s_out[i+2], s_out[i])
            self.tasks.append(tmp)
        
        random.shuffle(self.tasks)
        return 0
    
    def show_tasks(self):
        for i in range(len(self.tasks)):
            print(str(i+1)+".")
            print(self.tasks[i][0])
            # DEBUG
            print(self.tasks[i][1])
        
        self.time_start = time.time()
        self.has_started = True

    def add_user_answer(self, task_num, ans):
        print(task_num, ans)
        if 0 <= task_num < len(self.user_answers):
            self.user_answers[task_num] = ans

    def submit(self):
        if not self.has_started:
            return
        
        n_correct = 0
        stats_per_type = {"B": B_SOLVED_IDX, "D": D_SOLVED_IDX, "E": E_SOLVED_IDX}

        out = []

        for i in range(len(self.user_answers)):
            is_correct = self.tasks[i][1] == self.user_answers[i]
            if not is_correct:
                your_ans = ""
                if len(self.user_answers[i]):
                    your_ans = f"Ваш ответ: {self.user_answers[i]}. "
                out.append("Задание " + str(i+1) + ": " + your_ans + f"Правильный ответ: {self.tasks[i][1]}")
            n_correct += is_correct

            if self.save_stats and self.u_id in self.stats_mngr.stats_by_user:
                task_type = self.tasks[i][2]
                idx = stats_per_type[task_type]

                self.stats_mngr.stats_by_user[self.u_id][idx] += is_correct
                self.stats_mngr.stats_by_user[self.u_id][idx+1] += 1

        # Reset some key variables
        self.has_started = False
        self.save_stats = True

        curr_time = time.time()
        time_spent_min = (curr_time - self.time_start) / 60
        # Save additional statistics:
        self.stats_mngr.add_useronly_stats(self.u_id, time_spent_min, n_correct/len(self.user_answers))

        print(f"Решено {n_correct} из {len(self.user_answers)}.")
        print(f"Потрачено {round(time_spent_min)} минут.")
        print(*out, sep="\n")

    
    def get_task_distribution(self, n_total):
        coefficients = []
        task_amnt = []
        c_sum = 0

        if self.u_id in self.stats_mngr.stats_by_user and not (0 in self.stats_mngr.stats_by_user[self.u_id]):
            ls = self.stats_mngr.stats_by_user[self.u_id]
            initial = 1 - (ls[0] / ls[1])
            for i in range(0, len(ls), 2):
                curr = 1 - (ls[i] / ls[i+1])
                coefficients.append(curr / initial)
                c_sum += curr / initial
        else:
            coefficients = [1] * len(self.task_types)
            c_sum = len(self.task_types)
        print(coefficients, c_sum)
        n_tasks_first = round(n_total / c_sum)
        for i in range(len(coefficients)):
            tasks_curr = int(round(n_tasks_first * coefficients[i]))
            if tasks_curr > n_total:
                tasks_curr = n_total
            task_amnt.append(tasks_curr)
            n_total -= tasks_curr

        s = ""
        for i in range(len(self.task_types)):
            s += self.task_types[i] + str(task_amnt[i]) + " "

        return s


class ConsoleContext:

    def __init__(self, script_dir, script_name, desc_path, stats_path, task_types, qt_mngr):
        self.u_id = ""
        self.script_dir = script_dir
        self.script_path = os.path.join(script_dir, script_name)
        self.stats_manager = StatisticsManager(stats_path)
        self.task_gen = TaskGenerator(self.script_path, self.stats_manager, task_types)

        self.qt_mngr = qt_mngr

        data, n_rows, err = main_helpers.load_cmd_desc(desc_path)
        self.err_code = err
        self.help_table = pyqt_helpers.Table(main_helpers.CMD_DESC_HDRS, n_rows, data)

    def show_help(self):
        if not self.err_code:
            self.help_table.show(self.qt_mngr)

    def setuid(self, u_id):
        if (self.u_id == "" and u_id in self.stats_manager.stats_by_user) or u_id == "":
            self.u_id = u_id
            self.task_gen.u_id = u_id
            return 0
        return 1

    def createuid(self, u_id):
        self.stats_manager.add_user(u_id)

    def start_test(self, n_tasks, gen_str):
        if not self.task_gen.has_started:
            err = self.task_gen.generate_tasks(n_tasks, gen_str)
            self.task_gen.show_tasks()
            return err
        return 1

    def answer(self, task_num, ans):
        self.task_gen.add_user_answer(task_num, ans)

    def submit(self):
        self.task_gen.submit()


def help_cmd(console_context, args):
    if len(args) != 0:
        print(WRONG_CMD_MSG)
        return
    
    console_context.show_help()

def login(console_context, args):
    if len(args) != 1 or args[0] == "":
        print(WRONG_CMD_MSG)
        return
    
    err = console_context.setuid(args[0])
    if err:
        print(INVALID_LOGIN_MSG)


def logout(console_context, args):
    if len(args) != 0:
        print(WRONG_CMD_MSG)
        return
    
    console_context.setuid("")


def create(console_context, args):
    if len(args) != 1:
        print(WRONG_CMD_MSG)
        return

    console_context.createuid(args[0])


def start_test(console_context, args):
    if len(args) > 1:
        print(WRONG_CMD_MSG)
        return
    s_gen = None
    n_tasks = N_TASKS_PER_TEST

    if len(args) == 1:
        args[0] = args[0].replace("_", " ")
        err, n = main_helpers.check_task_string(args[0])
        if err:
            print(WRONG_CMD_MSG)
            return
        n_tasks = n
        s_gen = args[0]
    
    err = console_context.start_test(n_tasks, s_gen)
    if err:
        s_add = f"Пожалуйста, убедитесь, что файлы в директории {console_context.script_dir}"\
                 " не повреждены."
        print(TASK_GEN_MSG + s_add)


def answer(console_context, args):
    if len(args) != 2 or not args[0].isnumeric():
        print(WRONG_CMD_MSG)
        return
    
    console_context.answer(int(args[0])-1, args[1])


def submit(console_context, args):
    if len(args) != 0:
        print(WRONG_CMD_MSG)
        return
    
    console_context.submit()


def fini(console_context, args):
    if len(args) != 0:
        print(WRONG_CMD_MSG)
        return
    
    console_context.stats_manager.save_stats()
    exit()


command_map = {"-h": help_cmd,
               "login": login,
               "logout": logout,
               "exit": fini,
               "create": create,
               "start_test": start_test,
               "answer": answer,
               "submit": submit}


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.realpath(__file__))  # Directory where this .py file is located
    generator_dir = os.path.join(curr_dir, "generator")
    cmd_desc_path = os.path.join(curr_dir, "cmd_desc.txt")

    qt_manager = pyqt_helpers.QTManager()

    c_context = ConsoleContext(generator_dir, "generator_main.py", cmd_desc_path, 
                               "stats.txt", ["B", "D", "E"], qt_manager)
    
    if c_context.stats_manager.err_code == ERR_STATS_CORRUPT:
        print(STATS_CORRUPT_MSG)
    if c_context.err_code:
        print(f"При чтении файла {cmd_desc_path} возникла ошибка."+DESC_CORRUPT_MSG)

    while True:
        s = input(c_context.u_id + ">")
        words = s.strip().split()

        if len(words):
            cmd = words[0]
            if cmd not in command_map:
                print(WRONG_CMD_MSG)
            else:
                command_map[cmd](c_context, words[1:])
