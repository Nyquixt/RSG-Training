# this shell script creates a another directory on the sub level of the current directory
# after that it will copy all the necessary files, directories needed for training to that new directory
# ./create.sh folder_name
#!/bin/bash

mkdir /$1

cp -r tf/ /$1

cp -r trainers/ /$1

cp -r engine/ /$1

cp -r js/ /$1

cp main.py /$1

cd /$1
