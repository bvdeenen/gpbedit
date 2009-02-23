import FD
import google

class Builder:
	def __init__(self, gpbobject, treeitem):
		self.add_fields(gpbobject, treeitem)

	def add_fields(self, gpbobject, treeitem):	
		for fieldname, fd in gpbobject.DESCRIPTOR.fields_by_name.items():
			c=treeitem.find_child_by_name(fieldname)
			if c:
				if fd.type == FD.MESSAGE :
					g=getattr(gpbobject,fieldname)
					if fd.label == FD.REPEATED :
						self.add_fields(g.add(), c)
					else:
						self.add_fields(g, c)
				else:		
					if fd.label== FD.REPEATED:
						g=getattr(gpbobject,fieldname)
						g.append(c.get_value())
						
					else:
						setattr(gpbobject,fieldname, c.get_value())
					

	


		
