import time

from src.experiments import Experiment

from arweave.arweave_lib import Wallet, Transaction
from arweave.transaction_uploader import get_uploader
import matplotlib.pyplot as plt

from colorama import Fore


class ARWeaveExperiment(Experiment):
    """
    Exp results :
    Upload times:
        * dummyfile.dat: 7.94 sec
        * generated_mat10000x10000_0_1M_0.dat: 51 min (0,184 AR  4,41 USD) 762Mb
        * generated_mat10000x10000_1_1M_0.dat: 56 min (0,182 AR  4,28 USD) 762Mb
    Download times:
        * dummyfile.dat: 10.72 sec
        * generated_mat10000x10000_0_1M_0.dat: 16.278 min (976.68 seconds) (~8-9 seconds after a few minutes)
        * generated_mat10000x10000_1_1M_0.dat: 14.48 min (869.26 seconds) (~8-9 seconds after a few minutes)
        (~800 Kb/s mostly, regular drops to 50-150Kb and occasional dead times - 0 kb/s) -- SHORTLY AFTER UPLOAD

    Finding 1: Upload speed is terrible. The upside is that as soon as the tx is signed&sent
    (roughly 6 seconds), miners can start downloading the data associated with it
    (upload is done in chunks). This means that ARweave can essentially work as a peer to
    peer file transfer mechanism on the first upload, and still leverage permanent storage.
    Note: The streaming download is not out of the box. If a TX is still being uploaded data to,
    the download operation will finish when downloading all the available content. Subsequent retries
    must be made, and there needs to be smart use of caching here as well.

    Finding2 (TX confirmation): Tx takes quite a while to be confirmed. Downloads can only start after
    confirmation. Confirmation time seems to vary drastically. The first two experiments were unfortunately
    not timed, but they were much faster than the third one. The third took
    Found experiment data:
    Upload start: 1651412296
    Download attempts start: 1651412307 (subsequent tries every 5 seconds)
    Download start: 1651413315 (about 30% upload complete)
    (this seems to vary a lot, previous trys started at much samaller %s)
    * Launch a download, mark the timestamp and measure how much it takes. Rinse and repeat
    Upload finished: 1651415656

    *Timestamps: [1651412797.6914392, 1651413437.1142588, 1651413573.6977386, 1651413911.0904038, 1651414433.3321674, 1651415045.2217925, 1651415322.362638, 1651415876.2039237, 1651416878.5710511, 1651416888.8680816, 1651416898.069109, 1651416907.1071362, 1651416916.283664, 1651416925.8741934, 1651416935.400223, 1651416944.9022503, 1651416954.9547808, 1651416964.2833095, 1651416973.559337, 1651416983.2513628, 1651416992.6948802, 1651417001.8173976, 1651417011.0739145, 1651417020.7374332, 1651417029.8059502, 1651417038.8084683, 1651417048.1394868, 1651417057.3865025, 1651417066.9995217, 1651417076.3515387, 1651417085.7450562, 1651417094.8985739, 1651417103.9045908, 1651417113.6116126, 1651417122.7541285, 1651417132.002645]
    *DownTime: [639.4178206920624, 136.5779790878296, 337.3826653957367, 522.2032635211945, 611.8636255264282, 277.1403434276581, 553.8392863273621, 1002.3141272068024, 10.244030237197876, 9.147528171539307, 8.985027313232422, 9.122527122497559, 9.536528587341309, 9.46953010559082, 9.449026584625244, 9.999029397964478, 9.259030818939209, 9.22102665901184, 9.625528812408447, 9.389517307281494, 9.06851601600647, 9.203016519546509, 9.611018419265747, 9.01601791381836, 8.942518472671509, 9.275516271591187, 9.190516471862793, 9.559518098831177, 9.297516822814941, 9.339019060134888, 9.100017547607422, 8.952518939971924, 9.651018142700195, 9.08851408958435, 9.191515684127808, 9.39601731300354]

    Finding3: After enough block height,(~10 minutes after complete upload), the network becomes much, much faster.
    Download speeds essentially top out my bandwidth (100Mb/s). It seems download speeds also increases
    gradually, probably with the block height.

    Finding4: Speeds remain the same after the upload is finished. once enough blocks are stacked on top of the initial
    tx, the download will max out the bandwidth.

    """

    isUpload = False

    # Don't search for it, it's not uploaded anywhere, and if it is it's empty
    ARWEAVE_WALLET_UP = '../resources/ar_wallet_upload.json'
    ARWEAVE_WALLET_DOWN = '../resources/ar_wallet_download.json'

    M0_PATH = "../resources/poxsamples_dot/generated_mat10000x10000_0_1M_1.dat"
    M1_PATH = "../resources/poxsamples_dot/generated_mat10000x10000_1_1M_1.dat"
    DUMMY_PATH = "../resources/dummyfile.dat"

    TRANSACTIONS = {
        "-oF1ADpK5Rnz8QN_jeycqPO-wmYvDBCSxRDM0802URM": "dummyfile.dat",
        "_HgMpk4MTUjOe2DHCBGu-tjOExerGe1F6SP0sNRT6us": "dummyfile.dat",
        "gSFcJjCYtZ1OFZ3UteoIJ1UjZLUanMsS_O0XVYwPuHI": "generated_mat10000x10000_0_1M_0.dat",
        "LsKHq8uhwjhA_dxTQmxaCD9UL7_puQ_mvmWn6hgd2kE": "generated_mat10000x10000_1_1M_0.dat",
        "pI8Ose_wiAofAbqCFg9Yry4Z0jR45ubEPpHZTv8h8CI": "generated_mat10000x10000_1_1M_1.dat"
    }

    def __init__(self, isUpload):
        super().__init__()
        self.isUpload = isUpload
        self.wallet = None

    def run(self):
        if self.isUpload:
            self.run_upload()
        else:
            self.run_download()
        # self.plot_results()

    def plot_results(self):
        # downloadTimes = [34.54, 39.88, 1023, 100.69288444519043, 87.78737139701843, 425.37746143341064,
        #                  757.177606344223,
        #                  411.2595331668854, 814.6167254447937, 9.716392993927002, 9.318464040756226, 8.829202651977539,
        #                  8.760484457015991, 8.746602773666382, 8.738468647003174, 8.760543584823608, 9.189830780029297,
        #                  8.88254451751709, 8.839544773101807, 8.852820873260498, 8.761947870254517]
        # timestamps = [1651406270, 1651406303, 1651406406, 1651407475.1185744, 1651407575.8124585, 1651407663.6003299,
        #               1651408089.0067916, 1651408846.2333982, 1651409257.5169315, 1651410072.184157, 1651410081.95055,
        #               1651410091.3195136, 1651410100.2002163, 1651410109.0112007, 1651410117.8183048,
        #               1651410126.6072736, 1651410135.4188175, 1651410144.659148, 1651410153.5936923, 1651410162.4852388,
        #               1651410171.3905602]
        downloadTimes = [639.4178206920624, 136.5779790878296, 337.3826653957367, 522.2032635211945, 611.8636255264282, 277.1403434276581, 553.8392863273621, 1002.3141272068024, 10.244030237197876, 9.147528171539307, 8.985027313232422, 9.122527122497559, 9.536528587341309, 9.46953010559082, 9.449026584625244, 9.999029397964478, 9.259030818939209, 9.22102665901184, 9.625528812408447, 9.389517307281494, 9.06851601600647, 9.203016519546509, 9.611018419265747, 9.01601791381836, 8.942518472671509, 9.275516271591187, 9.190516471862793, 9.559518098831177, 9.297516822814941, 9.339019060134888, 9.100017547607422, 8.952518939971924, 9.651018142700195, 9.08851408958435, 9.191515684127808, 9.39601731300354]
        timestamps = [1651412797.6914392, 1651413437.1142588, 1651413573.6977386, 1651413911.0904038, 1651414433.3321674, 1651415045.2217925, 1651415322.362638, 1651415876.2039237, 1651416878.5710511, 1651416888.8680816, 1651416898.069109, 1651416907.1071362, 1651416916.283664, 1651416925.8741934, 1651416935.400223, 1651416944.9022503, 1651416954.9547808, 1651416964.2833095, 1651416973.559337, 1651416983.2513628, 1651416992.6948802, 1651417001.8173976, 1651417011.0739145, 1651417020.7374332, 1651417029.8059502, 1651417038.8084683, 1651417048.1394868, 1651417057.3865025, 1651417066.9995217, 1651417076.3515387, 1651417085.7450562, 1651417094.8985739, 1651417103.9045908, 1651417113.6116126, 1651417122.7541285, 1651417132.002645]

        fig, ax1 = plt.subplots(figsize=(7, 5))
        ax1.plot(range(len(downloadTimes)), downloadTimes, color='royalblue')
        # ax1.set_xticks(timestamps)
        # ax1.set_xticklabels(["%.1f" % ((x - 1651406098) / 60) for x in timestamps], rotation=90)  # 1651406098 is when Upload started.
        ax1.set_ylabel("Seconds to download exercise (760Mb)")
        ax1.axvline(self.find_index(1651415656, timestamps), color='red')
        # ax1.set_xlabel("Seconds since upload start")
        ax1.set_title("Repeated downloads over the same exercise")
        ax1.legend(['seconds to download', 'upload complete'])
        fig.show()

    @staticmethod
    def find_index(tstamp, series):
        for i in range(len(series)):
            if series[i] < tstamp:
                i += 1
            else:
                break
        return i + 1

    def run_upload(self):
        self.upload(self.M1_PATH)

    def run_download(self):
        times = []
        timestamps = []
        while True:
            for tx in self.TRANSACTIONS:
                timestamps.append(time.time())
                dTime = self.download(tx)
                print(Fore.CYAN + "Downloaded %s in %.2f seconds." % (self.TRANSACTIONS[tx], dTime))
                times.append(dTime)
                print(times)
                print(timestamps)

    def upload(self, filePath):
        """
        https://github.com/MikeHibbert/arweave-python-client
        :param filePath:
        :return:
        """
        startTime = time.time()
        print(Fore.YELLOW + "[UpThread] Starting upload ", startTime)
        with open(filePath, "rb", buffering=0) as file_handler:
            tx = Transaction(self.wallet, file_handler=file_handler, file_path=filePath)
            tx.add_tag('Content-Type', 'application/dat')
            tx.sign()

            try:
                uploader = get_uploader(tx, file_handler)
                print(Fore.CYAN + "Committed tx: %s" % tx.id)
                chunks = []
                while not uploader.is_complete:
                    cTime = time.time()
                    uploader.upload_chunk()
                    chunks.append(time.time() - cTime)

                    print(Fore.CYAN + "{}% complete, {}/{}".format(
                        uploader.pct_complete, uploader.uploaded_chunks, uploader.total_chunks
                    ))
                    print(time.time())
            except Exception as e:
                if uploader.pct_complete == uploader.uploaded_chunks:
                    print(Fore.CYAN + "Exception seen again though upload is ready.")

            print(Fore.CYAN + "Upload complete! Tx: " + tx.id + ", Status: " + tx.get_status())
        print(Fore.YELLOW + "[UpThread] Upload complete ", time.time())

        totalTime = time.time() - startTime
        print(Fore.CYAN + "Upload time: %.2f" % totalTime)
        print(Fore.CYAN + "Chunks: ", chunks)
        return totalTime, chunks

    def download(self, tx_id):
        startTime = time.time()
        print(Fore.RED + "[DownThread] Started downloading at ", startTime)
        tx = Transaction(self.wallet, id=tx_id)
        while tx.get_status() == "PENDING":
            print(Fore.CYAN + "Status is still pending...")
            time.sleep(5)
        print(Fore.CYAN + "TX is confirmed! Downloading ", time.time())
        tx.get_transaction()
        tx.get_data()
        try:
            print(tx.data_size)
            print(tx)
        except Exception as e:
            pass
        print(Fore.RED + "[DownThread] Finished downloading at ", time.time())
        totalTime = time.time() - startTime
        return totalTime

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
