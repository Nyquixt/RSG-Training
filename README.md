# RSG Training

Training script for ReadySetGo

## Tools:
- [Leela Zero 0.17](https://github.com/leela-zero/leela-zero)
- [@Sabaki/gtp](https://openbase.io/js/@sabaki/gtp/documentation)
- Python 3.7
- TensorFlow 1.13

## Installing Conda

Follow this [instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html).

Create a conda environment that at least has Python 3.7 and Tensorflow 1.13

    conda create -n <env_name> tensorflow=1.13

Python 3.7 will automatically be installed along with Tensorflow 1.13. Then, activate the conda environment and run the training.


## How To Run the Training

Leela Zero only allows contributing games to the main server, which is trained for the 19x19 board. In this repo, the board size is scaled down to 7x7 and train the network from scratch. GoGUI is used as the middle man to produce self-play games that serve as the training data. TensorFlow is used to train the neural network.

The only things needed to train are the `main.py`, the `js/` folder, trainer classes in `trainers/` and the `tf/` folder. A script called `create.sh` is provided to copy those 3 things into a separate folder for training. During the training process, a lot of OS system calls are used, so beware! To do so,

    ./create.sh training_id
    cd training_id

    # To see all the arguments the program needs
    python3 main.py -h

    # To run the script with the default settings
    python3 main.py