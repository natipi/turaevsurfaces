# graph class


# some notational stuff:
# always have the edge touple in lexicographical order


class ColoredGraph:
	# self.dictionary = {}
	# self.vertices = []
	# self.edges = []

	def __init__(self):
		# self.dictionary = {}
		self.vertices = []
		self.edges = {}
	
	def set_vertices(vertices):	
		self.vertices = vertices
		# order lexicographically
		self.vertices.sort()

	def set_uncolored_edges(edge_list, safe=False):
		if safe:
			if self.vertices == []:
				raise Exception("Empty vertex set, cannot check validity of edges.")
			# check whether edges are valid
			for edge in edge_list:
				if (not edge[0] in self.vertices) or (not edge[1] in self.vertices):
					raise Exception(str(edge_list)+" is invalid. "+str(edge)+" is not an edge with vertices in "+str(self.vertices))
		for edge in edge_list:
			self.edges[edge] = "None"

	def color_edge(key, color):
		if key in self.edges: self.edges[key] = color
		else: raise Exception("Edge "+str(key)+" does not exist.")

	def add_edge(node1, node2, color = "None"):
		self.edges[(min(node1, node2), max(node1, node2))] = color 
