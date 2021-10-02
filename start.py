from time import sleep
import sys
from subprocess import call
from argparse import ArgumentParser
PATH = '/rosreestr-ownership-parser/'


def createParser():
    parser = ArgumentParser()
    parser.add_argument('-i', '--id', default=0)
    namespace = parser.parse_args(sys.argv[1:])
    return namespace

namespace = createParser()
ID = str(namespace.id)
while True:
    answer  = call(['php '+PATH+'ir_egrn_create.php' +' '+ID], shell=True)
    print("SLEEP 600 2")
    sleep(600)

