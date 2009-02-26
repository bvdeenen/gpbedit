#!/usr/bin/env python
# vim:tw=120
from google.protobuf import text_format
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import settings
import buildgpb


class DebugWidget(QTextEdit):
	def __init__(self, parent=None):
		QTextEdit.__init__(self, parent)
		self.setReadOnly(True)

	# slot called when TreeWidget has updated the gpb_top object
	def slot_gpbobject_updated(self, treewidget):	
		topmessage=treewidget.topLevelItem(0)
		
		o=settings.new_gpb_root()

		buildgpb.Builder( o, topmessage )

		warning = ""
		if not o.IsInitialized() : warning = "WARNING, gpb object is incomplete\n"
		self.setText(warning + text_format.MessageToString(o))



