#!/usr/bin/env python
# vim:tw=120

import sys
import google

def read_settings_file(filename=".gpbedit"):
	f=open(filename,"r")
	global protofiles, rootmessage, gpb_root
	protofiles=[]
	for l in f.readlines():
		l=l.strip()
		if not l or l.startswith("#") : continue

		name,value = l.split(":",1)
		name=name.strip()
		value=value.strip()

		if name == "rootmessage" :
			rootmessage = value
		elif name=="protofile":
			if value.endswith(".proto"): value = value[:-len(".proto")]
			protofiles.append(value+"_pb2")
	f.close()

	g=globals()
	for protofile in protofiles :
		print "import "+ protofile
		g[protofile] = __import__(protofile)
	gpb_root = empty_root_message()	
	
def empty_root_message():
	global rootmessage
	return eval(rootmessage+"()")


if __name__ == '__main__':
	read_settings_file()
	print dir()
