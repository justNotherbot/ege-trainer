import subprocess
import os
import random
import main_helpers


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


class StatisticsManager:

    def __init__(self, f_path):
        self.err_code = 0
        self.stats_by_user = {}
        self.stats_path = f_path

        self.read_stats()

    def add_user(self, u_id):
        self.stats_by_user[u_id] = [0] * (N_STATS_WORDS_IN_LINE - 1)

    def read_stats(self):
        f = None
        try:
            f = open(self.stats_path, "r")
        except FileNotFoundError:
            self.err_code = ERR_STATS_NOT_FOUND
            return
        f_lines = f.readlines()

        tmp = {}
        for i in f_lines:
            curr_words = i.split()
            if len(curr_words) == N_STATS_WORDS_IN_LINE:
                n_numeric = 0
                for j in range(1, len(curr_words)):
                    n_numeric += curr_words[j].isnumeric()
                
                if n_numeric == N_STATS_WORDS_IN_LINE - 1:
                    tmp[curr_words[0]] = list(map(int, curr_words[1:]))
                else:
                    self.err_code = ERR_STATS_CORRUPT
                    f.close()
                    return
            else:
                self.err_code = ERR_STATS_CORRUPT
                f.close()
                return
        self.stats_by_user = tmp
        f.close()

    def save_stats(self):
        f = open(self.stats_path, "w")
        for i in self.stats_by_user:
            s = i + " " + main_helpers.list2string(self.stats_by_user[i]) + "\n"
            f.write(s)
        
        f.close()


class TaskGenerator:

    def __init__(self, s_path, stats_mngr, task_types):
        self.script_path = s_path
        self.stats_mngr = stats_mngr
        self.task_types = task_types

        self.u_id = ""
        self.tasks = []
        self.user_answers = []

    def generate_tasks(self, n_total):
        # Clear data from previous tests
        self.tasks = []
        self.user_answers = [""] * n_total

        # Get amounts of tasks per subtype
        task_distr = self.get_task_distribution(n_total)
        print(task_distr)

        # Get response from the target generation program

        out = None
        try:
            proc = subprocess.Popen(['python3', self.script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            proc.communicate(task_distr.encode("utf-8"))
            out = proc.communicate()[0]
        except Exception:
            return 1
        s_out = out.decode("utf-8").split("<task>")
        if len(s_out) - 1 != n_total * 2:
            return 1
                
        for i in range(0, len(s_out) - 1, 2):
            tmp = (s_out[i], s_out[i+1])
            self.tasks.append(tmp)
        
        random.shuffle(self.tasks)
        return 0
    
    def show_tasks(self):
        for i in range(len(self.tasks)):
            print(str(i+1)+".")
            print(self.tasks[i][0])

    def add_user_answer(self, task_num, ans):
        if 0 <= task_num < len(self.user_answers):
            self.user_answers[task_num] = ans

    def submit(self):
        n_correct = 0
        

    
    def get_task_distribution(self, n_total):
        coefficients = []
        task_amnt = []
        c_sum = 0

        if self.u_id in self.stats_mngr.stats_by_user:
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


stats_manager = StatisticsManager("stats.txt")
print(stats_manager.err_code, stats_manager.stats_by_user)
stats_manager.save_stats()
curr_dir = os.path.dirname(os.path.realpath(__file__))  # Directory where this .py file is located
tgt_dir = os.path.join(curr_dir, "generator", "generator_main.py")
task_gen = TaskGenerator(tgt_dir, stats_manager, ["B", "D", "E"])
task_gen.u_id = "cd"
task_gen.generate_tasks(N_TASKS_PER_TEST)
#task_gen.show_tasks()
#child = subprocess.Popen(['python', 'simple.py'], stdin=subprocess.PIPE)
