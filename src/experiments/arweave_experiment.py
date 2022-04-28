from src.experiments import Experiment

from arweave.arweave_lib import Wallet, Transaction
from arweave.transaction_uploader import get_uploader

from colorama import Fore


class ARWeaveExperiment(Experiment):

    isUpload = False

    # Don't search for it, it's not uploaded anywhere, and if it is it's empty
    ARWEAVE_WALLET_UP = '../ar_wallet_upload.json'
    ARWEAVE_WALLET_DOWN = '../ar_wallet_download.json'

    def __init__(self, isUpload):
        super().__init__()
        self.isUpload = isUpload
        self.wallet = None

    def run(self):
        if self.isUpload:
            self.run_upload()
        else:
            self.run_download()

    def run_upload(self):
        pass

    def run_download(self):
        pass

    def upload(self, filePath):
        """
        https://github.com/MikeHibbert/arweave-python-client
        :param filePath:
        :return:
        """
        with open(filePath, "rb", buffering=0) as file_handler:
            tx = Transaction(self.wallet, file_handler=file_handler, file_path=filePath)
            tx.add_tag('Content-Type', 'application/dat')
            tx.sign()

            uploader = get_uploader(tx, file_handler)

            while not uploader.is_complete:
                uploader.upload_chunk()

                print(Fore.CYAN + "{}% complete, {}/{}".format(
                    uploader.pct_complete, uploader.uploaded_chunks, uploader.total_chunks
                ))
            print(Fore.CYAN + "Upload complete! Tx: " + tx.id + ", Status: " + tx.get_status())

    def configure(self, **kwargs):
        if 'ARWEAVE_WALLET_UP' in kwargs:
            self.ARWEAVE_WALLET_UP = kwargs['ARWEAVE_WALLET_UP']
        if 'ARWEAVE_WALLET_DOWN' in kwargs:
            self.ARWEAVE_WALLET_DOWN = kwargs['ARWEAVE_WALLET_DOWN']

        address = self.ARWEAVE_WALLET_DOWN
        logMessage = "download"
        if self.isUpload:
            address = self.ARWEAVE_WALLET_UP
            logMessage = "upload"

        self.wallet = Wallet(address)
        print(Fore.CYAN + "Loaded wallet for %s with %.5f AR." % (logMessage, self.wallet.balance))
