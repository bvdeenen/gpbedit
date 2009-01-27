#!/usr/bin/env python
# vim:tw=120

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from example_pb2 import *
from effects_pb2 import *
from rows_pb2 import *


from debugwidget import *
from itemeditor import *

global type_map, label_map, gpb_top
type_map={}
label_map={}

# return a dictionary with value:name pairs for constants in a field object
# like 
# {1: 'TYPE_DOUBLE', 2: 'TYPE_FLOAT', 3: ...
def create_value_map(object,prefix):
	M={}
	types = [(getattr(object,m),m) for m in dir(object) \
		if not callable(getattr(object,m)) and m.startswith(prefix)]
	for key,value in types:
		M[key]=value
	return M	


class TreeItem(QTreeWidgetItem):
	def __init__(self, descriptor, parent=None, labels=[]):
		QTreeWidgetItem.__init__(self,parent)
		self.itemData = descriptor
	# analyze the structure of a gpb message descriptor and create TreeItems
	# based on that structure
	#def analyze_message(self,descriptor, parent, l=0):
		if not labels:
			self.setText(0,descriptor.name)
		else:
			for i,l in enumerate(labels): self.setText(i,str(l))

		if not descriptor: return
		if not hasattr(descriptor,'fields_by_number'): return

		global type_map, label_map

		fields = descriptor.fields_by_number
		for key,value in fields.items():

			if not type_map: type_map=create_value_map(value,"TYPE_")
			if not label_map: label_map=create_value_map(value,"LABEL_")

			if value.message_type: typename = value.message_type.name
			elif value.enum_type: typename = value.enum_type.name
			else: typename = type_map[value.type]

			if value.default_value : 
				if value.enum_type:
					default_value = value.enum_type.values_by_number[value.default_value].name
				else:	
					default_value=str(value.default_value)
			else: 
				default_value=""

			labels=[value.name, value.type,typename,label_map[value.label], default_value]
			# recurse
			if ( value.message_type ) :
				TreeItem(value.message_type, self,labels)
			else:	
				TreeItem(value,self, labels)
			#child.show_enum(value.enum_type, child, l+4)


class TreeWidget(QTreeWidget):
	def __init__(self, parent=None):
		QTreeWidget.__init__(self, parent)
	def emit_gpbupdate(self):
		global gpb_top
		self.emit(SIGNAL("gpbobject_updated(PyQt_PyObject)"), gpb_top)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	layout = QHBoxLayout(mainwindow)
	mainwindow.setLayout(layout)

	gpb_top = ILNMessage()
	movie = gpb_top.movies.add()

	widget = TreeWidget()
	widget.setWindowTitle("Simple Tree Model")
	widget.setHeaderLabels( [ "Name" ,"Type" ,"Kind" ,"Label" ,"Default"])
	widget.addTopLevelItem(TreeItem(gpb_top.DESCRIPTOR))

	layout.addWidget(widget)

	editwidget = ItemEditor(mainwindow)

	rightvbox=QVBoxLayout()
	layout.addLayout(rightvbox)
	rightvbox.addWidget(editwidget)
	rightvbox.addStretch()

	debugwidget = DebugWidget(mainwindow)
	rightvbox.addWidget(debugwidget)


	QObject.connect( widget, SIGNAL("gpbobject_updated(PyQt_PyObject)"),
		debugwidget.slot_gpbobject_updated)

	editwidget.make_connections(widget)

	mainwindow.show()
	widget.emit_gpbupdate()

	mainwindow.setMinimumSize(QSize(600,400))
	sys.exit(app.exec_())
