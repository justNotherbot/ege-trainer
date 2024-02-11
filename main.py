import subprocess
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


stats_manager = StatisticsManager("stats.txt")
print(stats_manager.err_code, stats_manager.stats_by_user)
stats_manager.save_stats()
#child = subprocess.Popen(['python', 'simple.py'], stdin=subprocess.PIPE)
