import FD
import google

## @package buildgpb
# recursively scans a MessageTreeItem to build a protocol object.


## recursively scans a MessageTreeItem to build a protocol object.
class Builder:

	## constructor.
	# @param gpbobject the protobuf object that we add the results of our tree
	# walk to.
	# @param treeitem the treeitem where we start our tree traverse.
	def __init__(self, gpbobject, treeitem):
		self.add_fields(gpbobject, treeitem)

	def add_fields(self, gpbobject, treeitem):	
		for i in xrange(treeitem.childCount()):
			c=treeitem.child(i)
		
			# 2000 is hardcoded custom tree item id that we use for our
			# MessageTreeItem's
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
					

	


		
