"""
    A Trainer Class for the AI2GOBot in Self-Play Mode
"""
# OS packages
import os
import subprocess
from subprocess import Popen

# Aux packages
import time
from datetime import timedelta

class AI2GOBotSelfPlay:
    def __init__(self, train_folder_path, generations, random_move, visit, random_temp, 
                komi, board_size, net_block, net_filter, step, past_generations, 
                games_per_gen, num_process):
        self.train_folder_path = train_folder_path # folder that stores the current gen's parsed sgf files
        
        # main hyper-parameters
        self.generations = generations
        self.random_move = random_move # the engine plays first random_move moves randomly
        self.visit = visit
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
        self.commands = []

        # keep track of checkpoints
        self.current_checkpoint = self.step
        
        self.make_folders()
        self.init_network()

    def make_folders(self):
        os.system('mkdir sgf') # to store sgf files
        os.system('mkdir models') # to store networks for each generation

    def init_network(self): # TODO: omit the training part because the new selfplay script don't encounter the GoGUI bug anymore
        print("Initializing Network...")

        # generate a random network and rename it to best-network.txt
        os.system('python tf/init_random_weights.py --blocks {} --filters {} >>output.txt 2>&1'.format(self.net_block, self.net_filter))
        os.system('cp leelaz-model-0.txt best-network.txt')

        self.populate_commands(0)
        self.self_play()
        self.dump_data()
        # train the new model, also train from 1st checkpoint - step, by now we should have leelaz-model-{step}.txt 
        os.system('python tf/parse.py {} {} train_data/train.out >>output.txt 2>&1'.format(self.net_block, self.net_filter))
        # os.system('rm best-network.txt')
        os.system('cp leelaz-model-{}.txt best-network.txt'.format(self.step))
        # remove the data folder
        os.system('rm -rf train_data')
        os.system('rm -rf sgf')
        os.system('mkdir sgf')

    def populate_commands(self, current_generation):

        games_per_process = self.games_per_gen // self.num_process

        self.commands.clear() # empty the list

        for i in range(self.num_process):
            self.commands.append(
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

    def self_play(self):
        # Parallelly run all the commands in the command list
        procs = []
        for c in self.commands:
            p = Popen(c, shell=True)
            procs.append(p)

        for p in procs:
            p.wait()

    def keep_max_games(self, generation):
        os.system('rm {}'.format(os.path.join(self.train_folder_path, 'sgf', 'sgf{}*'.format(generation) )) )

    def dump_data(self):
        os.system('cat sgf/*.sgf > train.sgf')

        # Make data folder
        os.system('mkdir train_data')

        # Dump to training data
        os.system('echo "dump_supervised train.sgf ./train_data/train.out" | ./engine/leelaz -w best-network.txt >>output.txt 2>&1')

    def train_network(self):
        # Resume training from the best checkpoint
        os.system('python tf/parse.py {} {} train_data/train.out leelaz-model-{} >> output.txt 2>&1'.format(self.net_block, self.net_filter, self.current_checkpoint)) 

        # remove the data folder
        os.system('rm -rf train_data')

    def train(self):

        start = time.time()

        for generation in range(1, self.generations + 1):
            gen_start = time.time()
            print("Generation {}".format(generation))
            self.populate_commands(generation)
            print("Self-Play Phase...")
            self.self_play()
            if generation > self.past_generations:
                self.keep_max_games(generation - self.past_generations)
            print("Train New Network Phase...")
            self.dump_data()
            self.train_network()

            # Save current model to models/ folder
            os.system('cp leelaz-model-{}.txt gen-{}.txt'.format(self.current_checkpoint, generation))
            os.system('mv gen-{}.txt models/'.format(generation))

            # Reassign values
            self.current_checkpoint += self.step

            # Set current network to be best best network
            os.system('rm best-network.txt')
            os.system('cp leelaz-model-{}.txt best-network.txt'.format(self.current_checkpoint))

            gen_end = time.time()
            # Logging
            with open('log.txt', 'a+') as f:
                f.write('*********************************\n')
                f.write( 'Generation {} trained for: {}\n'.format( generation, str(timedelta(seconds=int(gen_end - gen_start)) ) ) )
                f.write('*********************************\n')

        end = time.time()

        print('Total time trained: {}'.format( str(timedelta(seconds=int(end - start)) ) ))