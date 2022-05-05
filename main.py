import os
import time
from colorama import Fore
import platform
import subprocess
from src.config.exp_constants import EXP_FLAGS


def main():
    rootTime = time.time()
    expCount = 0
    print(Fore.BLUE + "Running experiments.")
    for exp in EXP_FLAGS:
        if exp in os.environ:
            print(Fore.GREEN + "\n\n\n=============================================")
            print(Fore.GREEN + "Found experiment %s. Launching" % exp)
            startTime = time.time()
            EXP_FLAGS[exp].configure(**os.environ)
            EXP_FLAGS[exp].run()
            print(Fore.GREEN + "Experiment %s ended successfully. (Runtime %.2f)" % (exp, time.time() - startTime))
            print(Fore.GREEN + "=============================================\n\n\n")
            expCount += 1

    print(Fore.BLUE + "Ran %d experiments in %.2f seconds." % (expCount, time.time() - rootTime))


def build_proto():
    args = ("./resources/protoc_win/protoc.exe", "-I=./resources/protobufs", "--python_out=.", "./resources/protobufs/*")
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    print(output)


if __name__ == "__main__":
    if platform.system() == 'Windows':
        build_proto()
    main()
