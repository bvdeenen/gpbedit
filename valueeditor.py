# vim:tw=120
# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *
from google.protobuf import text_format

import __main__ 

class ValueEditor(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self,parent)
		vbox=QVBoxLayout(self)
		self.setLayout(vbox)
		label=QLabel(self)
		label.setText("ValueEditor")
		vbox.addWidget(label)

		self.namelabel=QLabel(self)
		vbox.addWidget(self.namelabel)

		self.typelabel=QLabel(self)
		vbox.addWidget(self.typelabel)

		self.editbox=QLineEdit(self)
		vbox.addWidget(self.editbox)
		vbox.addStretch()
	
		QObject.connect(self.editbox, SIGNAL("editingFinished()"),
			self.editFinished)

	def set_treewidget(self, widgetitem):
		self.widgetitem = widgetitem
		fd = widgetitem.field_desc
		container = widgetitem.parent().gpbitem
		descriptor=container.DESCRIPTOR
		self.fd = fd
		self.container= container

		t=__main__.type_map[self.fd.type]

		self.namelabel.setText(fd.name)
		self.typelabel.setText(t)
		if t=="TYPE_STRING" :
			self.editbox.setText( getattr(container, fd.name).decode('utf-8'))
		else:	
			self.editbox.setText( str(getattr(container, fd.name)))
		self.editbox.setFocus()	

	def editFinished(self) :
		v = unicode(self.editbox.text())
		t=__main__.type_map[self.fd.type]

		if  t == "TYPE_STRING" :
			setattr(self.container, self.fd.name, v.encode('utf-8'))

		elif t.find("INT") >= 0 :
			setattr(self.container, self.fd.name, int(v))
		else:	
			setattr(self.container, self.fd.name, float(v))
		self.widgetitem.set_column_data()
		self.widgetitem.treeWidget().emit_gpbupdate()




