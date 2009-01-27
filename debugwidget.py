#!/usr/bin/env python
# vim:tw=120
from google.protobuf import text_format
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *



class DebugWidget(QLabel):
	def __init__(self, parent=None):
		QLabel.__init__(self, parent)
	# slot called when TreeWidget has updated the gpb_top object

	def slot_gpbobject_updated(self, gpb_top):	
		print "hoi"
		self.setText(text_format.MessageToString(gpb_top.itemData))


