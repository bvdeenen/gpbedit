#!/usr/bin/python

import sys, struct, google

from socket import *
import settings

if __name__ == '__main__' :
	
	s=socket(AF_INET, SOCK_STREAM)
	s.connect( ('',5009) )
	settings.read_settings_file()

	while True:
		bytes=s.recv(4) # mx header
		if bytes < 0 : break
		mxct = struct.unpack("<l", bytes)[0]
		print mxct
		bytes= s.recv(mxct)


		gpb=settings.new_gpb_root()
		gpb.ParseFromString( bytes )
		print google.protobuf.text_format.MessageToString(gpb)






