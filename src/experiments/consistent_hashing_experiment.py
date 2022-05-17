import base58
import binascii
import ecdsa
import hashlib
import matplotlib.pyplot as plt

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
    PB_KEY_MAX = 1000000

    HASH_RING = None

    def __init__(self):
        super().__init__()

    def run(self):
        buckets = int(self.PB_KEY_COUNT / 1000)
        self.create_hashring(buckets)
        bucket_load = [0 for _ in range(buckets)]
        for i in range(self.PB_KEY_COUNT):
            address = self.generate_key()
            bucket_load[int(self.get_bucket(address))] += 1
            if i % 1000 == 0:
                print(Fore.CYAN + "Generated address %d/%d" % (i, self.PB_KEY_COUNT))
        print(Fore.CYAN + "Computed bucket load: ", bucket_load)

        colors = ['slategrey', 'lightsteelblue', 'cornflowerblue', 'royalblue']
        plt.pie(bucket_load, labels=[str(x) for x in bucket_load], colors=colors)
        plt.title("Public key distribution in %d buckets" % buckets)
        plt.show()

    def configure(self, **kwargs):
        pass

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
