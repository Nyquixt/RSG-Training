"""
    Compare Strength Between 2 Networks
"""
import os
from subprocess import Popen

class CompareNetworks:
    def __init__(self, current_folder_path, engine_path, net1_path, net2_path, playout, board_size, komi):
        self.current_folder_path = current_folder_path
        self.engine_path = engine_path

        self.net1_path = net1_path
        self.net2_path = net2_path

        self.playout = playout
        self.board_size = board_size
        self.komi = komi

        self.commands = []

        if 'net1vs' in os.listdir(self.current_folder_path):
            os.system('rm -rf {}'.format(os.path.join(self.current_folder_path, 'net1vs')))
        os.mkdir(os.path.join(self.current_folder_path, 'net1vs'))

        if 'net2vs' in os.listdir(self.current_folder_path):
            os.system('rm -rf {}'.format(os.path.join(self.current_folder_path, 'net2vs')))
        os.mkdir(os.path.join(self.current_folder_path, 'net2vs'))

    def populate_commands(self):

        games_per_process = 100

        for i in range(2):
            self.commands.append(
                'gogui-twogtp -black "{} -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -white "{} -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -auto \
                    -sgffile {} \
                    -games {} \
                    -size {}  \
                    -komi {}'
                    .format(self.engine_path, self.net1_path, self.playout,
                    self.engine_path, self.net2_path, self.playout, 
                    os.path.join(self.current_folder_path, 'net1vs', 'sgf-{}'.format(i)), games_per_process,
                    self.board_size, self.komi)
            )

            self.commands.append(
                'gogui-twogtp -black "{} -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -white "{} -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -auto \
                    -sgffile {} \
                    -games {} \
                    -size {}  \
                    -komi {}'
                    .format(self.engine_path, self.net2_path, self.playout,
                    self.engine_path, self.net1_path, self.playout, 
                    os.path.join(self.current_folder_path, 'net2vs', 'sgf-{}'.format(i)), games_per_process,
                    self.board_size, self.komi)
            )

    def play(self):
        # Parallelly run all the commands in the command list
        procs = []
        for c in self.commands:
            p = Popen(c, shell=True)
            procs.append(p)

        for p in procs:
            p.wait()

    def calculate_wins(self, directory):
        black_count = 0
        white_count = 0
        
        for item in os.listdir(directory):
            if item.lower().endswith('.sgf'):
                f = open(os.path.join(directory, item), 'r')
                line = f.readline()
                if "gogui" in line: # structure of sgf created by gogui program is different
                    line = f.readline()
                result = line.split("RE")[1]

                winner = result.split("+")[0].replace('[','')

                if winner == 'B':
                    black_count += 1
                elif winner == 'W':
                    white_count += 1

        return black_count, white_count

    def calculate_winrate(self):

        net1_1, net2_1 = self.calculate_wins(os.path.join(self.current_folder_path, 'net1vs'))
        net2_2, net1_2 = self.calculate_wins(os.path.join(self.current_folder_path, 'net2vs'))

        net1_wins = net1_1 + net1_2
        net2_wins = net2_1 + net2_2
        
        total_games = net2_wins + net1_wins

        winrate_1 = float(net1_wins / total_games) * 100.0
        winrate_2 = 100.0 - winrate_1

        return winrate_1, winrate_2

    def validate(self):
        wr1, wr2 = self.calculate_winrate()

        print("Network {}: {}% winrate".format(self.net1_path, round(wr1, 2)))
        print("Network {}: {}% winrate".format(self.net2_path, round(wr2, 2)))

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--current-folder-path', type=str, default='.')
    parser.add_argument('-e', '--engine-path', type=str)
    parser.add_argument('--network-one', type=str, required=True)
    parser.add_argument('--network-two', type=str, required=True)
    parser.add_argument('-p', '--playout', type=int, default=100)
    parser.add_argument('-b', '--board-size', type=int, default=7)
    parser.add_argument('-k', '--komi', type=float, default=8.5)

    args = parser.parse_args()

    current_folder_path = args.current_folder_path
    engine_path = args.engine_path
    network_one = args.network_one
    network_two = args.network_two
    playout = args.playout
    board_size = args.board_size
    komi = args.komi

    validator = CompareNetworks(
        current_folder_path=current_folder_path,
        engine_path=engine_path,
        net1_path=network_one,
        net2_path=network_two,
        playout=playout,
        board_size=board_size,
        komi=komi
    )

    validator.populate_commands()
    validator.play()
    validator.validate()