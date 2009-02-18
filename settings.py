#!/usr/bin/env python
# vim:tw=120

import sys, commands, os.path
import google

global loadfile
loadfile=None

def read_settings_file(filename=".gpbedit"):
	global rootmessage
	f=open(filename,"r")
	global loadfile
	loadfile=""
	for l in f.readlines():
		l=l.strip()
		if not l or l.startswith("#") : continue

		name,value = l.split(":",1)
		name=name.strip()
		value=value.strip()

		if name == "rootmessage" :
			rootmessage = value
			import_proto()
		elif name=="protofiles":
			for p in value.split():
				cmd="protoc --python_out=. -I%s %s" % (os.path.dirname(p), p)
				(status,output) = commands.getstatusoutput(cmd)
				if status :
					print cmd,"had error", output
					sys.exit(1)
				else:
					print cmd, output
		elif name=="loadfile":
			loadfile= value
	f.close()

	gpb_root = empty_root_message()	
	
def import_proto():
	global gpb_module, rootmessage
	module, message = rootmessage.split(".")

	gpb_module = __import__(module)
	all_module_members = map(lambda n: (n,type( getattr(gpb_module,n))), dir(gpb_module))
	messages = [(name) for name,t  in all_module_members \
		if t == google.protobuf.reflection.GeneratedProtocolMessageType]
	print messages

def empty_root_message():
	global gpb_module
	module, message = rootmessage.split(".")
	return eval("gpb_module."+ message+"()")


if __name__ == '__main__':
	read_settings_file()
