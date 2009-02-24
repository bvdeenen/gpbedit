#!/usr/bin/python

from threading import Thread
import SocketServer, sys, struct


from PyQt4.QtGui import *
from PyQt4.QtCore import *


class Handler(SocketServer.BaseRequestHandler) :
	def setup(self):
		print self.client_address, 'connected'
		self.server.S.add_client(self)

	def handle(self):
		data = 'dummy'
		while data:
			try:
				data = self.request.recv(1024)
			except:
				self.finish()
				return
				

	def finish(self):
		print self.client_address,'disconnected'
		self.server.S.remove_client(self)


class Server(Thread):
	def __init__(self, ip, port ):
		Thread.__init__(self)
		self.clients=[]
		self.ip=ip
		self.port = port
		self.server = SocketServer.ThreadingTCPServer( (ip,port), Handler)
		self.server.S = self
	def add_client(self, client):
		self.clients.append(client)
		print self.clients
	def remove_client(self, client):
		if self.clients.count(client) :
			self.clients.remove(client)
		print self.clients
	def run(self):	
		self.server.serve_forever()	

	def push(self, data='hallo\n'):
		for client in self.clients:
			client.request.send(data)
			
	def pushgpb(self, gpbobject):
		msg=gpbobject.SerializeToString()
		ct = gpbobject.ByteSize()


		bytes= struct.pack("<l%ds" % (ct,) , ct, msg)
		print "packed message of ", ct, "bytes"

		deadclients=[]
		for client in self.clients:
			try:
				ct = client.request.send(bytes)
				print "transmitted", ct, "wanted to transmit", len(bytes)
			except:
				print "no client", client
				deadclients.append(client)
		
		for c in deadclients: self.remove_client(c)


	
if __name__=='__main__':
	app = QApplication(sys.argv)
	mainwindow=QWidget()
	layout = QVBoxLayout(mainwindow)
	mainwindow.setLayout(layout)
	serverpush=QPushButton("&tcp push ", mainwindow)
	layout.addWidget(serverpush)
	mainwindow.show()

	s=Server('',2003)
	QObject.connect(serverpush, SIGNAL("clicked()"), s.push)

	s.start()
	sys.exit(app.exec_())
