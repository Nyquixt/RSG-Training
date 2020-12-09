# AI2GO

A Hybrid Approach to Training Stronger Go Engine on Small Boards

## Tools:
- [Leela Zero 0.17](https://github.com/leela-zero/leela-zero)
- [GoGui 1.5.1](https://github.com/Remi-Coulom/gogui)
- [Sabaki](https://github.com/SabakiHQ/Sabaki)
- Python 3.x
- TensorFlow 1.13

## How To Run the Training

### Self-Play

Leela Zero only allows contributing games to the main server, which is trained for the 19x19 board. In this repo, the board size is scaled down to 7x7 and train the network from scratch. GoGUI is used as the middle man to produce self-play games that serve as the training data. TensorFlow is used to train the neural network.

The only 3 things needed to train are the `main.py`, trainer classes in `trainers/` and the `tf/` folder. A script called `create.sh` is provided to copy those 3 things into a separate folder for training. During the training process, a lot of OS system calls are used, so beware! To do so,

    ./create.sh name_of_exp
    cd ../name_of_exp

    # To see all the arguments the program needs
    python3 main.py -h

    # To run the script with the default settings
    python3 main.py -e path/to/leelaz -t . -g number_of_generations

### Analysis

We use Sabaki as the analysis program that pits 2 Go engines. Refer to the Sabaki repo for setting up pitting 2 agents against each other.
