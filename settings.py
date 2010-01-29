#!/usr/bin/env python
# vim:tw=120

## @file settings.py create or read the file \c .gpbedit in the current directory 

import sys, commands, os.path, ConfigParser
import google
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import FD

FD.init()

global loadfile, settings_file_name

## @var loadfile
# variable picked from the .gpbedit settings file for loading the gpb file.
loadfile=None

## @var settings_file_name
# the global name of the settings file (.gpbedit) in the current working directory.
settings_file_name=  ".gpbedit"
sys.path.append('.')


## a dialog that shows a QComboBox for picking the toplevel message (typically ILNMessage )
class ConfigDialog(QDialog):

	## @var messagewidget
	# the QComboBox that shows a popup of all message types.
	
	## constructor.
	# @param messages a list of Message types from the protocol file.
	# @param parent QWidget parent (typically None).
	def __init__(self, messages, module, parent=None):
		QDialog.__init__(self, parent)
		self.setWindowTitle("Pick a main message type")
		self.module=module

		layout = QVBoxLayout()
		self.setLayout(layout)

		label=QLabel()
		label.setText("Pick a main message as a container for all the other messages")
		layout.addWidget(label)

		self.messagewidget = QComboBox()
		for m in messages: self.messagewidget.addItem(m)
		layout.addWidget(self.messagewidget)


		label=QLabel()
		label.setText("Pick a main message and field for object identification")
		layout.addWidget(label)

		self.idmessagewidget = QComboBox()
		self.idmessagewidget.addItem("")
		for m in messages: self.idmessagewidget.addItem(m)
		layout.addWidget(self.idmessagewidget)
		QObject.connect(self.idmessagewidget, SIGNAL("currentIndexChanged(int)"),
			self.update_fields_widget)

		self.fieldswidget = QComboBox()
		layout.addWidget(self.fieldswidget)


		hl= QHBoxLayout()
		hl.addStretch()

		closebutton=QPushButton(self)
		closebutton.setText("&Choose")
		closebutton.setDefault(True)
		hl.addWidget(closebutton)

		layout.addLayout(hl)
		QObject.connect(closebutton, SIGNAL("clicked()"), self.accept)

	def update_fields_widget(self):
		self.fieldswidget.clear()
		messagetype = str(self.idmessagewidget.currentText())
		m, message = messagetype.split(".")
		ff=getattr(self.module, message).DESCRIPTOR.fields
		for x in ff:
			if x.type != FD.MESSAGE:
				self.fieldswidget.addItem(x.name)

	## which message got picked.
	# @return the value of the QComboBox
	# @todo We really should add an ok button or something, instead of just hitting the close X.

	def get_picked_message(self):
		return self.messagewidget.currentText()

	def get_id_info(self):
		if self.idmessagewidget.currentText() :
			m, message = str( self.idmessagewidget.currentText()).split(".")
			return ( message , str(self.fieldswidget.currentText()))
		else:
			return ( "", "")


## create a .gpbedit file in the current working directory.
def create_settings_file():
	global rootmessage, loadfile, settings_file_name
	qstrlist = QFileDialog.getOpenFileNames(None, "pick at least one .proto file", "", "proto files (*.proto)")
	filelist=[str(x) for x in qstrlist]
	protofiles = "||".join(filelist)

	compile_protofiles(protofiles)
	all_messages=[]
	for m in filelist:
		modulename = os.path.basename(m)[:-6] + "_pb2"  # strip .proto
		M = __import__(modulename)
		all_module_members = map(lambda n: (n,type( getattr(M,n))), dir(M))
		all_messages.extend( [modulename+"."+name for name,t  in all_module_members \
			if t == google.protobuf.reflection.GeneratedProtocolMessageType])

	d = ConfigDialog(all_messages, M)
	r=d.exec_()

	
	import ConfigParser
	config = ConfigParser.RawConfigParser()
	config.add_section("proto")
	config.set("proto", "protofiles", protofiles)
	config.set("proto", "rootmessage", d.get_picked_message())
	config.set("proto", "#loadfile", "<fill in your filename>")

	id_info = d.get_id_info()

	config.set("proto", "id_message", id_info[0])
	config.set("proto", "id_field", id_info[1])
	configfile=open(settings_file_name, "wb")
	config.write(configfile)
	configfile.close()


	info = QString("""
<html><body>
Created file <tt>%1</tt> in directory <tt>%2</tt>
using protofiles: <tt>%3</tt> <br>and toplevel message <tt>%4</tt>. 
<p>If you want to automatically load a gpb file next time
you run gpbedit.py add 
<pre>loadfile=&lt;filename&gt;</pre> to <tt>%1</tt>
</body></html>""").arg( ".gpbedit").arg( os.path.abspath(os.path.curdir)).arg(protofiles).arg(d.get_picked_message())


	msgbox = QMessageBox.information(None, "settings file created", info)


	
