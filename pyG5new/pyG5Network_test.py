import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import logging
import time
import struct
from PySide6.QtCore import  Slot, QObject,Signal,QByteArray
from PySide6.QtNetwork import QUdpSocket, QHostAddress,QAbstractSocket

from PySide6.QtWidgets import   QApplication

from pyG5new.udpMulticastReader import UdpMulticastReader
from pyG5new.dataRefReader import DataRefReader
  
class TestUdpReader(unittest.TestCase):
    recorded_port = None
    recorded_addr = None
    rref_frequ = None
    rref_idx = None
    rref_str = None
    rref_cmd = "XX".encode()

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        

    logger = None
    def setUp(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.multicast_reader = UdpMulticastReader()
      
    def tearDown(self):
        self.logger.debug("tearDown")
        self.multicast_reader.udpReceiverSocket.close() #udpReceiverSocket.close() 
        del self.app
        self.logger.debug("tearDown finished")

    ############################
    ####### TEST RREF SEND #####
    def test_RREF_was_sent(self):
        self.logger.debug("start test_RREF_was_sent")
     #   message,dummyMessage = self.given_BECN_datagrams()
     #   self.given_connected_slot_to_get_addr_port_slot()
     #   self.when_beacon_datagrams_are_send_and_events_processed(message, dummyMessage)
        self.when_test_reader_is_connected_to_xplane_socket()
        # self.when_dataRefReader_is_initialized()
        dataRefReader = DataRefReader() #DataRefReader(self.multicast_reader)
        self.logger.debug("self.app.processEvents():")
        self.app.processEvents()
        self.logger.debug("after self.app.processEvents()")
        # self.logger.debug("dataRefReader initialized should send to host:port: %s:%s",self.recorded_addr,self.recorded_port)
        # self.then_RREF_datagram_was_send_to_xplane()
        dataRefReader.senderUdpSocket.close()
        self.logger.debug("end test_RREF_was_sent")
       
    def when_dataRefReader_is_initialized(self):
        dataRefReader = DataRefReader() #DataRefReader(self.multicast_reader)
        self.logger.debug("self.app.processEvents():")
        self.app.processEvents()
        self.logger.debug("after self.app.processEvents()")
        self.logger.debug("after self.app.processEvents()2")
        return
    
    def when_test_reader_is_connected_to_xplane_socket(self):
        # listen on self.recorded_addr:self.recorded_port for RREF datagram:
      
        self.recorded_port = 49000
        self.recorded_addr = QHostAddress.LocalHost
        self.udp_test_socket_reader = UDPSocketReader(self.recorded_port)
        self.received_data = None
        self.logger.debug("UDPSocketReader initialized")
        def on_data_received(data):
            self.logger.debug("on_data_received()")
            self.received_data = data.data()
            self.rref_cmd, freq, idx, ref = struct.unpack("<5sii400s",self.received_data)
            if self.rref_cmd == b"RREF\x00" :
                self.rref_frequ = freq
                self.rref_idx = idx
                self.rref_str = str
            self.logger.debug("end on_data_received()")    
            return 

        self.logger.debug("udp_test_socket_reader.dataReceived.connect(on_data_received)")
        self.udp_test_socket_reader.dataReceived.connect(on_data_received)
        return
    def then_RREF_datagram_was_send_to_xplane(self):
        # Wait for the datagram to be processed
        def processEvents_and_check():
             self.app.processEvents()
             self.logger.debug("self.app.processEvents()")
             if self.rref_cmd == b"RREF\x00":
                 return True
             else:
                 self.logger.debug("rref_cmd=%s",self.rref_cmd.decode())
             return False 
        self.assertTrue(self.repeat_until_true(processEvents_and_check, 10, 0.100),msg="no RREF found after x*0.1 sec")

        self.assertEqual(self.rref_cmd , b"RREF\x00")
        # self.udp_test_socket_reader.disconnect()
        return
    ############################
    ####### TEST BECN ##########
    def test_receive_becn_data(self):
        self.senderUdpSocket = QUdpSocket()
        message,dummyMessage = self.given_BECN_datagrams()
        self.given_connected_slot_to_get_addr_port_slot()

        self.when_beacon_datagrams_are_send_and_events_processed(message, dummyMessage)
        
        self.then_addr_port_is_set_and_valid()
        self.senderUdpSocket.close()
       

    def then_addr_port_is_set_and_valid(self):
        self.assertTrue(self.recorded_port != None)
        self.assertTrue(self.recorded_addr != None)

    def when_beacon_datagrams_are_send_and_events_processed(self, message, dummyMessage):
        self.senderUdpSocket.writeDatagram(dummyMessage, 
                                self.multicast_reader.xplaneMulticastAddress, self.multicast_reader.xplaneMulticastPort)
        self.senderUdpSocket.writeDatagram(message, 
                                self.multicast_reader.xplaneMulticastAddress, self.multicast_reader.xplaneMulticastPort)
        self.app.processEvents()

    def given_connected_slot_to_get_addr_port_slot(self):
        @Slot(QHostAddress,int)
        def assert_addr_port_slot(host_addr:QHostAddress , port):
            self.logger.debug("signal_handler4test host = %s:%s",host_addr.toString(),port)
            self.recorded_port = port
            self.recorded_addr = host_addr
            self.logger.info("got port and host address %s:%s, next: QEventLoop.quit()"
                                ,host_addr.toString(),port)
        self.multicast_reader.xPlaneAddrPortSignal.connect(assert_addr_port_slot)

    def given_BECN_datagrams(self):
        cmd = b"BECN\x00"
        beacon_minor_version = 2 # uchar
        application_host_id = 1  # xint 1 for X-Plane, 2 for PlaneMaker
        version_number = 120301 # xint 104103 for X-Plane 10.41r3
        role = 1 #  uint 1 for master, 2 for extern visual, 3 for IOS
        port = 49000  # ushort port number X-Plane is listening on, 49000 by default
        computer_name = "myCompi\x00" # xchr[500] the hostname of the computer, e.g. “Joe’s Macbook”, null-terminated string
        raknet_port = 49010; # ushort port number the X-Plane Raknet client is listening on, default is 49010
        message = struct.pack("<5sBiiIH500sH", cmd, beacon_minor_version,
                              application_host_id,version_number,role,port,computer_name.encode(),
                              raknet_port)      
        dummyMessage = struct.pack("<5s", b"DMMY\x00")            
        return message,dummyMessage
    def repeat_until_true(self, func, max_attempts=None, delay=0):
        """
        Repeatedly calls the given function until it returns True.

        Args:
        func (callable): The function to be called repeatedly.
        max_attempts (int, optional): Maximum number of attempts. If None, will try indefinitely.
        delay (float, optional): Delay in seconds between attempts.

        Returns:
        bool: True if func() eventually returned True, False if max_attempts was reached.

        Raises:
        Any exception raised by func() will be propagated.
        """
        import time
        self.logger.debug("repeat loop start")
        attempts = 0
        while max_attempts is None or attempts < max_attempts:
            if func():
                return True
            self.logger.debug("repeat loop false")
            attempts += 1
            if delay > 0:
                time.sleep(delay)
        
        return False
        
 
                  
class UDPSocketReader(QObject):
    dataReceived = Signal(QByteArray)

    def __init__(self, port, parent=None):
        super().__init__(parent)
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.socket = QUdpSocket(self)
        self.socket.stateChanged.connect(self.stateChangedSlot)
        self.socket.bind(QHostAddress.LocalHost, port)
        self.socket.readyRead.connect(self.processPendingDatagrams)
      #  self.socket.connected.connect(self.connectedSlot)
        self.logger.debug("UDPSocketReader.__init__ ")
    
    @Slot(QAbstractSocket.SocketState)
    def stateChangedSlot(self,state):
        self.logger.debug("socket state changed {}".format(state))

    @Slot()
    def connectedSlot(self):
        self.logger.debug("socket state connected")

    @Slot()
    def processPendingDatagrams(self):
        self.logger.debug("UDPSocketReader.processPendingDatagrams readyRead slot() called ")
        while self.socket.hasPendingDatagrams():
            datagram = self.socket.receiveDatagram()
            self.dataReceived.emit(datagram.data())
        

if __name__ == '__main__':
    unittest.main()