import SolveRequest_pb2
import ValidateRequest_pb2

import pythonp2p
from colorama import Fore


class Server(pythonp2p.Node):

    SOLVE_REQUEST_CODE = 1
    VALIDATE_REQUEST_CODE = 2

    recvMode = False

    RECV_PORT = 65434
    SEND_PORT = 65435

    def __init__(self, recv):
        self.recvMode = recv
        if recv:
            port = self.RECV_PORT
            connectPort = self.SEND_PORT
            self.label = Fore.GREEN + "[RECV] "
        else:
            port = self.SEND_PORT
            connectPort = self.RECV_PORT
            self.label = Fore.RED + "[SEND] "

        super().__init__("", port)
        if not recv:
            self.connect_to("127.0.0.1", connectPort)

        print(self.label + "Node with id %s registered" % self.id)

    def on_message(self, message, sender, private):
        try:
            protoStruct = self._decode(message)
            print(Fore.GREEN + "[RECV] message %s from %s" % (str(protoStruct), sender))
        except Exception as e:
            print(self.label + "Error processing message from %s: %s" % (sender, e))

    def send_message(self, protobufObj, receiver=None):
        try:
            serialized = self._encode(protobufObj)
            print(Fore.RED + "[SEND] message %s to %s" % (str(protobufObj), receiver))
            super().send_message(str(serialized, 'utf-8'), receiver)
        except Exception as e:
            print(self.label + "Error sending message to %s: %s" % (receiver, e))

    def start(self):
        super().start()

    def _encode(self, protobuf):
        return self._get_code(protobuf) + protobuf.SerializeToString()

    def _decode(self, message):
        message = bytearray(message.encode())
        code = int.from_bytes(message[:4], 'big')

        protobuf = None
        if code == self.SOLVE_REQUEST_CODE:
            protobuf = SolveRequest_pb2.SolveRequest()
        if code == self.VALIDATE_REQUEST_CODE:
            protobuf = ValidateRequest_pb2.ValidateRequest()

        if protobuf is None:
            raise RuntimeError("Received unknown object code %d." % code)
        else:
            protobuf.ParseFromString(message[4:])
            return protobuf

    def _get_code(self, protobuf):
        if isinstance(protobuf, SolveRequest_pb2.SolveRequest):
            return int.to_bytes(self.SOLVE_REQUEST_CODE, 4, 'big')
        if isinstance(protobuf, ValidateRequest_pb2.ValidateRequest):
            return int.to_bytes(self.VALIDATE_REQUEST_CODE, 4, 'big')
