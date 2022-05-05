import SolveRequest_pb2

import pythonp2p


class Server(pythonp2p.Node):

    solveRequest = SolveRequest_pb2.SolveRequest()

    def __init__(self):
        super().__init__()

    def on_message(self, message, sender, private):
        pass

    def send_message(self, data, receiver=None):
        super().send_message(data, receiver)

    def start(self):
        super().start()
