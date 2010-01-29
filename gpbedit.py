#!/usr/bin/env python
# vim:tw=120

## @package gpbedit
# the main entry point for the gpb editor.

## @mainpage
# tool to graphically edit a file based on a message structure defined in a google protocol buffers format

## @page interactivesession An interactive gpbedit.py session with idle
# <pre>
# >>> import google
# >>> import FD
# >>> import jdsclient_protos_pb2
# >>> message=jdsclient_protos_pb2.ILNMessage()
# >>> o=jdsclient_protos_pb2.PB_OBJECT()
# >>> print getattr(o, "autohide")
# 0
# >>> a=jdsclient_protos_pb2.PB_AUTOSIZE()
# >>> a
# <jdsclient_protos_pb2.PB_AUTOSIZE object at 0xb630570c>
# >>> a.parent_width
# False
# >>> a.parent_width=True
# >>> a
# <jdsclient_protos_pb2.PB_AUTOSIZE object at 0xb630570c>
# >>> a.parent_width
# True
# >>> al=jdsclient_protos_pb2.PB_ALIGNMENT()
# >>> al.v_align
# 1
# >>> al.v_align = al.LEFT
# >>> al.v_align
# 4
# >>> fd = al.DESCRIPTOR
# >>> fd
# <google.protobuf.descriptor.Descriptor object at 0xb61ba54c>
#
# >>> fd.fields_by_name
# {'v_align': <google.protobuf.descriptor.FieldDescriptor object at 0xb61ba48c>, 'h_align':
# <google.protobuf.descriptor.FieldDescriptor object at 0xb61ba4ac>}
# >>> fd.fields_by_name
# {'v_align': <google.protobuf.descriptor.FieldDescriptor object at 0xb61ba48c>, 'h_align':
# <google.protobuf.descriptor.FieldDescriptor object at 0xb61ba4ac>}
#
# >>> fielddescriptor=d['v_align']
# >>> fielddescriptor
# <google.protobuf.descriptor.FieldDescriptor object at 0xb61ba48c>
# >>> fielddescriptor.label
# 1
# >>> fielddescriptor.name
# 'v_align'
# >>> dir(fielddescriptor)
# ['CPPTYPE_BOOL', 'CPPTYPE_DOUBLE', 'CPPTYPE_ENUM', 'CPPTYPE_FLOAT', 'CPPTYPE_INT32', 'CPPTYPE_INT64', 'CPPTYPE_MESSAGE',
# 'CPPTYPE_STRING', 'CPPTYPE_UINT32', 'CPPTYPE_UINT64', 'GetOptions', 'LABEL_OPTIONAL', 'LABEL_REPEATED',
# 'LABEL_REQUIRED', 'MAX_CPPTYPE', 'MAX_LABEL', 'MAX_TYPE', 'TYPE_BOOL', 'TYPE_BYTES', 'TYPE_DOUBLE', 'TYPE_ENUM',
# 'TYPE_FIXED32', 'TYPE_FIXED64', 'TYPE_FLOAT', 'TYPE_GROUP', 'TYPE_INT32', 'TYPE_INT64', 'TYPE_MESSAGE', 'TYPE_SFIXED32',
# 'TYPE_SFIXED64', 'TYPE_SINT32', 'TYPE_SINT64', 'TYPE_STRING', 'TYPE_UINT32', 'TYPE_UINT64', '__class__', '__delattr__',
# '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__',
# '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_options',
# '_options_class_name', 'containing_type', 'cpp_type', 'default_value', 'enum_type', 'extension_scope', 'full_name',
# 'index', 'is_extension', 'label', 'message_type', 'name', 'number', 'type']
# >>> 
# >>> fielddescriptor.number
# 1
# >>> fielddescriptor.type
# 14
# >>> fielddescriptor.TYPE_ENUM
# 14
# 
# 
# 
# </pre>
# 

import sys
import SocketServer
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from debugwidget import *
from itemeditor import *

import google
import FD
import settings

global wanted_type
wanted_type="PB_OBJECT"
global wanted_field
wanted_field="id"

## scan object m looking for a certain field of a certain message
def scan(m):
	if not m : return ""
	for fd, o in m.ListFields():
		if fd.type == FD.MESSAGE :  
			if fd.label==FD.REPEATED :
				for i in range(len(o)):
					o1=getattr(m,fd.name)[i]
					return scan(o1)
			else:		
				o1=getattr(m,fd.name)
				return scan(o1)
		else:
			if m.DESCRIPTOR.name == settings.id_message:
				if fd.label == FD.REPEATED:
					for i in range(len(o)):
						o1=getattr(m, fd.name)[i]
						if fd.name==settings.id_field:
							return o1
				else:
					if fd.name==settings.id_field:
						return o
	return ""				

