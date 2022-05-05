from src.experiments.experiment import Experiment
from src.server.server_base import Server

import time


class ServerBasedExperiment(Experiment):

    server = None
    isDone = False

    def __init__(self):
        super().__init__()

    def run(self):
        self.server.start()

        while not self.isDone:
            time.sleep(5)

    def configure(self, **kwargs):
        self.server = Server()
