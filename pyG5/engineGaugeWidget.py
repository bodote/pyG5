import logging

from math import cos, radians, sin, sqrt, floor
from functools import wraps

from PySide6.QtCore import (
    QLine,
    QPoint,
    QPointF,
    QRectF,
    QLineF,
    Qt,
    Slot,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QPainter,
    QPolygonF,
    QColor,
    QLinearGradient,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from pyG5.pyG5Widget import pyG5Widget


class engineGaugeWidget(pyG5Widget):
    """Generate G5 wdiget view."""

    engineGWidth=200
    engineGHeight=120
    rpmMaxInverse=1/2800

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        pyG5Widget.__init__(self, parent)
    
    def paintEvent(self, event):
        """Paint the widget."""
        self.qp = QPainter(self)

        # Draw the background
        self.setPen(1, Qt.GlobalColor.black)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawRect(0, 0, self.engineGWidth, self.engineGHeight)

        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))

        font = self.qp.font()
        font.setPixelSize(30)
        font.setBold(True)
        self.qp.setFont(font)

        # engineRpm Tachometer
        rpmRadius = 40
        rpmCenterX = 20+rpmRadius
        rpmCenterY = 20+rpmRadius
        redArcDegree=45
        greenArcDegrees=45
        whiteArcDegrees=45+90
        endRedDegree=0

        font = self.qp.font()
        font.setPixelSize(16)
        font.setBold(False)
        self.qp.setFont(font)
        self.setPen(1, Qt.GlobalColor.white)
        self.qp.drawText(
            QRectF(
                rpmCenterX ,
                rpmCenterY+20 ,
                80,
                40,
            ),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            "{} rpm".format(self._engineRpm),
        )

        self.qp.translate(rpmCenterX, rpmCenterY)
        
        self.setPen(1, Qt.GlobalColor.white)
        self.qp.drawArc(
            -rpmRadius,
            -rpmRadius,
            2 * rpmRadius,
            2 * rpmRadius,
            (endRedDegree+redArcDegree+greenArcDegrees)*16,
            (endRedDegree+whiteArcDegrees) * 16,
        )

        self.setPen(4, Qt.GlobalColor.green)
        self.qp.drawArc(
            -rpmRadius,
            -rpmRadius,
            2 * rpmRadius,
            2 * rpmRadius,
            (endRedDegree+redArcDegree)*16,
            (endRedDegree+greenArcDegrees) * 16,
        )
        self.setPen(4, Qt.GlobalColor.red)
        self.qp.drawArc(
            -rpmRadius,
            -rpmRadius,
            2 * rpmRadius,
            2 * rpmRadius,
            -endRedDegree*16,
            redArcDegree * 16,
        )
        rpmPeripheralMarkers = [
            90,
            135,
            180,
            225,
            270,
            315,
        ]
        self.setPen(2, Qt.GlobalColor.white)

        for marker in rpmPeripheralMarkers:
            self.qp.rotate(-marker)
            self.qp.drawLine(0, rpmRadius, 0, rpmRadius+10)
            self.qp.rotate(marker)

        # needle
        needleAngle = self._engineRpm*self.rpmMaxInverse*225+45
        self.qp.rotate(needleAngle)
        self.qp.drawLine(0, 0, 0, rpmRadius-5)
        self.qp.rotate(-needleAngle)
        
        self.qp.end()
