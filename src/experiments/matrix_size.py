from src.experiments import Experiment

import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt

from colorama import Fore


class MatrixSizeExperiment(Experiment):
    """
    For X=Y scaling, 10K x 10K with 5K scaling works great
    For Y/X only scaling, 10K x 20K with 10K scaling works great
    """

    START_COL_SIZE = 20000
    START_ROW_SIZE = 10000

    INC_X = 10000
    INC_Y = 10000

    TARGET_TIME = 10

    RESULTS = []

    PREGENERATED_FILE = "generated_mat"

    PREGENERATION = False

    def __init__(self):
        super().__init__()

    def run(self):
        if self.PREGENERATION:
            return

        xvals, yvals, results = self.benchmark_multiplication(False, True)
        plt.figure(1, (7, 5))
        plt.plot(yvals, results)
        plt.xlabel("Matrix Column Size")
        plt.ylabel("Seconds to multiply")
        plt.title("Multiplication time for two matrices")
        print(xvals)
        print(yvals)
        print(results)
        plt.show()

    def configure(self, **kwargs):
        if 'START_ROW_SIZE' in kwargs:
            self.START_ROW_SIZE = kwargs['START_ROW_SIZE']
        if 'START_COL_SIZE' in kwargs:
            self.START_COL_SIZE = kwargs['START_COL_SIZE']
        if 'INC_X' in kwargs:
            self.INC_X = kwargs['INC_X']
        if 'INC_Y' in kwargs:
            self.INC_Y = kwargs['INC_Y']
        if 'TARGET_TIME' in kwargs:
            self.TARGET_TIME = kwargs['TARGET_TIME']

        print(Fore.CYAN + "Running matrix multiplication experiment with %dx%d start size, incrementing by %d;%d."
                          " Target time: %d" % (self.START_COL_SIZE, self.START_ROW_SIZE,
                                                self.INC_X, self.INC_Y,
                                                self.TARGET_TIME))
        if 'PREGENERATE' in kwargs:
            self.PREGENERATION = True
            self.pregenerate_matrix()

    def pregenerate_matrix(self):
        """
        Does not work as is. Serialization of huge matrices needs to be heavily optimized.
        As it is, 10K x 10K matrices take about 3.85 Gb and ~20 seconds to serialize.
        They get multiplied in 0.16 seconds.
        :return:
        """
        if len([x for x in os.listdir() if self.PREGENERATED_FILE in x]) > 0:
            print(Fore.CYAN + "Found pregenerated file.")
        else:
            print(Fore.CYAN + "No pregenerated file found. Generating.")
            matrices = {}
            for i in range(10):
                m0, m1 = self.generate_matrix()
                matrices['m0'] = m0.tolist()
                matrices['m1'] = m1.tolist()
                matrices['dimX'] = self.START_COL_SIZE
                matrices['dimY'] = self.START_ROW_SIZE
                matrices['sparsityM0'] = np.count_nonzero(m0 == 0)
                matrices['sparsityM1'] = np.count_nonzero(m1 == 0)
                print(Fore.CYAN + "Generated %dx%d matrix." % (self.START_COL_SIZE, self.START_ROW_SIZE))
                self.START_COL_SIZE += self.INC_Y
                self.START_ROW_SIZE += self.INC_X
                with open("%s%d.txt" % (self.PREGENERATED_FILE, i), "wb") as f:
                    json.dump(matrices, f)

    def generate_matrix(self):
        m0 = np.random.rand(self.START_ROW_SIZE, self.START_COL_SIZE)
        m1 = np.random.rand(self.START_ROW_SIZE, self.START_COL_SIZE)
        return m0, m1

    def benchmark_multiplication(self, scaleX, scaleY):
        xvals = []
        yvals = []
        results = []

        while True:

            startTime = time.time()
            m0, m1 = self.generate_matrix()
            print(Fore.CYAN + "Generated %dx%d matrix in %.2f seconds" %
                  (self.START_COL_SIZE, self.START_ROW_SIZE, time.time() - startTime))
            startTime = time.time()

            np.multiply(m0, m1)
            results.append(time.time() - startTime)
            print(Fore.CYAN + "Multiplied %dx%d matrix in %.2f seconds" %
                  (self.START_COL_SIZE, self.START_ROW_SIZE, results[-1]))

            xvals.append(self.START_ROW_SIZE)
            yvals.append(self.START_COL_SIZE)

            if results[-1] >= self.TARGET_TIME:
                break
            else:
                if scaleY:
                    self.START_COL_SIZE += self.INC_Y
                if scaleX:
                    self.START_ROW_SIZE += self.INC_X
        return xvals, yvals, results
