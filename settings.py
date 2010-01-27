#!/usr/bin/env python
# vim:tw=120

import sys, commands, os.path, ConfigParser
import google
from PyQt4.QtGui import *
from PyQt4.QtCore import *

global loadfile, settings_file_name
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
	def __init__(self, messages, parent=None):
		QDialog.__init__(self, parent)
		layout = QVBoxLayout()

		self.messagewidget = QComboBox()

		for m in messages: self.messagewidget.addItem(m)
		layout.addWidget(self.messagewidget)
		self.setLayout(layout)
		self.setWindowTitle("Pick a main message type")

	## which message got picked.
	# @return the value of the QComboBox
	# @todo We really should add an ok button or something, instead of just hitting the close X.

	def get_picked_message(self):
		return self.messagewidget.currentText()


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

	d = ConfigDialog(all_messages)
	r=d.exec_()

	
	import ConfigParser
	config = ConfigParser.RawConfigParser()
	config.add_section("proto")
	config.set("proto", "protofiles", protofiles)
	config.set("proto", "rootmessage", d.get_picked_message())
	configfile=open(settings_file_name, "wb")
	config.write(configfile)
	configfile.close()



	
def read_settings_file():
	global rootmessage, loadfile, settings_file_name
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

	compile_protofiles(protofiles)
	import_proto()
	
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
def import_proto():
	global gpb_module, rootmessage
	module, message = rootmessage.split(".")

	gpb_module = __import__(module)
	all_module_members = map(lambda n: (n,type( getattr(gpb_module,n))), dir(gpb_module))
	messages = [(name) for name,t  in all_module_members \
		if t == google.protobuf.reflection.GeneratedProtocolMessageType]
	#print messages

def get_descriptor(name):
	global gpb_module
	d= getattr(gpb_module, name)
	return d.DESCRIPTOR
	
def gpb_root_descriptor():
	global gpb_module, rootmessage
	module, message = rootmessage.split(".")
	return get_descriptor(message)

def new_gpb_root():
	global gpb_module, rootmessage
	module, message = rootmessage.split(".")
	d= getattr(gpb_module, message)
	return d()
	


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	mainwindow.show()
	read_settings_file()
