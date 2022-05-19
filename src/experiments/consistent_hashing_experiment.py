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
        self.run_tx_deviation()

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

    def hash_tx(self, buckets, txcount):
        tx_load = [0 for _ in range(buckets)]
        tx_samples = np.random.choice(self.TX_EXAMPLES, size=txcount, replace=False)
        for i, tx in enumerate(tx_samples):
            tx_load[int(self.get_bucket(tx))] += 1
            if i % 1000 == 0:
                print(Fore.CYAN + "Hashed %d/%d txs" % (i, self.PB_KEY_COUNT))
        print(Fore.CYAN + "Computed tx load: ", tx_load)
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
