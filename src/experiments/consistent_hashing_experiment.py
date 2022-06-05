import random
import time

import base58
import binascii
import ecdsa
import hashlib
import matplotlib.pyplot as plt
import numpy as np
from arweave import Wallet
from arweave.arweave_lib import arql

from uhashring import HashRing
from colorama import Fore

from pytrie import StringTrie

from src.experiments import Experiment


class ConsistentHashExp(Experiment):
    """
    Finding1: Using a bitcoin-like address derivation method, consistent hashing the keys to a sufficiently large ring
    is very, very good in terms of coverage: [920, 1082, 1099, 902, 1033, 1082, 1097, 955, 952, 878] (ideal is 1000)
    """

    PB_KEY_COUNT = 10000
    PB_KEY_MIN = 10
    PB_KEY_MAX = 1000

    ARWEAVE_WALLET_DOWN = './resources/ar_wallet_download.json'
    TX_EXAMPLES = []

    HASH_RING = None

    def __init__(self):
        super().__init__()

    def run(self):
        # self.run_overtake_prob()
        self.plot_attacker_size([], [])

    def run_overtake_prob(self):
        attacker_size = 500
        buckets = 10
        key_count = 1_000
        transactions = 100
        self.create_hashring(buckets)

        print(Fore.CYAN + "Generating keys...")
        keys = self.generate_keys(key_count)
        exercises = self.generate_tx(buckets, transactions)
        print(Fore.CYAN + "Generated %d keys..." % key_count)

        xvals = []
        results = []
        blocks = 1000
        for i in range(blocks):
            self.create_hashring(buckets)
            load, bh = self.hash_keys(keys, buckets)
            attacker_load = self.get_attacker_load(load, keys[:attacker_size])
            validation_load = self.get_validation_load(attacker_load, exercises, bh)
            xvals.append(i)
            results.append(max(validation_load))
            if i % 100 == 0:
                print(Fore.CYAN + "Computed block %d/%d" % (i, blocks))
        print(Fore.CYAN + "Computed attacker distribution: ", results)
        self.plot_attacker_size(xvals, results)

    def get_validation_load(self, attacker_load, exercises, bh):
        self.create_hashring(5)

        exercise_groups = dict()
        for group in range(len(exercises)):
            exercise_groups[group] = set()
            for ex in exercises[group]:
                solution = hashlib.sha256(bytes(str(group) + ex + str(random.randint(-1000, 1000)), 'utf-8')).hexdigest()
                exercise_groups[group].add(self.get_bucket(bh + ex + solution))

        attacker_coverages = []
        for group in range(len(attacker_load)):
            # For every attacker node in this group
            for _ in attacker_load[group]:

                # Find how many other attackers nodes this attacker can ask validation from
                attacker_reach = 0
                for validator_key in attacker_load[group]:
                    validator_egroup = self.get_bucket(bh + validator_key)
                    if validator_egroup in exercise_groups[group]:
                        attacker_reach += 1
                attacker_coverages.append(attacker_reach)

        return attacker_coverages

    @staticmethod
    def get_attacker_load(load, attacker_keys):
        attacker_load = dict()
        for group in range(len(load)):
            keys = [k for k in attacker_keys if k in load[group]]
            attacker_load[group] = keys
        return attacker_load

    @staticmethod
    def plot_attacker_size(xvals, results):
        results = [63, 60, 57, 58, 53, 60, 57, 55, 67, 60, 73, 66, 58, 59, 67, 61, 60, 63, 70, 58, 60, 63, 66, 57, 64, 62, 60, 62, 64, 66, 61, 60, 63, 61, 63, 71, 70, 57, 62, 62, 71, 58, 63, 83, 50, 59, 63, 63, 66, 59, 58, 66, 56, 52, 55, 62, 63, 71, 64, 57, 63, 61, 68, 64, 66, 60, 62, 60, 75, 63, 63, 54, 58, 58, 60, 59, 62, 56, 58, 63, 61, 61, 63, 63, 64, 63, 60, 64, 61, 58, 64, 63, 58, 64, 59, 66, 55, 61, 69, 59, 66, 67, 55, 68, 74, 58, 55, 62, 56, 66, 65, 65, 73, 60, 65, 61, 68, 65, 64, 57, 64, 59, 56, 63, 64, 60, 65, 57, 68, 64, 71, 60, 61, 70, 62, 59, 56, 64, 52, 62, 64, 58, 62, 55, 54, 67, 63, 58, 57, 58, 58, 60, 62, 72, 61, 59, 59, 68, 64, 70, 55, 65, 58, 56, 70, 59, 71, 57, 66, 66, 55, 66, 64, 62, 59, 63, 58, 60, 71, 60, 61, 67, 57, 63, 62, 58, 67, 58, 58, 58, 63, 66, 72, 72, 63, 68, 60, 68, 67, 57, 62, 65, 64, 62, 59, 60, 63, 63, 59, 60, 65, 65, 62, 61, 68, 53, 58, 62, 63, 62, 60, 59, 61, 55, 60, 60, 61, 59, 61, 57, 58, 59, 71, 63, 60, 58, 70, 61, 58, 65, 60, 62, 58, 64, 57, 59, 62, 56, 60, 61, 58, 59, 65, 63, 67, 55, 61, 61, 58, 56, 56, 62, 67, 65, 63, 66, 64, 67, 59, 63, 61, 65, 61, 63, 60, 64, 58, 56, 64, 58, 65, 61, 66, 58, 60, 59, 61, 65, 62, 66, 64, 70, 56, 60, 60, 56, 59, 65, 56, 60, 64, 63, 70, 72, 66, 53, 60, 63, 59, 56, 56, 61, 69, 65, 60, 67, 62, 65, 66, 61, 61, 70, 59, 56, 60, 62, 69, 60, 59, 55, 59, 74, 67, 64, 68, 63, 62, 57, 60, 67, 67, 55, 58, 58, 70, 60, 64, 66, 62, 56, 66, 59, 54, 53, 65, 64, 58, 64, 66, 54, 71, 61, 60, 65, 63, 59, 66, 75, 54, 60, 61, 61, 60, 64, 68, 56, 69, 58, 64, 61, 63, 67, 54, 64, 58, 64, 54, 61, 56, 64, 56, 55, 56, 70, 65, 65, 60, 63, 61, 61, 63, 62, 55, 60, 66, 64, 56, 52, 69, 66, 58, 59, 62, 71, 66, 63, 56, 58, 61, 75, 60, 67, 55, 63, 62, 60, 65, 61, 61, 59, 59, 63, 74, 54, 61, 62, 61, 60, 58, 55, 69, 76, 61, 65, 68, 58, 62, 65, 56, 65, 66, 58, 60, 68, 60, 61, 57, 61, 64, 65, 58, 65, 59, 65, 58, 69, 70, 57, 58, 60, 75, 60, 67, 55, 62, 61, 57, 54, 56, 62, 62, 59, 62, 64, 66, 68, 70, 68, 64, 62, 59, 68, 63, 59, 59, 73, 60, 69, 57, 54, 66, 59, 57, 61, 56, 61, 59, 70, 64, 60, 63, 52, 65, 58, 65, 60, 61, 60, 56, 56, 64, 62, 61, 62, 65, 60, 60, 59, 62, 66, 65, 57, 63, 66, 59, 58, 61, 63, 70, 48, 53, 71, 64, 59, 68, 58, 70, 61, 60, 55, 60, 56, 61, 68, 55, 63, 67, 61, 67, 63, 62, 65, 65, 70, 71, 60, 61, 70, 63, 55, 61, 64, 64, 72, 56, 60, 70, 64, 58, 65, 56, 60, 66, 61, 65, 65, 69, 62, 59, 64, 57, 67, 58, 59, 57, 58, 63, 64, 57, 66, 55, 63, 64, 59, 62, 70, 61, 63, 67, 67, 61, 57, 72, 65, 57, 54, 67, 69, 59, 61, 56, 60, 53, 61, 60, 69, 60, 60, 65, 62, 74, 65, 64, 63, 63, 61, 57, 60, 61, 64, 58, 71, 64, 60, 66, 61, 64, 55, 64, 66, 56, 62, 62, 87, 58, 58, 63, 61, 60, 68, 69, 60, 60, 62, 66, 58, 56, 62, 58, 64, 61, 62, 59, 59, 60, 56, 61, 59, 63, 58, 67, 60, 55, 64, 61, 50, 54, 61, 65, 56, 61, 65, 64, 70, 64, 62, 66, 62, 70, 64, 65, 68, 60, 65, 56, 59, 66, 61, 70, 60, 61, 68, 56, 65, 67, 68, 62, 65, 63, 63, 54, 60, 51, 60, 64, 64, 61, 60, 56, 60, 61, 63, 64, 59, 68, 58, 59, 61, 58, 63, 67, 68, 63, 69, 55, 59, 61, 60, 71, 72, 61, 58, 63, 62, 63, 58, 64, 61, 62, 62, 64, 65, 62, 67, 59, 56, 69, 64, 60, 62, 62, 69, 63, 61, 64, 57, 64, 65, 60, 54, 70, 59, 57, 59, 58, 58, 72, 63, 60, 62, 64, 61, 61, 61, 56, 64, 62, 67, 61, 64, 56, 64, 57, 64, 60, 55, 59, 64, 65, 65, 63, 61, 68, 59, 66, 57, 59, 66, 58, 61, 62, 63, 63, 58, 62, 67, 59, 52, 61, 62, 60, 59, 72, 63, 69, 64, 59, 59, 62, 66, 67, 62, 63, 55, 57, 58, 54, 63, 61, 51, 65, 56, 57, 58, 64, 64, 62, 59, 67, 54, 70, 62, 61, 61, 62, 57, 60, 64, 65, 67, 57, 65, 56, 64, 70, 67, 61, 63, 57, 61, 63, 62, 64, 62, 56, 60, 65, 59, 65, 69, 69, 55, 65, 66, 64, 60, 67, 72, 61, 60, 54, 68, 74, 65, 77, 54, 65, 60, 67, 61, 56, 63, 71, 63, 64, 63, 60, 75, 59, 60, 63, 55, 62, 66, 65, 59, 65, 56, 65, 54, 63, 62, 72, 71, 60, 60, 58, 65, 64, 60, 57, 58, 59, 55, 58, 61, 67, 65, 67, 65, 61, 63, 53, 61, 58, 56, 60, 60, 67, 66, 59, 63, 59, 59, 57, 58, 64, 57, 65, 66, 68, 59, 72, 68, 55, 68, 55, 67, 61, 61, 59, 64, 61, 59, 60, 54, 65, 61, 60, 65, 68, 53, 62, 58, 63, 66, 61, 62, 64, 56]
        xvals = range(len(results))
        fig, ax = plt.subplots()
        ax.plot(xvals, results, color='royalblue')
        ax.set_title("Maximum number of colluding attacker nodes in the same group")
        ax.set_xlabel("Block number")
        ax.set_ylabel("Number of attacker nodes in one group")
        for i in range(len(results) - 1):
            if results[i] > 70 and results[i+1] > 70:
                ax.axvline(i, color='red')
        ax.legend(['colluding nodes', 'can overtake'])
        fig.show()

    def run_trie_benchmark(self):
        results = []
        actual_size = []
        xvals = []
        total = 50000
        for i in range(1000, total, 1000):
            startTime = time.time()
            hashes = [''.join([chr(x) for x in hashlib.sha256(bytes(str(j) + "hash stringer", 'utf-8')).digest()])
                      for j in range(i)]
            print(Fore.CYAN + "Computed hashes for %d/%d entries in %.2fs." % (i, total, time.time() - startTime))
            trie = StringTrie.fromkeys(hashes)
            results.append(self.compute_trie_size(trie._root) / 1024 / 1024)
            xvals.append(i)
            actual_size.append(32 * len(hashes) / 1024 / 1024)

        print(xvals)
        print(results)
        print(actual_size)
        self.plot_trie_sizes(xvals, results, actual_size)

    def compute_trie_size(self, node):
        size = 0
        ptr_size = 4

        if len(node.children.keys()) == 0:
            return 1  # 1 byte for array termination marker.

        for key in node.children:
            size += self.compute_trie_size(node.children[key])

        return size + ptr_size * len(node.children.keys())

    @staticmethod
    def plot_trie_sizes(xvals, results, actual_size):
        fig, ax = plt.subplots()
        ax.plot(xvals, results, color='royalblue')
        ax.plot(xvals, actual_size, color='cornflowerblue')
        ax.set_title("Memory required based on the number of matrices (megabytes)")
        ax.set_xlabel("Number of unique exercises")
        ax.set_ylabel("Size of trie structure (megabytes)")
        ax.legend(['trie size', 'hash list size'])
        fig.show()

    def run_tx_deviation(self):
        txs = 10
        x = []
        ymean = []
        ystd = []
        ydiff = []
        ymin = []
        ymax = []
        while txs < 200:
            mean, std, mmax, mmin = self.compute_tx_stats(txs)
            x.append(txs)
            ymean.append(mean)
            ystd.append(std)
            ydiff.append(mmax - mmin)
            ymin.append(mmin)
            ymax.append(mmax)
            txs += 10
            if txs % 1000 == 0:
                print(Fore.CYAN + "Computed deviation for %d/%d txs" % (txs, len(self.TX_EXAMPLES)))
        print(Fore.CYAN + "Mean: ", ymean)
        print(Fore.CYAN + "Std: ", ystd)
        print(Fore.CYAN + "Diff: ", ydiff)

        fig, ax = plt.subplots()
        ax.plot(x, ymean, color='cornflowerblue')
        ax.plot(x, ystd, color='royalblue')
        # ax.plot(x, ydiff, color='rosybrown')
        ax.bar([p + 1 for p in x], ymin, color='indianred')
        ax.bar([p - 1 for p in x], ymax, color='brown')
        ax.set_title("Avg. and Std. Dev. of bucket load for exercises (10 buckets)")
        ax.set_xlabel("Number of exercises (network load)")
        ax.set_ylabel("Avg & dev on 10 buckets")
        ax.legend(['average', 'std. dev.', 'max', 'min'])
        fig.show()

    def run_pb_deviation(self):
        pubkeys = self.PB_KEY_MIN
        x = []
        ymean = []
        ystd = []
        ydiff = []
        while pubkeys < self.PB_KEY_MAX:
            mean, std, diff = self.compute_pb_stats(pubkeys)
            x.append(pubkeys)
            ymean.append(mean)
            ystd.append(std)
            ydiff.append(diff)
            pubkeys += 100
            print(Fore.CYAN + "Computed deviation for %d/%d pubkeys" % (pubkeys, self.PB_KEY_MAX))
        print(Fore.CYAN + "Done!")
        print(Fore.CYAN + "Mean: ", ymean)
        print(Fore.CYAN + "Std: ", ystd)
        print(Fore.CYAN + "Diff: ", ydiff)

        # Precomputed results with PB_KEY_MAX = 10000
        # x = range(10, self.PB_KEY_MAX + 10, 100)
        # ymean = [1.0, 11.0, 21.0, 31.0, 41.0, 51.0, 61.0, 71.0, 81.0, 91.0, 101.0, 111.0, 121.0, 131.0, 141.0, 151.0,
        #          161.0, 171.0, 181.0, 191.0, 201.0, 211.0, 221.0, 231.0, 241.0, 251.0, 261.0, 271.0, 281.0, 291.0,
        #          301.0, 311.0, 321.0, 331.0, 341.0, 351.0, 361.0, 371.0, 381.0, 391.0, 401.0, 411.0, 421.0, 431.0,
        #          441.0, 451.0, 461.0, 471.0, 481.0, 491.0, 501.0, 511.0, 521.0, 531.0, 541.0, 551.0, 561.0, 571.0,
        #          581.0, 591.0, 601.0, 611.0, 621.0, 631.0, 641.0, 651.0, 661.0, 671.0, 681.0, 691.0, 701.0, 711.0,
        #          721.0, 731.0, 741.0, 751.0, 761.0, 771.0, 781.0, 791.0, 801.0, 811.0, 821.0, 831.0, 841.0, 851.0,
        #          861.0, 871.0, 881.0, 891.0, 901.0, 911.0, 921.0, 931.0, 941.0, 951.0, 961.0, 971.0, 981.0, 991.0]
        # ystd = [0.7745966692414834, 3.3466401061363023, 7.771743691090179, 6.928203230275509, 9.612491872558333,
        #         5.477225575051661, 10.611314715905847, 4.538722287164087, 11.515207336387824, 11.730302638892145,
        #         11.696153213770756, 12.00833044182246, 17.35511451993331, 19.313207915827967, 12.165525060596439,
        #         11.16243700990066, 23.01303978182804, 19.834313701260246, 20.813457185196313, 19.115438786488788,
        #         16.229602582934678, 22.181073012818835, 26.290682760247975, 21.203773249117717, 23.630488780387086,
        #         30.78311225331188, 17.326280616450838, 32.526911934581186, 24.53161225847172, 22.47665455533808,
        #         33.24154027718932, 28.684490582891655, 28.035691537752374, 18.504053609952603, 29.604053776467843,
        #         36.149688795340964, 31.11591232793922, 36.18839593018734, 31.317726609701413, 50.82322303829225,
        #         44.73253849269008, 47.11475352795555, 29.165047574108293, 57.0087712549569, 45.9782557302906,
        #         32.890728176797786, 40.43760625952036, 36.47464873031679, 57.26779199515204, 50.85272854036448,
        #         49.957982345166826, 42.558195450465234, 34.50507209092599, 48.879443532020694, 43.278170016764804,
        #         35.59213396243614, 46.89136381040756, 68.48211445333737, 47.795397267937844, 61.144092110358464,
        #         51.4664939548052, 54.48853090330111, 52.130605214211734, 64.67147748428205, 69.33108970728789,
        #         63.9718688174732, 52.375566822708464, 54.12947441089743, 62.28322406555396, 71.59050216334566,
        #         54.74486277268398, 62.6418390534633, 54.55639284263577, 60.44997932174998, 61.624670384514026,
        #         62.0789819504154, 49.41861997263784, 73.03971522397934, 55.54997749774522, 63.2329028275628,
        #         66.76825593049439, 64.55850060216703, 81.18866916017284, 75.7218594594718, 68.05585940975251,
        #         67.18779651097363, 70.8660708661063, 79.65174197718466, 81.62597625756153, 89.74742336134224,
        #         83.05058699371125, 78.23298537062227, 81.88040058524383, 74.11072796835826, 84.84338512812887,
        #         82.8420183240365, 86.43031875447411, 92.22147255384724, 99.57811004432651, 80.94195451062447]
        fig, ax = plt.subplots()
        ax.plot(x, ymean, color='lightsteelblue')
        ax.plot(x, ystd, color='royalblue')
        ax.plot(x, ydiff, color='rosybrown')
        ax.set_title("Avg. and Std. Dev. of bucket load for public keys (10 buckets)")
        ax.set_xlabel("Number of public keys (network participants)")
        ax.set_ylabel("Avg & dev on 10 buckets")
        ax.legend(['average', 'std. dev.', 'max - min'])
        fig.show()

    def compute_pb_stats(self, pubkey_count):
        buckets = int(self.PB_KEY_COUNT / 1000)
        self.create_hashring(buckets)
        bucket_load = self.hash_pubkeys(buckets, pubkey_count)
        return np.average(bucket_load), np.std(bucket_load), np.max(bucket_load) - np.min(bucket_load)

    def compute_tx_stats(self, tx_count):
        buckets = int(self.PB_KEY_COUNT / 1000)
        self.create_hashring(buckets)
        tx_load = self.hash_tx(buckets, tx_count)
        return np.average(tx_load), np.std(tx_load), np.max(tx_load), np.min(tx_load)

    def run_distribution(self):
        buckets = int(self.PB_KEY_COUNT / 1000)
        self.create_hashring(buckets)
        bucket_load = self.hash_pubkeys(buckets, self.PB_KEY_COUNT)
        tx_load = self.hash_tx(buckets, len(self.TX_EXAMPLES))

        fig, ax = plt.subplots()
        size = .4
        colors = ['slategrey', 'lightsteelblue', 'cornflowerblue', 'royalblue']
        tx_colors = ['rosybrown', 'lightcoral', 'indianred', 'brown']
        patches, texts = ax.pie(bucket_load, radius=1, labels=[str(x) for x in bucket_load], colors=colors,
                                wedgeprops=dict(width=size, edgecolor='w'), labeldistance=0.8)
        for t in texts:
            t.set_horizontalalignment('center')
        patches, texts = ax.pie(tx_load, radius=1 - size, labels=[str(x) for x in tx_load], colors=tx_colors,
                                wedgeprops=dict(width=size, edgecolor='w'), labeldistance=0.8)
        for t in texts:
            t.set_horizontalalignment('center')
        ax.set_title("Public keys (blue) & Tx (red) distribution in %d buckets" % buckets)
        fig.show()

    def hash_pubkeys(self, buckets, keycount):
        bucket_load = [0 for _ in range(buckets)]
        for i in range(keycount):
            address = self.generate_key()
            bucket_load[int(self.get_bucket(address))] += 1
            if i % 1000 == 0:
                print(Fore.CYAN + "Generated address %d/%d" % (i, self.PB_KEY_COUNT))
        return bucket_load

    def generate_keys(self, key_count):
        return [self.generate_key() for _ in range(key_count)]

    def hash_keys(self, keys, buckets):
        block_seed = str(random.randint(0, 1000)) + "some more hash random" + str(random.randint(0, 1000))
        block_hash = hashlib.sha256(bytes(block_seed, 'utf-8')).hexdigest()
        bucket_load = [[] for _ in range(buckets)]
        for key in keys:
            bucket_load[int(self.get_bucket(block_hash + key))].append(key)
        return bucket_load, block_hash

    def hash_tx(self, buckets, txcount):
        tx_load = [0 for _ in range(buckets)]
        tx_samples = np.random.choice(self.TX_EXAMPLES, size=txcount, replace=False)
        for i, tx in enumerate(tx_samples):
            tx_load[int(self.get_bucket(tx))] += 1
            if i % 1000 == 0:
                print(Fore.CYAN + "Hashed %d/%d txs" % (i, self.PB_KEY_COUNT))
        print(Fore.CYAN + "Computed tx load: ", tx_load)
        return tx_load

    def generate_tx(self, buckets, txcount):
        tx_load = [[] for _ in range(buckets)]
        tx_samples = np.random.choice(self.TX_EXAMPLES, size=txcount, replace=False)
        for i, tx in enumerate(tx_samples):
            tx_load[int(self.get_bucket(tx))].append(tx)
            if i % 1000 == 0:
                print(Fore.CYAN + "Hashed %d/%d txs" % (i, self.PB_KEY_COUNT))
        return tx_load

    def configure(self, **kwargs):
        wallet = Wallet(self.ARWEAVE_WALLET_DOWN)
        print(Fore.CYAN + "Loaded wallet with %.5f AR." % wallet.balance)

        self.TX_EXAMPLES = arql(
            wallet,
            {
                "op": "equals",
                "expr1": "from",
                "expr2": "DqXrdqdSonUccH2EHP0ifXiQZb_x86Vz_3w7BkYpnss"  # random address with a lot of txs
            })
        print(Fore.CYAN + "Loaded %d transactions." % len(self.TX_EXAMPLES))

    def create_hashring(self, size):
        self.HASH_RING = HashRing([str(i) for i in range(size)], hash_fn='ketama')

    def get_bucket(self, key):
        return self.HASH_RING.get_node(key)

    @staticmethod
    def generate_key():
        """
        https://medium.com/coinmonks/bitcoin-address-generation-on-python-e267df5ff3a3
        https://github.com/burakcanekici/BitcoinAddressGenerator/blob/master/Main.py
        :return:
        """
        ecdsaPrivateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        ecdsaPublicKey = '04' + ecdsaPrivateKey.get_verifying_key().to_string().hex()
        hash256FromECDSAPublicKey = hashlib.sha256(binascii.unhexlify(ecdsaPublicKey)).hexdigest()
        ridemp160FromHash256 = hashlib.new('ripemd160', binascii.unhexlify(hash256FromECDSAPublicKey))
        prependNetworkByte = '00' + ridemp160FromHash256.hexdigest()
        hash = prependNetworkByte
        for x in range(1, 3):
            hash = hashlib.sha256(binascii.unhexlify(hash)).hexdigest()
        cheksum = hash[:8]
        appendChecksum = prependNetworkByte + cheksum
        bitcoinAddress = base58.b58encode(binascii.unhexlify(appendChecksum))

        return bitcoinAddress.decode('utf8')
