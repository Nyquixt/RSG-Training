import argparse
from trainers.selfplay import AI2GOBotSelfPlay

parser = argparse.ArgumentParser()

parser.add_argument('--generations', '-g', type=int, default=5, help='Number of generations to be trained')
parser.add_argument('--train-folder-path', '-t', type=str, default='.', help='Path to folder that stores sgf folder during training')
parser.add_argument('--random-move', type=int, default=10, help='Starting with x first random moves for first 10 generations. It will decay.')
parser.add_argument('--visit', type=int, default=50, help='Number of visits during selfplay.')
parser.add_argument('--playout', type=int, default=25, help='Number of playouts during validation.')
parser.add_argument('--gate', type=int, default=55, help='Validation gate.')
parser.add_argument('--random-temp', type=float, default=1.0, help='Parameter for search temparature in MCTS.')
parser.add_argument('--size', type=int, default=7, help='Board size.')
parser.add_argument('--komi', type=float, default=8.5, help='Komi.')
parser.add_argument('--block', type=int, default=4, help='Number of blocks of network.')
parser.add_argument('--filter', type=int, default=128, help='Number of filters of network.')
parser.add_argument('--past-generations', type=int, default=10, help='Number of past generations whose games are used for training.')
parser.add_argument('--games-per-gen', type=int, default=1000, help='Number of games deleted when exceeding maximum games for training. This number should be equal the number of games generated per generation!!!')
parser.add_argument('--num-process', type=int, default=10, help='Number of process to self-play')
parser.add_argument('--step', type=int, default=1000, help='Save new net at every x training step. Remember to fix tf folder as well.')

args = parser.parse_args()

# path to engine and where to store the training files
train_folder_path = args.train_folder_path

# HYPER-PARAMETERS
generations = args.generations

random_move = args.random_move
visit = args.visit
playout = args.playout
gate = args.gate
random_temp = args.random_temp

size = args.size
komi = args.komi

train_block = args.block
train_filter = args.filter

step = args.step

past_generations = args.past_generations
games_per_gen = args.games_per_gen
num_process = args.num_process

AI2GOTrainer = AI2GOBotSelfPlay(
    train_folder_path=train_folder_path,
    generations=generations,
    random_move=random_move,
    visit=visit,
    playout=playout,
    gate=gate,
    random_temp=random_temp,
    komi=komi,
    board_size=size,
    net_block=train_block,
    net_filter=train_filter,
    step=step,
    past_generations=past_generations,
    games_per_gen=games_per_gen,
    num_process=num_process
)

AI2GOTrainer.train()