## tree item for items that represent a non-message field of a protobuf message object.
#
# this class is a subclass of QTreeWidgetItem and represents one node in the tree
class FieldTreeItem(QTreeWidgetItem):

	## @var field_desc 
	# the field descriptor corresponding to this tree item.

	## @var _value
	# the value of the field, a simple python value (number, string).



	## constructor
	# @param self self
	# @param field_desc google.protobuf.descriptor.FieldDescriptor object
	# @param value the value of a field for instance a number, boolean or enum value
	# @param parent QWidget parent
	def __init__(self, field_desc, value, parent):
		QTreeWidgetItem.__init__(self,parent, 2001)

		self.field_desc = field_desc
		if value != None:
			self.set_value(value)
		else:
			if field_desc.label == FD.REPEATED:
				self.set_value(None)
			else:
				self.set_value(field_desc.default_value)

	
	## return the value of the treewidget item.
	def get_value(self): 
		return self._value

	## set the visible value of the treewidget item.
	def set_value(self, value):
		self._value=value
		self.set_column_data()

	## set what is being shown in the columns of the QTreeWidget.
	def set_column_data(self):

		fd=self.field_desc
		t = fd.type

		# what is being shown depends on the type
		if t == FD.STRING:
			default_value=fd.default_value
			if fd.label == FD.REPEATED: default_value=""
			if self._value==None :  self._value=""
			self.setText(5,self._value)
		elif t==FD.ENUM:
			# protobuf enums
			if self._value == None: self._value = 0
			self.setText(5,fd.enum_type.values_by_number[self._value].name)
			if fd.label == FD.REPEATED: 
				default_value = fd.enum_type.values_by_number[0].name
			else:
				default_value = fd.enum_type.values_by_number[fd.default_value].name
		else:	
			# all kinds of numbers (int, float, ...)
			if fd.label == FD.REPEATED:
				default_value=""
			else:
				default_value=unicode(fd.default_value)
			self.setText(5,unicode(self._value))

		self.setText(0, fd.name)
		self.setText(1, FD.type_map[t].lower())
		self.setText(2, FD.label_map[fd.label].lower())
		self.setText(4,default_value)
		
	## get the field name of the associated protobuf object.
	def get_fieldname(self):
		return self.field_desc.name

