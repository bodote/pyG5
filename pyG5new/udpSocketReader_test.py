import sys
from PySide6.QtCore import QObject, Signal, Slot, QByteArray
from PySide6.QtNetwork import QHostAddress,QUdpSocket,QAbstractSocket
from PySide6.QtWidgets import   QApplication
import unittest
import logging

class UDPSocketReader(QObject):
    dataReceived = Signal(QByteArray)

    def __init__(self, port, parent=None):
        super().__init__(parent)
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.socket = QUdpSocket(self)
        self.socket.stateChanged.connect(self.stateChangedSlot)
        self.socket.bind(QHostAddress.LocalHost, 49000)
        self.socket.readyRead.connect(self.processPendingDatagrams)
        self.logger.debug("UDPSocketReader.__init__")
   
    @Slot(QAbstractSocket.SocketState)
    @Slot("QAbstractSocket::SocketState")
    def stateChangedSlot(self,state):
        self.logger.debug("socket state changed {}".format(state))


    @Slot()
    def processPendingDatagrams(self):
        self.logger.debug("UDPSocketReader.processPendingDatagrams")
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            self.dataReceived.emit(datagram.data())

class TestUDPSocketReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   
    def setUp(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = QApplication(sys.argv)
        self.reader = UDPSocketReader(0)
        self.received_data = None
        self.logger.debug("UDPSocketReader initialized")

    def test_receive_datagram(self):
        def on_data_received(data):
            self.logger.debug("on_data_received")
            self.received_data = data.data().decode()
            self.logger.debug("end on_data_received: %s",self.received_data)
            return
        self.logger.debug("reader.dataReceived.connect(on_data_received)")
        self.reader.dataReceived.connect(on_data_received)

        # Send a test datagram
        self.sender = QUdpSocket()
        self.logger.debug("sender= QUdpSocket(); sender.stateChanged.connect(self.stateChangedSlotTest)")
        self.sender.stateChanged.connect(self.stateChangedSlotTest)
        test_message = "Hello, UDP!"
        self.sender.writeDatagram(test_message.encode(), QHostAddress.LocalHost, 49000)
        self.logger.debug("after sender.writeDatagram")
        # Wait for the datagram to be processed
        self.logger.debug("self.app.processEvents():")
        self.app.processEvents()
        self.logger.debug("after processEvents()")

        self.assertEqual(self.received_data, test_message)
    
    @Slot(QAbstractSocket.SocketState)
    def stateChangedSlotTest(self,state):
        self.logger.debug("socket state changed {}".format(state))


if __name__ == '__main__':
    unittest.main()