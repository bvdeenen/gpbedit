#!/usr/bin/env python
# vim:tw=120

## @package debugwidget
# shows debugging output from protobuf.
from google.protobuf import text_format
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import settings
import buildgpb


## widget that shows json like text of current gpb object.
class DebugWidget(QTextEdit):
	## constructor.
	def __init__(self, parent=None):
		QTextEdit.__init__(self, parent)
		self.setReadOnly(True)

	# slot called when TreeWidget has updated the gpb_top object
	# @param treewidget the top of the tree.
	def slot_gpbobject_updated(self, treewidget):	
		topmessage=treewidget.topLevelItem(0)
		
		o=settings.new_gpb_root()

		buildgpb.Builder( o, topmessage )

		warning = ""
		if not o.IsInitialized() : warning = "WARNING, gpb object is incomplete\n"
		self.setText(warning + text_format.MessageToString(o))



