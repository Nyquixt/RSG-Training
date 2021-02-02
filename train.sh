#!/bin/bash
source /home/ai-lab/anaconda3/etc/profile.d/conda.sh
conda activate tf
./create.sh $1
cd $1
python3 main.py