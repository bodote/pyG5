import sys
import logging
import time
import struct
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QUdpSocket, QHostAddress,QAbstractSocket
from PySide6.QtWidgets import   QApplication
from pyG5new.udpMulticastReader import UdpMulticastReader


class DataRefReader(QObject):
    drefUpdate = Signal(object)
    xplaneAddr = None
    xplanePort = None
   
    
    def __init__(self ): #udpMulticastReader:UdpMulticastReader, parent=None
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.senderUdpSocket = QUdpSocket()
        self.logger.debug("sender= QUdpSocket(); sender.stateChanged.connect(self.stateChangedSlotTest)")
        self.senderUdpSocket.stateChanged.connect(self.stateChangedSlot)
        # self.senderUdpSocket.connected.connect(self.connectedSlot)
        self.xplaneAddr = QHostAddress.LocalHost#udpMulticastReader.xplaneAddr
        self.xplanePort = 49000# udpMulticastReader.xplanePort
        assert self.xplaneAddr!=None
        self.connectXplane()
        return 
    
    @Slot(QAbstractSocket.SocketState)
    def stateChangedSlot(self,state):
        self.logger.debug("socket state changed {}".format(state))

    @Slot()
    def connectedSlot(self):
        self.logger.debug("socket state connected")
        
    def connectXplane(self):
        cmd = b"RREF\x00"
        freq = 30 
        idx = 1
        ref = "sim/cockpit/radios/nav1_dme_dist_m"
        message = struct.pack("<5sii400s", cmd, freq, idx, ref.encode())     
        self.senderUdpSocket.writeDatagram(message, 
                                self.xplaneAddr, self.xplanePort)
        self.logger.debug("after senderUdpSocket.writeDatagram to %s:%s",self.xplaneAddr,self.xplanePort)
        return
