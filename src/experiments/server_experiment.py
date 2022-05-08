from src.experiments.experiment import Experiment
from src.server.server_base import Server

import time
from colorama import Fore

import SolveRequest_pb2
import ValidateRequest_pb2
import generic_pb2


class ServerBasedExperiment(Experiment):

    server = None
    isDone = False
    recv = False

    # Regenerates every time a SEND experiment starts
    send_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2kLv9mftlkj7uyxYN2Z\
I3Axm5NEIv0Zv1egqvcNoN/e1DU7yLzYUNr+Kp8mU+XPFALUM0TeZvYiPpXlvlLY7ZFwkkKtY652zudKcqP\
Czn2KlAuUpbLtwCttea131GN42um4pS4qCzUO1mIISVc4cEl8onDX5OrE0RqOjxEBtGvQIDAQAB"

    MATRICES = {
        "gSFcJjCYtZ1OFZ3UteoIJ1UjZLUanMsS_O0XVYwPuHI": "generated_mat10000x10000_0_1M_0.dat",
        "LsKHq8uhwjhA_dxTQmxaCD9UL7_puQ_mvmWn6hgd2kE": "generated_mat10000x10000_1_1M_0.dat",
        "pI8Ose_wiAofAbqCFg9Yry4Z0jR45ubEPpHZTv8h8CI": "generated_mat10000x10000_1_1M_1.dat"
    }

    def __init__(self, recv):
        super().__init__()
        self.recv = recv

    def run(self):
        self.server.start()

        while not self.isDone:
            if not self.recv:
                self.server.send_message(self.generate_solve_req())
            time.sleep(5)

    def configure(self, **kwargs):
        self.server = Server(self.recv)

    def generate_solve_req(self):
        solveReq = SolveRequest_pb2.SolveRequest()
        solveReq.solver = generic_pb2.Solver.DotSolver
        solveReq.storageProvider = generic_pb2.StorageProvider.AWS
        solveReq.verificationSchema = generic_pb2.VerificationSchema.PROBABILISTIC
        solveReq.m0Ids.extend(["gSFcJjCYtZ1OFZ3UteoIJ1UjZLUanMsS_O0XVYwPuHI"])
        solveReq.m1Ids.extend(["LsKHq8uhwjhA_dxTQmxaCD9UL7_puQ_mvmWn6hgd2kE"])
        solveReq.name = "testMessage"
        return solveReq
