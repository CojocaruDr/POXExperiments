import time

import numpy as np
from botocore.exceptions import ClientError

from src.experiments import Experiment
import boto3

from colorama import Fore


class S3Experiment(Experiment):
    """
    After observing the latencies for ARweave (which was the preferred storage provider for POX), I decided
    to benchmark S3 performance as well. There is also filecoin, a project that is in direct competition
    with S3, however the only advantage is that it is supposedly cheaper, and since it is decentralized, it
    is also supposed to be more reliable. None of that matters in the experiment phase.

    Upload speeds:
    * ./resources/poxsamples_dot/generated_mat10000x10000_1_1M_0.dat: 166.42
    * ./resources/poxsamples_dot/generated_mat10000x10000_0_1M_0.dat: 166.84

    Download speeds:
    * ./resources/poxsamples_dot/generated_mat10000x10000_1_1M_0.dat: 80.28
    * ./resources/poxsamples_dot/generated_mat10000x10000_0_1M_0.dat: 83.00

    Finding 1: While upload speeds are probably the best out of all the storage providers, the download speeds
    are awful unless you replicate the S3 bucket in all regions. Proximity to an AWS datacenter is crucial here.
    """

    isUpload = False

    M0_PATH = "./resources/poxsamples_dot/generated_mat10000x10000_0_1M_0.dat"
    M1_PATH = "./resources/poxsamples_dot/generated_mat10000x10000_1_1M_0.dat"
    DUMMY_PATH = "./resources/dummyfile.dat"

    S3_BUCKET = "m1-pox-example"

    def __init__(self, isUpload):
        super().__init__()
        self.isUpload = isUpload

    def run(self):
        if self.isUpload:
            self.run_upload()
        else:
            self.run_download()
        # self.plot_results()

    def run_upload(self):
        self.upload(self.DUMMY_PATH)

    def upload(self, filePath):
        print(Fore.CYAN + "Running upload experiment on %s" % filePath)
        startTime = time.time()
        self.upload_file(filePath, self.S3_BUCKET, filePath.split('/')[-1].replace('.dat', ''))
        totalTime = time.time() - startTime
        print(Fore.CYAN + "Uploaded %s in %.2f seconds" % (filePath, totalTime))
        return totalTime

    @staticmethod
    def upload_file(file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name
        :return: True if file was uploaded, else False
        """
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            print(Fore.CYAN + "Exception uploading to s3: ", e)
            return False
        return True

    def run_download(self):
        s3 = boto3.client('s3')
        results = []
        for file in [self.M0_PATH, self.DUMMY_PATH]:
            print(Fore.CYAN + "Running download experiment on %s" % file)
            object_name = file.split('/')[-1].replace('.dat', '')
            startTime = time.time()
            res = s3.get_object(Bucket=self.S3_BUCKET, Key=object_name)
            body = res['Body']
            line = body.next()
            data = []
            try:
                while line:
                    data.append(line)
                    line = body.next()
            except StopIteration:
                pass
            print(len(data) * 1024)
            totalTime = time.time() - startTime
            results.append(totalTime)
            print(Fore.CYAN + "Downloaded %s in %.2f seconds" % (object_name, totalTime))
        return results
