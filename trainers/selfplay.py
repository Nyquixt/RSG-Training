"""
    A Trainer Class for the AI2GOBot in Self-Play Mode
    TODO: Bring back the elo system :(
"""
# OS packages
import os
import subprocess
from subprocess import Popen

# Aux packages
import time
import math
from datetime import timedelta

class AI2GOBotSelfPlay:
    def __init__(self, train_folder_path, generations, random_move, visit, playout, gate, random_temp, 
                komi, board_size, net_block, net_filter, step, past_generations, 
                games_per_gen, num_process):
        self.train_folder_path = train_folder_path # folder that stores the current gen's parsed sgf files
        
        # main hyper-parameters
        self.generations = generations
        self.random_move = random_move # the engine plays first random_move moves randomly
        self.visit = visit
        self.playout = playout
        self.gate = gate
        self.random_temp = random_temp

        # game parameters
        self.komi = komi
        self.board_size = board_size

        # network parameters
        self.net_block = net_block
        self.net_filter = net_filter

        # aux parameters
        self.step = step
        self.past_generations = past_generations # the past generations whose games are used for training
        self.games_per_gen = games_per_gen

        # commands list
        self.num_process = num_process
        self.selfplay_commands = []
        self.validation_commands = []

        # keep track of checkpoints
        self.best_checkpoint = self.step
        self.current_checkpoint = self.best_checkpoint + self.step
        self.best_generation = 0
        self.best_elo = 0.0
        
        self.make_folders()
        self.init_network()

    def make_folders(self):
        os.system('mkdir sgf') # to store sgf files
        os.system('mkdir models') # to store networks for each generation

    def init_network(self):
        print("Initializing Network...")

        # generate a random network and rename it to best-network.txt
        os.system('python tf/init_random_weights.py --blocks {} --filters {} >>output.txt 2>&1'.format(self.net_block, self.net_filter))
        os.system('cp leelaz-model-0.txt best-network.txt')

        self.populate_selfplay_commands(0)
        self.selfplay()
        self.dump_data()
        # train the new model, also train from 1st checkpoint - step, by now we should have leelaz-model-{step}.txt 
        os.system('python tf/parse.py {} {} train_data/train.out >>output.txt 2>&1'.format(self.net_block, self.net_filter))
        # os.system('rm best-network.txt')
        os.system('cp leelaz-model-{}.txt best-network.txt'.format(self.step))
        # remove the data folder
        os.system('rm -rf train_data')
        os.system('rm -rf sgf')
        os.system('mkdir sgf')
        with open('progress.txt', 'w') as outfile:
            outfile.write('1,0.0') # Generation 0, Elo 0, this is for the main server to read progress

    def populate_selfplay_commands(self, current_generation):

        games_per_process = self.games_per_gen // self.num_process

        self.selfplay_commands.clear() # empty the list

        for i in range(self.num_process):
            self.selfplay_commands.append(
                'node js/selfplay.js \
                    -e ./engine/leelaz \
                    -w {} \
                    -v {} \
                    -m {} \
                    --randomtemp {} \
                    -r 0 \
                    -b {} \
                    -k {} \
                    --numgame {} \
                    --sgfname {}'.format(
                        os.path.join(self.train_folder_path, 'best-network.txt'),
                        self.visit,
                        self.random_move,
                        self.random_temp,
                        self.board_size,
                        self.komi,
                        games_per_process,
                        os.path.join(self.train_folder_path, 'sgf', 'sgf-{}-{}'.format(current_generation, i))
                    )
            )


    def populate_validation_commands(self): # validation still use gogui because we have to pit 2 networks against each other

        games_per_process = 50

        self.validation_commands.clear()

        # Games where best network is black
        for i in range(2):
            self.validation_commands.append(
                'gogui-twogtp -black "./engine/leelaz -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -white "./engine/leelaz -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -auto \
                    -sgffile {} \
                    -games {} \
                    -size {}  \
                    -komi {}'
                    .format(os.path.join(self.train_folder_path, 'best-network.txt'), self.playout,
                    os.path.join(self.train_folder_path, 'leelaz-model-{}.txt'.format(self.current_checkpoint)),
                    self.playout, os.path.join(self.train_folder_path, 'bestvs', 'sgf{}'.format(i)), games_per_process, 
                    self.board_size, self.komi)
            )

        # Games where current network is black
        for i in range(2):
            self.validation_commands.append(
                'gogui-twogtp -black "./engine/leelaz -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -white "./engine/leelaz -g -w {} -r 0 -p {} --noponder --gpu 0 --randomtemp 0" \
                    -auto \
                    -sgffile {} \
                    -games {} \
                    -size {}  \
                    -komi {}'
                    .format(os.path.join(self.train_folder_path, 'leelaz-model-{}.txt'.format(self.current_checkpoint)), 
                    self.playout, os.path.join(self.train_folder_path, 'best-network.txt'),
                    self.playout, os.path.join(self.train_folder_path, 'vsbest', 'sgf{}'.format(i)), games_per_process, 
                    self.board_size, self.komi)
            )

    def selfplay(self):
        # parallelly run all the commands in the command list
        procs = []
        for c in self.selfplay_commands:
            p = Popen(c, shell=True)
            procs.append(p)

        for p in procs:
            p.wait()

    def keep_max_games(self, generation): # delete all games from the specified generation
        os.system('rm {}'.format(os.path.join(self.train_folder_path, 'sgf', 'sgf-{}*'.format(generation) )) )

    def dump_data(self):
        os.system('cat sgf/*.sgf > train.sgf')
        os.system('mkdir train_data')
        # Dump to training data
        os.system('echo "dump_supervised train.sgf ./train_data/train.out" | ./engine/leelaz -w best-network.txt >>output.txt 2>&1')

    def train_network(self):
        # Resume training from the best checkpoint
        os.system('python tf/parse.py {} {} train_data/train.out leelaz-model-{} >> output.txt 2>&1'.format(self.net_block, self.net_filter, self.best_checkpoint)) 
        # remove the data folder
        os.system('rm -rf train_data')

    def validate_network(self):
        # Make necessary folders
        os.system('mkdir bestvs') # sgf games where best network is black
        os.system('mkdir vsbest') # sgf games where current network is black

        self.populate_validation_commands()
        # run the commands as processes
        procs = []
        for j in (self.validation_commands):
            p = Popen(j, shell=True)
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

        best_net_1, current_net_1 = self.calculate_wins(os.path.join(self.train_folder_path, 'bestvs'))
        current_net_2, best_net_2 = self.calculate_wins(os.path.join(self.train_folder_path, 'vsbest'))

        current_net_wins = current_net_1 + current_net_2
        best_net_wins = best_net_1 + best_net_2

        total_games = current_net_wins + best_net_wins
        winrate = float(current_net_wins / total_games) * 100
        if winrate >= self.gate:
            return True, winrate # Pass
        else:
            return False, winrate

    def calculate_elo_difference(self, winrate):
        if winrate == 0.0:
            elo_diff = 400 * math.log10(100.0)
        elif winrate == 100.0:
            elo_diff = -(400 * math.log10(100.0))
        else:
            elo_diff = 400 * math.log10((100.0 - winrate) / winrate)

        return elo_diff 

    def train(self):

        start = time.time()

        for generation in range(1, self.generations + 1):
            gen_start = time.time()
            print("Generation {}".format(generation))
            self.populate_selfplay_commands(generation)
            print("Self-Play Phase...")
            self.selfplay()
            if generation > self.past_generations:
                self.keep_max_games(generation - self.past_generations)
            print("Train New Network Phase...")
            self.dump_data()
            self.train_network()
            print("Validate New Network Phase...")
            self.validate_network()
            result, winrate = self.calculate_winrate()

            if result == True: # pass
                # Save passed network to models/ folder
                os.system('cp leelaz-model-{}.txt gen-{}.txt'.format(self.current_checkpoint, generation))
                os.system('mv gen-{}.txt models/'.format(generation))

                # Set current network to be best best network
                os.system('rm best-network.txt')
                os.system('cp leelaz-model-{}.txt best-network.txt'.format(self.current_checkpoint))

                # Reassign values
                self.best_generation = generation
                self.best_checkpoint = self.current_checkpoint
                self.current_checkpoint = self.best_checkpoint + self.step

                elo_diff = self.calculate_elo_difference(winrate)
                self.best_elo = round(self.best_elo - elo_diff, 2)
                with open('progress.txt', 'w') as outfile:
                    outfile.write('{},{}'.format(generation + 1, self.best_elo)) # current generation + 1, current best elo from current generation
            
            else: # Fail, calculate elo
                
                elo_diff = self.calculate_elo_difference(winrate)
                elo = round(self.best_elo - elo_diff, 2)
                with open('progress.txt', 'w') as outfile:
                    outfile.write('{},{}'.format(generation + 1, elo)) # current generation + 1, current elo from current generation

            gen_end = time.time()
            # Logging
            with open('log.txt', 'a+') as f:
                f.write('*********************************\n')
                f.write('Generation {} trained for: {}\n'.format( generation, str(timedelta(seconds=int(gen_end - gen_start)) ) ) )
                f.write('Elo: {}'.format(self.best_elo if result == True else elo))
                f.write('*********************************\n')

        end = time.time()

        print('Total time trained: {}'.format( str(timedelta(seconds=int(end - start)) ) ))