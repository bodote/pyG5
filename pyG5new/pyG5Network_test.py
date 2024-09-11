import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import logging
import time
import struct
from PySide6.QtCore import  Slot, QEventLoop
from PySide6.QtNetwork import QUdpSocket, QHostAddress,QAbstractSocket

from PySide6.QtWidgets import   QApplication

from pyG5new.UdpMulticastReader import UdpMulticastReader


  
class TestUdpReader(unittest.TestCase):
    recorded_port = None
    recorded_addr = None
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.__class__.__name__)
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.reader = UdpMulticastReader()
        self.senderUdpSocket = QUdpSocket()
      
       
    def tearDown(self):
        self.logger.debug("tearDown")
        self.reader.udpReceiverSocket.close()
        self.senderUdpSocket.close()
        del self.app
        self.logger.debug("tearDown finished")
    
    def test_receive_becn_data(self):
        self.logger.debug("start test_receive_becn_data")
        cmd = b"BECN\x00"
        beacon_minor_version = 2 # uchar
        application_host_id = 1  # xint 1 for X-Plane, 2 for PlaneMaker
        version_number = 120301 # xint 104103 for X-Plane 10.41r3
        role = 1 #  uint 1 for master, 2 for extern visual, 3 for IOS
        port = 49000  # ushort port number X-Plane is listening on, 49000 by default
        computer_name = "myCompi\x00" # xchr[500] the hostname of the computer, e.g. “Joe’s Macbook”, null-terminated string
        raknet_port = 49010; # ushort port number the X-Plane Raknet client is listening on, default is 49010
        message = struct.pack("<5sBiiIH500sH", cmd, beacon_minor_version,
                              application_host_id,version_number,role,port,computer_name.encode(),raknet_port)
        dummyMessage = struct.pack("<5s", b"DMMY\x00") 
        @Slot(QHostAddress,int)
        def signal_handler4test(myhost:QHostAddress , port):
            self.logger.debug("signal_handler4test host = %s:%s",myhost.toString(),port)
            self.recorded_port = port
            self.recorded_addr = myhost
            self.logger.info("got port and host address %s:%s, next: QEventLoop.quit()"
                             ,myhost.toString(),port)
            # loop.quit()
        
        self.reader.xPlaneAddrPortSignal.connect(signal_handler4test)
        #loop = QEventLoop()
        self.senderUdpSocket.writeDatagram(dummyMessage, 
                                self.reader.xplaneMulticastAddress, self.reader.xplaneMulticastPort)
        self.senderUdpSocket.writeDatagram(message, 
                                self.reader.xplaneMulticastAddress, self.reader.xplaneMulticastPort)
        #self.logger.debug("next: loop.exec()")
        #loop.exec()
        self.app.processEvents()
        self.assertTrue(self.recorded_port != None)
        self.assertTrue(self.recorded_addr != None)
        self.logger.debug("end of test_receive_becn_data")
                  
        

if __name__ == '__main__':
    unittest.main()