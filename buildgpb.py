import FD
import google

class Builder:
	def __init__(self, gpbobject, treeitem):
		print "Builder", treeitem
		self.add_fields(gpbobject, treeitem)

	def add_fields(self, gpbobject, treeitem):	
		for i in xrange(treeitem.childCount()):
			c=treeitem.child(i)
		
			if c.type() == 2000:
				fd=c.field
				g=getattr(gpbobject,c.get_fieldname())
				if fd.label == FD.REPEATED :
					self.add_fields(g.add(), c)
				else:
					self.add_fields(g, c)
			else:		
				fd=c.field_desc
				if fd.label== FD.REPEATED:
					g=getattr(gpbobject,fd.name)
					g.append(c.get_value())
					
				else:
					setattr(gpbobject,fd.name, c.get_value())
					

	


		
