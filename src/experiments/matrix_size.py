import random

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

        xvals, yvals, results, m0_s, m1_s = self.benchmark_multiplication(False, True)
        self.plot_results(xvals, yvals, results, m0_s, m1_s, "Matrix Column Size")

        self.START_COL_SIZE = 20000
        self.START_ROW_SIZE = 10000
        self.INC_Y = 10000
        self.INC_X = 10000
        xvals, yvals, results, m0_s, m1_s = self.benchmark_multiplication(True, False)
        self.plot_results(xvals, yvals, results, m0_s, m1_s, "Matrix Row Size")

        self.START_COL_SIZE = 10000
        self.START_ROW_SIZE = 10000
        self.INC_Y = 5000
        self.INC_X = 5000
        xvals, yvals, results, m0_s, m1_s = self.benchmark_multiplication(True, True)
        self.plot_results(xvals, yvals, results, m0_s, m1_s, "Matrix Size")

    @staticmethod
    def plot_results(xvals, yvals, results, m0_s, m1_s, xlabel):
        fig, ax1 = plt.subplots(figsize=(7, 5))
        ax1.plot(range(len(yvals)), results, color='brown')
        ax1.tick_params(axis='y', labelcolor='brown')
        ax1.set_xticks(range(len(yvals)))
        ax1.set_xticklabels(["%dK" % int(x/1000) for x in yvals], rotation=40)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel("Seconds to multiply")
        ax1.set_title("Multiplication time for two matrices")
        ax1.legend(['Multiplication Seconds'])
        ax2 = ax1.twinx()
        color = 'royalblue'
        ax2.bar([x - 1/len(yvals) for x in range(len(yvals))], m0_s, color=color, width=0.25, alpha=0.5)
        ax2.bar([x + 1/len(yvals) for x in range(len(yvals))], m1_s, color='lightsteelblue', width=0.25, alpha=0.5)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylabel("Matrix sparsity (0 value counts)")
        ax2.legend(['M1 Sparsity', 'M2 Sparsity'])
        print(xvals)
        print(yvals)
        print(results)
        print(m0_s)
        print(m1_s)
        fig.show()

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
                m0, m1, z0, z1 = self.generate_matrix()
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

        m0_z = self.randomize(m0)
        m1_z = self.randomize(m1)

        return m0, m1, m0_z, m1_z

    def randomize(self, m):
        z_count = np.random.randint(0, 1000)
        for _ in range(z_count):
            i = np.random.randint(0, self.START_ROW_SIZE)
            j = np.random.randint(0, self.START_COL_SIZE)
            m[i][j] = 0

        return z_count

    def benchmark_multiplication(self, scaleX, scaleY):
        xvals = []
        yvals = []
        m0_sparsity = []
        m1_sparsity = []
        results = []

        while True:

            startTime = time.time()
            m0, m1, z0, z1 = self.generate_matrix()
            print(Fore.CYAN + "Generated %dx%d matrix in %.2f seconds" %
                  (self.START_COL_SIZE, self.START_ROW_SIZE, time.time() - startTime))
            startTime = time.time()

            np.multiply(m0, m1)
            results.append(time.time() - startTime)
            print(Fore.CYAN + "Multiplied %dx%d matrix in %.2f seconds" %
                  (self.START_COL_SIZE, self.START_ROW_SIZE, results[-1]))
            m0_sparsity.append(z0)
            m1_sparsity.append(z1)

            xvals.append(self.START_ROW_SIZE)
            yvals.append(self.START_COL_SIZE)

            if results[-1] >= self.TARGET_TIME:
                break
            else:
                if scaleY:
                    self.START_COL_SIZE += self.INC_Y
                if scaleX:
                    self.START_ROW_SIZE += self.INC_X
        return xvals, yvals, results, m0_sparsity, m1_sparsity