## treewidget item that shows a protobuf message item.
class MessageTreeItem(QTreeWidgetItem):
	## @var field_desc 
	# the field descriptor corresponding to this tree item.

	## @var gpbobject
	# the gpbobject containing the information for this tree item

	## @var field
	# the field descriptor of the field in the containing message that refers to this message. 
	# Might be  None for the top level message.

	## @var required_fields
	# dictionary with as keys required field names and values the corresponding field descriptors

	## @var optional_fields
	# dictionary with as keys optional field names and values the corresponding field descriptors

	## @var repeated_fields
	# dictionary with as keys repeated field names and values the corresponding field descriptors


	## constructor
	# @param self self
	# @param field_desc google.protobuf.descriptor.FieldDescriptor object
	# @param field the field descriptor of the field in the containing message that refers to this message. 
	#	Might be  None for the top level message.
	# @param gpbobject the optional gpb message object that is used to create this MessageTreeItem .
	#    The presence of this parameter will recursively create more FieldTreeItem and MessageTreeItem instances
	# until all the stuff in the gpbobject is exhausted
	# @param parent QWidget parent
	def __init__(self, field_desc, field=None, gpbobject = None, parent=None):
		QTreeWidgetItem.__init__(self,parent, 2000)

		self.setExpanded(True)
		self.field_desc = field_desc
		self.gpbobject = gpbobject
		self.field=field

		self.createFieldCategories()
		if field :
			# set text of column 0 ('name') to the name of this message field ('clocks', 'text', 'text_properties', ...)
			self.setText(0,field.name)
			# set text of column 2 ('kind') to repeated, required or optional
			self.setText(2,FD.label_map[field.label].lower())
			self.setText(5, scan(gpbobject))
		else:	
			self.setText(0,"^^^")

			
		self.setText(1,self.field_desc.name)


		if self.gpbobject:
			# we're constructing this object from an existing gpb object
			for field, o in self.gpbobject.ListFields():
				if field.type == FD.MESSAGE :  
					if field.label==FD.REPEATED :
						for i in range(len(o)):
							o1=getattr(self.gpbobject,field.name)[i]
							MessageTreeItem (field.message_type, field, o1, self)
					else:		
						o1=getattr(self.gpbobject,field.name)
						MessageTreeItem (field.message_type, field, o1, self)
				else:
					if field.label == FD.REPEATED:
						for i in range(len(o)):
							o1=getattr(self.gpbobject, field.name)[i]
							FieldTreeItem(field, o1, self)
					else:
						FieldTreeItem(field, o, self)
		else:
			# we're constructing a brand new object, with default data
			self.setExpanded(True)
			for fieldname, field_desc in self.required_fields.items():
				if field_desc.type == FD.MESSAGE :  
					MessageTreeItem(field_desc.message_type, field_desc, None, self)
				else:	
					FieldTreeItem(field_desc, None, self)

	def get_fieldname(self):
		if not self.field : return None
		return self.field.name

	## create the tree dictionaries with fields of this message type. 
	#
	# each MessageTreeItem has three dictionairies, required_fields, optional_fields and repeated_fields.
	#
	def createFieldCategories(self):
		self.required_fields={}
		self.optional_fields={}
		self.repeated_fields={}
		for fieldname, fd in self.field_desc.fields_by_name.items():
			if fd.label == FD.OPTIONAL : 
				self.optional_fields[fieldname] = fd
			elif fd.label ==FD.REQUIRED : 
				self.required_fields[fieldname] = fd
			elif fd.label==FD.REPEATED: 
				self.repeated_fields[fieldname] = fd
			else:
				print "unknown label"
				sys.exit(1)

	## add a new child to a MessageTreeItem.
	# @param fieldname the name of the field that gets created.
	def add_child(self, fieldname):
		# fist find where in the widget tree to insert a new widgetitem.
		# preceding is a list of all items with name <fieldname>
		preceding = self.find_children_by_name(fieldname)
		if preceding: preceding=preceding[-1] # last child, we append our new item after this one

		# get the field descriptor for the new item.
		fd=self.field_desc.fields_by_name[fieldname]

		# create a new tree item depending on the type of the field descriptor.
		if fd.type == FD.MESSAGE :  
			c=MessageTreeItem(fd.message_type, fd, None, self)
		else:	
			c=FieldTreeItem(fd, None, self)
		
		self.move_child(c, preceding)
		editwidget.slot_treeitem_click(c,0)
		


		
	## move a new TreeWidget to its correct place. Also used for moving an item up or down.
	# @param child the child that needs to be moved
	# @param precedingchild the child after which we want to put the new child.
	def move_child(self, child, precedingchild):
		if not child.parent() : return
		p=child.parent()
		if not precedingchild: 
			# very first
			p.removeChild(child)
			p.insertChild(0,child)
		else:	
			i = p.indexOfChild(precedingchild)
			p.removeChild(child)
			p.insertChild(i+1,child)
		child.treeWidget().setCurrentItem(child)	
		self.treeWidget().emit_gpbupdate()


	## find siblings with same fieldname.
	# @return a list of siblings with the same field name. 
	def find_same_type_siblings(self):
		if not self.parent() : 
			return []
		return self.parent().find_children_by_name( self.field.name) 

	## Check if this child can be moved up or down.
	# @param dir 1:can child be moved down? -1: can sibling be moved up?
	# @return True if sibling can be moved up, False not.
	def move_by_one_enabled(self,dir):
		s = self.find_same_type_siblings()
		if not s or len(s)==1: 
			return None
		i=s.index(self)
		if (i==0 and dir == -1) or (i==len(s)-1 and dir==+1) :
			return None
		return s
		
	## move sibling by one in hierarchy.
	# @param dir 1 up -1 down
	def move_by_one(self, dir):
		s = self.move_by_one_enabled(dir)
		if not s: return
		p=self.parent()
		i=s.index(self)
		p.removeChild(self)
		p.insertChild(i+dir,self)
		self.treeWidget().setCurrentItem(self)	
		self.treeWidget().emit_gpbupdate()


	## return a list of treeitem children of a certain name. This is used for repeating items.
	# @param name the childs name you're looking for.
	def find_children_by_name(self,name):
		children=[]
		for i in xrange(self.childCount()):
			c=self.child(i)
			if c.get_fieldname() == name :
				children.append(c)
		return children
		

	## get first child with fieldname name.
	# @param name the name we're looling for.
	# @return Child or none.
	def find_child_by_name(self,name):
		for i in xrange(self.childCount()):
			c=self.child(i)
			if c.get_fieldname() == name :
				return c
		return None

		
