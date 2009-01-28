#!/usr/bin/env python
# vim:tw=120
from google.protobuf import text_format
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class DebugWidget(QTextEdit):
	def __init__(self, parent=None):
		QTextEdit.__init__(self, parent)
		self.setReadOnly(True)

	# slot called when TreeWidget has updated the gpb_top object
	def slot_gpbobject_updated(self, gpb_top):	
		self.setText(text_format.MessageToString(gpb_top.gpbitem))


