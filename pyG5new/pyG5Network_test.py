import sys
import logging
import pytest
import struct
from PySide6.QtCore import  Slot, QObject,Signal,QByteArray
from PySide6.QtNetwork import QUdpSocket, QHostAddress,QAbstractSocket

from PySide6.QtWidgets import   QApplication

from pyG5new.udpMulticastReader import UdpMulticastReader
from pyG5new.dataRefReader import DataRefReader
from pyG5new import repeat_until_true


class UDPSocketReader(QObject):
    dataReceived = Signal(QByteArray)

    def __init__(self, port,  parent=None):
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
global_rref_cmd = "XX".encode()
global_counter = 1
class TestPyG5Network:
    recorded_port = None
    recorded_addr = None
    rref_freq = None
    rref_idx = None
    rref_str = None

        
    def setUp(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("start setUp global_counter = %s",global_counter)
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.multicast_reader = UdpMulticastReader()
        global_rref_cmd = "XX".encode()
      
    def tearDown(self):
        self.logger.debug("tearDown")
        self.multicast_reader.close() #udpReceiverSocket.close() 
        self.logger.debug("tearDown finished")
    
    @pytest.fixture
    def setup_teardown(self):
        self.setUp()
        yield
        self.tearDown()

    ############################
    ####### TEST RREF SEND #####
    @pytest.mark.repeat(2)
    def test_RREF_was_sent(self,setup_teardown):
        self.logger.debug("start test_RREF_was_sent")
        message,dummyMessage = self.given_BECN_datagrams()
        self.given_connected_slot_to_get_addr_port_slot()
     #   self.when_beacon_datagrams_are_send_and_events_processed(message, dummyMessage)
        self.when_test_reader_is_connected_to_xplane_socket()
        self.logger.debug("after when_test_reader_is_connected_to_xplane_socket: global_rref_cmd=%s global_counter=%s",
                          global_rref_cmd,global_counter)  
        # self.when_dataRefReader_is_initialized()
        dataRefReader = DataRefReader() #DataRefReader(self.multicast_reader)
        self.logger.debug("after DataRefReader(): ")
        self.logger.debug("before self.app.processEvents(): global_rref_cmd=%s global_counter=%s  id=%s hash=%s"
                          ,global_rref_cmd,global_counter,id(self),hash(self))  
        self.app.processEvents()
        self.logger.debug("after app.processEvents(): global_rref_cmd=%s global_counter=%s",global_rref_cmd,global_counter)  
        self.then_RREF_datagram_was_send_to_xplane()
        self.logger.debug("after then_RREF_datagram_was_send_to_xplane()")
        dataRefReader.close()
        self.logger.debug("after dataRefReader.senderUdpSocket.close()")
        self.multicast_reader.xPlaneAddrPortSignal.disconnect(self.assertAddrPortSlot)
        self.logger.debug("end test_RREF_was_sent, xPlaneAddrPortSignal.disconnect(")

    def then_RREF_datagram_was_send_to_xplane(self):
        self.logger.debug("start then_RREF_datagram_was_send_to_xplane()")
        # Wait for the datagram to be processed
        def processEvents_and_check(self):
             self.app.processEvents()
             self.logger.debug("self.app.processEvents()")
             if global_rref_cmd == b"RREF\x00":
                 return True
             else:
                 self.logger.debug("rref_cmd=%s",global_rref_cmd.decode())
             return False 
        self.logger.debug("before repeat_unit_true: global_rref_cmd=%s",global_rref_cmd)
        result =  repeat_until_true(self,processEvents_and_check, 10, 0.100)
        self.logger.debug("after  repeat_until_true()")
        assert (global_rref_cmd == b"RREF\x00")
        # self.udp_test_socket_reader.disconnect()
        return
       
    def when_dataRefReader_is_initialized(self):
        dataRefReader = DataRefReader() #DataRefReader(self.multicast_reader)
        self.logger.debug("self.app.processEvents():")
        self.app.processEvents()
        self.logger.debug("after self.app.processEvents()")
        self.logger.debug("after self.app.processEvents()2")
        return
    
    def on_data_received(self,data):
            global global_counter
            global global_rref_cmd
            self.logger.debug("start on_data_received() global_counter=%s id=%s hash=%s",global_counter,id(self),hash(self))  
            global_counter = global_counter+1
            self.logger.debug("on_data_received()")
            self.received_data = data.data()
            global_rref_cmd, freq, idx, str = struct.unpack("<5sii400s",self.received_data)
            self.logger.debug("on_data_received(): global_rref_cmd=%s global_counter=%s",global_rref_cmd,global_counter)  
            if global_rref_cmd == b"RREF\x00" :
                self.logger.debug("RREF received")  
                self.rref_freq = freq
                self.rref_idx = idx
                self.rref_str = str
            self.logger.debug("end on_data_received()")    
            return 

    def when_test_reader_is_connected_to_xplane_socket(self):
        # listen on self.recorded_addr:self.recorded_port for RREF datagram:
      
        self.recorded_port = 49000
        self.recorded_addr = QHostAddress.LocalHost
        self.udp_test_socket_reader = UDPSocketReader(self.recorded_port)
        self.received_data = None
        self.logger.debug("UDPSocketReader initialized id=%s hash=%s",id(self),hash(self))  
        self.udp_test_socket_reader.dataReceived.connect(self.on_data_received)
        self.logger.debug("udp_test_socket_reader.dataReceived connected to (self.on_data_received)")
        return

    ############################
    ####### TEST BECN ##########
    @pytest.mark.repeat(2)
    def test_receive_becn_data(self,setup_teardown):
        self.logger.debug("start test_receive_becn_data")
        self.senderUdpSocket = QUdpSocket()
        message,dummyMessage = self.given_BECN_datagrams()
        self.given_connected_slot_to_get_addr_port_slot()

        self.when_beacon_datagrams_are_send_and_events_processed(message, dummyMessage)
        repeat_until_true( self, self.then_addr_port_is_set_and_valid, max_attempts=20, delay=0.1)
        
        self.senderUdpSocket.close()
        self.multicast_reader.xPlaneAddrPortSignal.disconnect(self.assertAddrPortSlot)
        self.logger.debug("end test_receive_becn_data, xPlaneAddrPortSignal.disconnect(")
       

    def then_addr_port_is_set_and_valid(self,self2):
        #self.assertTrue(self.recorded_port != None)
        #self.assertTrue(self.recorded_addr != None)
        if (self.recorded_port == None) | (self.recorded_addr == None): 
            self.logger.debug("got no recoreded_port or -addr  yet called processEvents() again ")
            self.app.processEvents()
            return False
        self.logger.debug("then_addr_port_is_set_and_valid()")
        return (self.recorded_port != None) & (self.recorded_addr != None)

    def when_beacon_datagrams_are_send_and_events_processed(self, message, dummyMessage):
        self.senderUdpSocket.writeDatagram(dummyMessage, 
                                self.multicast_reader.xplaneMulticastAddress, self.multicast_reader.xplaneMulticastPort)
        self.senderUdpSocket.writeDatagram(message, 
                                self.multicast_reader.xplaneMulticastAddress, self.multicast_reader.xplaneMulticastPort)
        self.app.processEvents()
        self.logger.debug("datagram written,processEvents() called")

    def given_connected_slot_to_get_addr_port_slot(self):
        @Slot(QHostAddress,int)
        def assert_addr_port_slot(host_addr:QHostAddress , port):
            self.logger.debug("signal_handler4test host = %s:%s",host_addr.toString(),port)
            self.recorded_port = port
            self.recorded_addr = host_addr
            self.logger.info("got port and host address %s:%s"
                                ,host_addr.toString(),port)
        self.assertAddrPortSlot = assert_addr_port_slot
        self.multicast_reader.xPlaneAddrPortSignal.connect(self.assertAddrPortSlot)
        self.logger.debug("multicast_reader.xPlaneAddrPortSignal.connect(self.assertAddrPortSlot)")

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
        
 
                  
