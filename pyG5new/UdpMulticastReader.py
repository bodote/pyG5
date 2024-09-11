import sys
import logging
import time
import struct
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QUdpSocket, QHostAddress,QAbstractSocket
from PySide6.QtWidgets import   QApplication


  

class UdpMulticastReader(QObject):
    xPlaneAddrPortSignal = Signal(QHostAddress, int)
    # xPlaneAddrPortSignal = Signal()
    
    xplaneMulticastAddress = QHostAddress("239.255.1.1")
    xplaneMulticastPort = 49707
    last_messageByteArray = None
  
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.udpReceiverSocket = QUdpSocket(self)
        self.udpReceiverSocket.stateChanged.connect(self.stateChangedSlot)
        self.udpReceiverSocket.connected.connect(self.connectedSlot)
        self.udpReceiverSocket.readyRead.connect(self.read_and_signal_xplane_addr_port)
        self.udpReceiverSocket.bind(QHostAddress.AnyIPv4, self.xplaneMulticastPort,
                         QUdpSocket.ShareAddress | QUdpSocket.ReuseAddressHint)
        if not self.udpReceiverSocket.joinMulticastGroup(self.xplaneMulticastAddress):
            self.logger.warning("Failed to join multicast group")
        
        self.logger.debug("UdpMulticastReader.__init__ ende")

    @Slot(QAbstractSocket.SocketState)
    def stateChangedSlot(self,state):
        self.logger.debug("socket state changed {}".format(state))

    @Slot()
    def connectedSlot(self):
        self.logger.debug("socket state connected")
        
    
    
    def read_and_signal_xplane_addr_port(self):
        self.logger.debug("read_and_signal_xplane_addr_port")
        while self.udpReceiverSocket.hasPendingDatagrams():
            datagram = self.udpReceiverSocket.receiveDatagram()
            messageByteArray = datagram.data().data()
            xplaneAddr = datagram.senderAddress()
            if (messageByteArray == self.last_messageByteArray) : 
                self.logger.info("duplicate message")
                continue
            self.last_messageByteArray = messageByteArray
            unpacked_tuple = [b"x"]
            try:
               unpacked_tuple = struct.unpack("<5sBiiIH500sH",messageByteArray)
               self.logger.debug("received %s ",unpacked_tuple[0])
            except:
                self.logger.info("no BECN in multicast Datagram")
            if unpacked_tuple[0] == b'BECN\x00':
                xplanePort = unpacked_tuple[5]
                self.xPlaneAddrPortSignal.emit(xplaneAddr,xplanePort)
                self.logger.debug("signal emitted: xplaneAddr=%s port=%s",xplaneAddr,xplanePort)
        self.udpReceiverSocket.leaveMulticastGroup(self.xplaneMulticastAddress)
        self.udpReceiverSocket.close()
        self.logger.debug("leaveMulticastGroup")

