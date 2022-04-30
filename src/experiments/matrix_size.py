from src.experiments import Experiment

import time
import numpy as np
import matplotlib.pyplot as plt

from colorama import Fore


class MatrixSizeExperiment(Experiment):
    """
    For X=Y scaling, 10K x 10K with 5K scaling works great
    For Y/X only scaling, 10K x 20K with 10K scaling works great

    Finding 1: Matrix dimensions are not really important. As long as the amount of data is the same,
    if the matrix is bigger on X or Y is relevant.

    Finding 2: Sparsity of the matrix does not affect multiplication time at all, as long as we dont change
    the algorithm. Since we are talking about rather short multiplication times in any scenario, running a
    sparsity test will delay the process rather than provide an advantage. 0 multiplications, even if optimized
    by numpy, don't present a problem for PoX time assumptions

    ~~TODO: Experiment with different kinds of numbers as well as precision.
    Ideally, this experiment produces a bar plot showing various numbers ([0, 1], [-1,1], [0, +1M],[-1M,+1M])
    across 2 or 3 levels of precision (full precision, rounded to 5 digits, to 2 and to 0). Using normally
    distributed numbers will do.~~
    DONE


    Finding 3: All of the above are computed for np.multiply. For np.dot, things get different
    For X=Y scaling, 5K x 5K with 1K scaling works great
    For X only scaling (increase in row size), the time grows linearly. Ran with 5K x 10K and 5K increase
    For Y only scaling (increase in col size), the timg grows as for X=Y.

    Finding 1: It seems that matrices that are have more columns than rows (are wider), work faster.
    Finding 2: Sparsity still doesn't really change anything
    """

    START_COL_SIZE = 10000
    START_ROW_SIZE = 10000

    INC_X = 5000
    INC_Y = 5000

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
        self.plot_results(xvals, yvals, results, m0_s, m1_s, "Matrix Size (row)")

        self.START_COL_SIZE = 5000
        self.START_ROW_SIZE = 5000
        self.INC_Y = 5000
        self.INC_X = 5000
        xvals, yvals, results, m0_s, m1_s = self.benchmark_multiplication(True, False)
        self.plot_results(xvals, yvals, results, m0_s, m1_s, "Matrix Size (column)")

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
        This is used to serialize a number of exercises to benchmark multiplication on later.
        In first iterations, an optimal matrix size was found, and this function can now be used
        to benchmark impact of sparsity and disk throughput
        :return:
        """
        print(Fore.CYAN + "Generating exercises.")
        for count in range(0, 10):
            i = 0
            m0, m1, z0, z1 = self.generate_matrix()
            print(Fore.CYAN + "Generated %dx%d matrix." % (self.START_COL_SIZE, self.START_ROW_SIZE))
            for m in [m0, m1]:
                with open("../resources/poxsamples_dot/%s%dx%d_%d_1M_%d.dat" %
                          (self.PREGENERATED_FILE, self.START_COL_SIZE, self.START_ROW_SIZE, i, count), "wb") as f:
                    f.write(m.tobytes())
                    print(Fore.CYAN + "Wrote matrix m%d" % i)
                    i += 1

    def generate_matrix(self):
        if self.START_COL_SIZE == self.START_ROW_SIZE:
            m0 = np.random.normal(1000000, 400000, [self.START_ROW_SIZE, self.START_COL_SIZE])
            m1 = np.random.normal(1000000, 400000, [self.START_ROW_SIZE, self.START_COL_SIZE])
            # m0 = np.random.randn(self.START_ROW_SIZE, self.START_COL_SIZE)
            # m1 = np.random.randn(self.START_ROW_SIZE, self.START_COL_SIZE)
        else:
            m0 = np.random.randn(self.START_ROW_SIZE, self.START_COL_SIZE)
            m1 = np.random.randn(self.START_COL_SIZE, self.START_ROW_SIZE)

        m0_z = self.randomize(m0)
        m1_z = self.randomize(m1)

        return m0, m1, m0_z, m1_z

    def randomize(self, m):
        z_count = np.random.randint(0, 1000)
        for _ in range(z_count):
            i = np.random.randint(0, len(m))
            j = np.random.randint(0, len(m[0]))
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

            np.dot(m0, m1)
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
