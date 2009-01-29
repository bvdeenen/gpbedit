#!/usr/bin/env python
# vim:tw=120

import sys
import google

def read_settings_file(filename=".gpbedit"):
	#try:
	f=open(filename,"r")
	#except IOErr 
	global loadfile
	loadfile=""
	for l in f.readlines():
		l=l.strip()
		if not l or l.startswith("#") : continue

		name,value = l.split(":",1)
		name=name.strip()
		value=value.strip()

		if name == "rootmessage" :
			set_root_message(value)
		elif name=="protofile":
			import_proto(value)
		elif name=="loadfile":
			loadfile= value
	f.close()

	gpb_root = empty_root_message()	
	
def import_proto(protofile):
	global gpb_module, rootmessage, gpb_root, loadfile
	if protofile.endswith(".proto"): protofile = protofile[:-len(".proto")]
	gpb_module = protofile+"_pb2"

	gpb_module = __import__(gpb_module)
	all_module_members = map(lambda n: (n,type( getattr(gpb_module,n))), dir(gpb_module))
	messages = [(name) for name,t  in all_module_members \
		if t == google.protobuf.reflection.GeneratedProtocolMessageType]
	print messages

def set_root_message(message):
	global rootmessage
	rootmessage = message

def empty_root_message():
	global rootmessage, gpb_module
	return eval("gpb_module."+rootmessage+"()")


if __name__ == '__main__':
	read_settings_file()
