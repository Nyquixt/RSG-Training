import os
import shutil
if ('test' in os.listdir('.')):
    shutil.rmtree('test')
os.system('./create.sh test')
os.system('cd test')
os.system('/home/ai-lab/anaconda3/bin/activate tf')
os.system('python3 main.py')