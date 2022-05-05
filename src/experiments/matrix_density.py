from src.experiments import Experiment

import time
import numpy as np
import matplotlib.pyplot as plt
import os
import json

from colorama import Fore


class MatrixDensityExperiment(Experiment):
    """
    This experiment essentially confirms that at CPU level, 0 multiplications don't change anything.

    It also shows that numpy does not do any out of the box optimization. even a dot on two completely 0-element
    matrices still takes about as long as a randomly initialized matrix
    """
    PREGENERATED_FILE_PREFIX = "generated_mat"
    PREGENERATED_DIR = "./resources/poxsamples_dot"

    MATRICE_PATHS = {
        '1M': {
            '0': [],
            '1': []
        },
        '-1M': {
            '0': [],
            '1': []
        },
        'randn': {
            '0': [],
            '1': []
        }
    }

    def __init__(self):
        super().__init__()

    def run(self):
        # Verify BLAS linkage
        np.show_config()
        # self.run_base_multiplication()
        self.run_sparsity_checker()

    def run_sparsity_checker(self):
        results = {
            '1M': [],
            '-1M': [],
            'randn': []
        }
        for mtype in self.MATRICE_PATHS:
            print(Fore.CYAN + "Benchmarking %s type matrices..." % mtype)
            m0, m1 = self.load_matrices(self.MATRICE_PATHS[mtype]['0'][0], self.MATRICE_PATHS[mtype]['1'][0])
            results[mtype].append(self.benchmark_multiplication(m0, m1, mtype))
            bucket_size = 20
            for i in range(bucket_size):
                print(Fore.CYAN + "Benchmarking %d/%d zero rows..." % (i + 1, bucket_size))
                for j in range(int(i * len(m0) / bucket_size), int((i + 1) * len(m0) / bucket_size)):
                    m0[j] = 0
                    m1[j] = 0
                results[mtype].append(self.benchmark_multiplication(m0, m1, mtype))

        print(Fore.CYAN + "Benchmark complete: %s" % json.dumps(results, indent=4))
        self.plot_density_results(results)

    def run_base_multiplication(self):
        results = {
            '1M': [],
            '-1M': [],
            'randn': []
        }
        for mtype in self.MATRICE_PATHS:
            print(Fore.CYAN + "Benchmarking %s type matrices..." % mtype)
            for index in range(len(self.MATRICE_PATHS[mtype]['0'])):
                m0, m1 = self.load_matrices(self.MATRICE_PATHS[mtype]['0'][index],
                                            self.MATRICE_PATHS[mtype]['1'][index])
                results[mtype].append(self.benchmark_multiplication(m0, m1, mtype))
            print(Fore.CYAN + "Benchmark for %s done." % mtype)

        print(Fore.CYAN + "Benchmark complete: %s" % json.dumps(results, indent=4))
        self.plot_results(results)

    @staticmethod
    def load_matrices(m0Path, m1Path):
        matrices = []

        for path in [m0Path, m1Path]:
            print(Fore.CYAN + "Loading matrix %s..." % path)
            with open(path, "rb") as in_f:
                m0_buf = in_f.read()
                print(Fore.CYAN + "Constructing...")
                m0 = np.frombuffer(m0_buf).reshape([10000, 10000])
                matrices.append(m0)
                print(Fore.CYAN + "Done.")
        print(Fore.CYAN + "Exercise loaded.")

        # NP went completely nuts and doesn't let you change the writeable flag on frombuffer loaded data
        return np.copy(matrices[0]), np.copy(matrices[1])

    @staticmethod
    def plot_results(results):
        # results = {
        #     "1M": [
        #         4.387004852294922,
        #         3.5850040912628174,
        #         3.612001657485962,
        #         3.38200306892395,
        #         3.3770041465759277,
        #         3.2900030612945557,
        #         4.071504831314087,
        #         3.638505458831787,
        #         3.8195018768310547,
        #         3.6690030097961426
        #     ],
        #     "-1M": [
        #         3.807501792907715,
        #         3.6990020275115967,
        #         3.773003578186035,
        #         3.822003126144409,
        #         3.757502794265747,
        #         3.556499719619751,
        #         3.805501699447632,
        #         3.6050028800964355,
        #         3.772500991821289,
        #         3.771002769470215
        #     ],
        #     "randn": [
        #         3.8295035362243652,
        #         4.0550007820129395,
        #         4.006001710891724,
        #         3.8825016021728516,
        #         3.770002603530884,
        #         3.645502805709839,
        #         3.825003147125244,
        #         3.7170028686523438,
        #         3.91050386428833,
        #         4.011003017425537
        #     ]
        # }
        fig, ax1 = plt.subplots(figsize=(7, 5))
        ax1.bar(range(len(results.keys())), [np.max(results[x]) for x in results.keys()], color='royalblue')
        ax1.bar(range(len(results.keys())), [np.average(results[x]) for x in results.keys()], color='cornflowerblue')
        ax1.bar(range(len(results.keys())), [np.min(results[x]) for x in results.keys()], color='lightsteelblue')
        ax1.set_xticks(range(len(results.keys())))
        ax1.set_xticklabels(results.keys())
        ax1.set_ylabel("Seconds to multiply (average)")
        ax1.set_title("Multiplication time for two matrices ")
        fig.show()

    @staticmethod
    def plot_density_results(results):
        fig, ax1 = plt.subplots(figsize=(7, 5))
        ax1.plot(range(len(results['1M'])), results['1M'], color='royalblue')
        ax1.plot(range(len(results['-1M'])), results['-1M'], color='cornflowerblue')
        ax1.plot(range(len(results['randn'])), results['randn'], color='lightsteelblue')
        ax1.set_ylabel("Seconds to multiply")
        ax1.set_xticks(range(len(results['1M'])))  # 1M, -1M, randn have the same length
        ax1.set_xticklabels(["%d/%d" % (i, len(results['1M']) - 1) for i in range(len(results['1M']))], rotation=35)
        ax1.set_xlabel("Number of zero-value rows (x4000)")
        ax1.set_title("Multiplication time for two matrices increasing in sparsity")
        ax1.legend(['1M', '-1M', 'randn'])
        fig.show()

    def configure(self, **kwargs):
        if 'PREGENERATED_FILE_PREFIX' in kwargs:
            self.PREGENERATED_FILE_PREFIX = kwargs['PREGENERATED_FILE_PREFIX']
        if 'PREGENERATED_DIR' in kwargs:
            self.PREGENERATED_DIR = kwargs['PREGENERATED_DIR']

        for file in os.listdir(self.PREGENERATED_DIR):
            if file.startswith(self.PREGENERATED_FILE_PREFIX):
                fpath = os.path.join(self.PREGENERATED_DIR, file)
                if os.path.isfile(fpath):
                    tokens = file.split('_')
                    self.MATRICE_PATHS[tokens[-2]][tokens[-3]].append(fpath)

        print(Fore.CYAN + "Loaded matrices: %s" % json.dumps(self.MATRICE_PATHS, indent=4))

    def benchmark_multiplication(self, m0, m1, mtype):
        startTime = time.time()
        np.dot(m0, m1)
        totalTime = time.time() - startTime

        print(Fore.CYAN + "Multiplied %dx%d (%s) matrix in %.2f seconds" %
              (m0.shape[0], m0.shape[1], mtype, totalTime))
        return totalTime
