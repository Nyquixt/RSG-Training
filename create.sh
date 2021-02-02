#!/bin/bash

mkdir $1

cp -r tf/ $1

cp -r trainers/ $1

cp -r engine/ $1

cp -r js/ $1

cp main.py $1