## load information from .gpbedit in the current directory	
def read_settings_file():
	global rootmessage, loadfile, settings_file_name, id_message, id_field
	
	config = ConfigParser.RawConfigParser( {'loadfile':None})
	try:
		okfiles = config.read(settings_file_name)
		if not okfiles:
			raise Exception()
	except:
		create_settings_file()
		okfiles = config.read(settings_file_name)

	try:
		loadfile=config.get('proto','loadfile')
	except:
		loadfile=None
	protofiles=config.get('proto', 'protofiles')
	rootmessage=config.get('proto', 'rootmessage')
	id_message=config.get("proto", "id_message")
	id_field=config.get("proto", "id_field")

	compile_protofiles(protofiles)
	import_proto()
	
## update settings file.
def update_settings_file(loadfile=None):
	print "update_settings_file", loadfile
	global rootmessage, settings_file_name, id_message, id_field
	
	config = ConfigParser.RawConfigParser( )
	try:
		okfiles = config.read(settings_file_name)
		if not okfiles:
			raise Exception()
	except:
		create_settings_file()
		okfiles = config.read(settings_file_name)

	if loadfile:
		config.set("proto", "loadfile", loadfile)
	
	configfile=open(settings_file_name, "wb")
	config.write(configfile)
	configfile.close()

## use protoc protobuf compiler to create _pb2.py files.
# @param protofiles list of protocol files
def compile_protofiles(protofiles):	
	for p in protofiles.split("||"):
		cmd="protoc --python_out=. -I\"%s\" \"%s\"" % (os.path.dirname(p), os.path.abspath(p))
		if sys.platform=='win32':
			pipe=os.popen(cmd,'r')
			output=pipe.read()
			status=pipe.close()
		else:		
			(status,output) = commands.getstatusoutput(cmd)
		if status :
			print cmd,"had error", output
			sys.exit(1)


## import the _pb2 file into the FD namespace.
# uses rootmessage typically something like jdsclient_protos_pb2.ILNMessage.

def import_proto():
	global gpb_module, rootmessage
	module, message = rootmessage.split(".")

	# import the module into the FD namespace
	gpb_module = __import__(module)
	all_module_members = map(lambda n: (n,type( getattr(gpb_module,n))), dir(gpb_module))

	return

	# the code below shows how to get all the messages inside the module.
	# just for information.
	messages = [(name) for name,t  in all_module_members \
		if t == google.protobuf.reflection.GeneratedProtocolMessageType]
	print messages

## get protobuf DESCRIPTOR by name
# @return the DESCRIPTOR object
def get_descriptor(name):
	global gpb_module
	d= getattr(gpb_module, name)
	return d.DESCRIPTOR
	
## get protobuf root DESCRIPTOR by name
# @return the DESCRIPTOR object
def gpb_root_descriptor():
	global gpb_module, rootmessage
	module, message = rootmessage.split(".")
	return get_descriptor(message)

## make a new gpb root, with no contents.
# @return the gpb object
def new_gpb_root():
	global gpb_module, rootmessage
	module, message = rootmessage.split(".")
	d= getattr(gpb_module, message)
	return d()
	