## tree for whole gpb message.
class TreeWidget(QTreeWidget):
	## The container tree for all the gpb objects that we have created/destroyed.
	def __init__(self, parent=None):
		QTreeWidget.__init__(self, parent)
		self.filename = ""

	## TreeWidget will emit an gpbobject_updated signal.
	def emit_gpbupdate(self):
		self.emit(SIGNAL("gpbobject_updated(PyQt_PyObject)"), self)

	## save the internal tree to a gpb text file.
	def save_gpb(self):

		o=settings.new_gpb_root()
		topmessage=self.topLevelItem(0)
		buildgpb.Builder( o, topmessage )

		if not o.IsInitialized() : 
			msgBox = QMessageBox()
			msgBox.setText("The GPB Object tree is incomplete. This is a bug, The file can not be saved")
			msgBox._exec()
			return


		filename = QFileDialog.getSaveFileName(self, "save gpb file", self.filename)
		if not filename : return
		self.filename=filename

		
		f=open(filename,"w")
		f.write( text_format.MessageToString(o))
		f.close()

		settings.update_settings_file(loadfile=filename)

		
	## load a text gpb file into the tree widget.
	def open_gpb(self):
		filename = QFileDialog.getOpenFileName(self, "open gpb file", self.filename, "GPB files (*.gpb);;All files (*.*)")
		if not filename: return
		self.loadfile(filename)
		settings.update_settings_file(loadfile=filename)

	## load a text gpb file into the tree widget.
	# @param filename the name of the text based protobuf file.
	def loadfile(self,filename):
		self.clear_gpb()
		self.filename=filename
		f=open(filename, "r")
		gpb=settings.new_gpb_root()
		text_format.Merge( f.read(), gpb)
		f.close()

		self.create_toplevel(gpb)


	
	## clear the whole tree.
	def clear_gpb(self):
		global editwidget
		editwidget.no_edit()
		self.invisibleRootItem().removeChild( self.topLevelItem(0))
	
	## clear tree and insert the toplevel item.
	# @param gpb toplevel object or nothing.
	def create_toplevel(self, gpb=None):
		top=MessageTreeItem(settings.gpb_root_descriptor(), None, gpb)
		self.addTopLevelItem(top)
		self.expandItem(top)
		self.emit_gpbupdate()
	
	## start new empty tree.
	def start_with_empty_toplevel(self):
		self.clear_gpb()
		self.create_toplevel()

	


if __name__ == "__main__":
	FD.init()
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	layout = QHBoxLayout(mainwindow)
	mainwindow.setLayout(layout)


	treewidget = TreeWidget()
	treewidget.setWindowTitle("Google Protocol Object Editor")
	treewidget.setHeaderLabels( [ "Name" ,"Type" ,"Kind" ,"Label" ,"Default", "Value"])

	settings.read_settings_file()
	
	treewidget.create_toplevel()

	layout.addWidget(treewidget, 1)

	global editwidget
	editwidget = ItemEditor(mainwindow)

	rightvbox=QVBoxLayout()
	layout.addLayout(rightvbox)
	rightvbox.addWidget(editwidget)
	rightvbox.addStretch()

	debugwidget = DebugWidget(mainwindow)
	debugwidget.setMinimumSize(200,400)
	debugwidget.setMaximumWidth(300)

	rightvbox.addWidget(debugwidget)

	clearbutton=QPushButton("&clear whole tree", mainwindow)
	rightvbox.addWidget(clearbutton)

	savebutton=QPushButton("&save gpb file", mainwindow)
	rightvbox.addWidget(savebutton)

	openbutton=QPushButton("&open gpb file", mainwindow)
	rightvbox.addWidget(openbutton)



	QObject.connect( treewidget, SIGNAL("gpbobject_updated(PyQt_PyObject)"), debugwidget.slot_gpbobject_updated)

	QObject.connect(savebutton, SIGNAL("clicked()"), treewidget.save_gpb)	
	QObject.connect(openbutton, SIGNAL("clicked()"), treewidget.open_gpb)	
	QObject.connect(clearbutton, SIGNAL("clicked()"), treewidget.start_with_empty_toplevel)	

	editwidget.make_connections(treewidget)

	treewidget.setColumnWidth(0,220)
	treewidget.setColumnWidth(1,60)
	mainwindow.setMinimumSize(QSize(1000,800))

	mainwindow.show()

	if settings.loadfile: treewidget.loadfile(settings.loadfile)
		
	treewidget.emit_gpbupdate()


	sys.exit(app.exec_())
