from tfprocess import TFProcess
import argparse
from parse import RAM_BATCH_SIZE, BATCH_SIZE

def main():
    parser = argparse.ArgumentParser(
        description='Init random network.')
    parser.add_argument("--blocks", '-b',
        help="Number of blocks", type=int)
    parser.add_argument("--filters", '-f',
        help="Number of filters", type=int)
    parser.add_argument("--logbase", default='leelalogs', type=str,
        help="Log file prefix (for tensorboard) (default: %(default)s)")
    args = parser.parse_args()
    blocks = args.blocks
    filters = args.filters

    tf = TFProcess(blocks, filters)
    tf.init(RAM_BATCH_SIZE, logbase=args.logbase, macrobatch=BATCH_SIZE // RAM_BATCH_SIZE)

    tf.init_random_weights()

if __name__ == '__main__':
    main()

