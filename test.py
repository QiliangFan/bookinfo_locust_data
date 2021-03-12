import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--c", type=bool)
config = vars(argparser.parse_args())
print(config)