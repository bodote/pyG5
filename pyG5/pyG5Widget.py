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

class pyG5Widget(QWidget):
    """Base class for the G5 wdiget view."""

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QWidget.__init__(self, parent)

        self.logger = logging.getLogger(self.__class__.__name__)

        """property name, default value"""
        propertyList = [
            ("altitudeHold", 0),
            ("altitudeVNAV", 0),
            ("navSrc", 0),
            ("apAltitude", 0),
            ("apVS", 0),
            ("apAirSpeed", 0),
            ("apState", 0),
            ("apMode", 0),
            ("fuelPress", 0),
            ("lowVolts", 0),
            ("oilPres", 0),
            ("parkBrake", 0),
            ("lowVacuum", 0),
            ("lowFuel", 0),
            ("fuelSel", 4),
            ("xpdrMode", 0),
            ("xpdrCode", 5470),
            ("trims", 0),
            ("flaps", 0),
            ("fuelpump", 0),
            ("carbheat", 0),
            ("gpsdmedist", 0),
            ("gpshsisens", 0),
            ("nav1type", 0),
            ("nav2type", 0),
            ("gpstype", 0),
            ("avionicson", 1),
            ("hsiSource", 0),
            ("nav1fromto", 0),
            ("nav2fromto", 0),
            ("gpsfromto", 0),
            ("nav1crs", 0),
            ("nav1gsavailable", 0),
            ("nav1gs", 0),
            ("nav2crs", 0),
            ("gpscrs", 0),
            ("nav2gsavailable", 0),
            ("nav2gs", 0),
            ("nav1dft", 0),
            ("nav2dft", 0),
            ("nav1bearing", 0),
            ("nav2bearing", 0),
            ("nav1dme", 0),
            ("nav2dme", 0),
            ("gpsdft", 0),
            ("gpsgsavailable", 0),
            ("gpsvnavavailable", 0),
            ("gpsgs", 0),
            ("groundTrack", 0),
            ("magHeading", 0),
            ("windDirection", 0),
            ("windSpeed", 0),
            ("rollAngle", 0),
            ("pitchAngle", 0),
            ("gs", 0),
            ("kias", 0),
            ("kiasDelta", 0),
            ("ktas", 0),
            ("altitude", 0),
            ("altitudeSel", 0),
            ("alt_setting", 1013),
            ("alt_setting_metric", 1),
            ("vh_ind_fpm", 0),
            ("turnRate", 0),
            ("slip", 0),
            ("headingBug", 0),
            ("vs", 30),
            ("vs0", 23),
            ("vfe", 88),
            ("vno", 118),
            ("vne", 127),
            ("engineRpm",0),
        ]

        def _make_setter(val):
            """Generate a setter function."""

            @wraps(val)
            def setter(inputVal):
                setattr(self, "_{}".format(val), inputVal)
                self.repaint()

            return setter

        for prop in propertyList:
            setattr(self, "_{}".format(prop[0]), prop[1])
            setattr(self, "{}".format(prop[0]), _make_setter(prop[0]))

    def setPen(self, width, color, style=Qt.PenStyle.SolidLine):
        """Set the pen color and width."""
        pen = self.qp.pen()
        pen.setColor(color)
        pen.setWidth(width)
        pen.setStyle(style)
        self.qp.setPen(pen)

    @Slot(dict)
    def drefHandler(self, retValues):
        """Handle the DREF update."""
        for idx, value in retValues.items():
            try:
                setattr(self, value[3], value[0])
            except Exception as e:
                self.logger.error("failed to set value {}: {}".format(value[5], e))

    def getNavTypeString(self, navType, navIndex):
        """getNavTypeString.

        Args:
            type: type number

        Returns:
            string
        """
        value = int(navType)

        if value == 0:
            return ""
        elif value == 3:
            return "VOR" + navIndex
        elif value >= 4:
            return "LOC" + navIndex

        logging.error("Failed to decode navtype")

