import sys
from pyG5new import repeat_until_true
from PySide6.QtCore import QObject, Signal, Slot, QByteArray
from PySide6.QtNetwork import QHostAddress,QUdpSocket,QAbstractSocket
from PySide6.QtWidgets import   QApplication
import pytest
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
    def close(self):
        self.socket.close()


class TestUDPSocketReader:
   
    def setUp(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.reader = UDPSocketReader(0)
        self.received_data = None
        self.logger.debug("setUp initialized")
    
    def tearDown(self):
        self.reader.close()
        # del self.app
        self.logger.debug("tearDown disconnected and closed")
       
    @pytest.fixture
    def setup_teardown(self):
        self.setUp()
        yield
        self.tearDown()
        
   
    @pytest.mark.repeat(100)
    def test_receive_datagram(self,setup_teardown):
        def on_data_received(data):
            self.logger.debug("on_data_received")
            self.received_data = data.data().decode()
            self.logger.debug("end on_data_received: %s",self.received_data)
            return
        self.onDataReceived = on_data_received
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
        self.logger.debug("before self.app.processEvents():")

        def process_events_and_assert():
            self.app.processEvents()
            return self.received_data ==  test_message
        repeat_until_true(self, process_events_and_assert, max_attempts=10, delay=0.1)
        self.logger.debug("after processEvents(), sleep , processEvents()")
        assert self.received_data ==  test_message
        # self.reader.dataReceived.disconnect(on_data_received)
    
    @Slot(QAbstractSocket.SocketState)
    def stateChangedSlotTest(self,state):
        self.logger.debug("socket state changed {}".format(state))
