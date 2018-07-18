# graph class


# some notational stuff:
# always have the edge touple in lexicographical order


class ColoredGraph:
	# self.dictionary = {}
	# self.vertices = []
	# self.edges = []

	def __init__(self):
		# self.dictionary = {}
		self.vertices = {}
		self.edges = {}
	
	def set_uncolored_vertices(self, vertex_list):	
		# order lexicographically
		vertex_list.sort()

		for vertex in vertex_list:
			self.vertices[tuple(vertex)] = []

	def set_uncolored_edges(self, edge_list, safe=False):
		if safe:
			if self.vertices == []:
				raise Exception("Empty vertex set, cannot check validity of edges.")
			# check whether edges are valid
			for edge in edge_list:
				if (not edge[0] in self.vertices) or (not edge[1] in self.vertices):
					raise Exception(str(edge_list)+" is invalid. "+str(edge)+" is not an edge with vertices in "+str(self.vertices))
		for edge in edge_list:
			self.edges[edge] = "None"

	def color_edge(self, edge, color):
		if edge in self.edges: self.edges[edge] = color
		else: raise Exception("Edge "+str(edge)+" does not exist.")

	def add_edge(self, node1, node2, color = "None"):
		self.edges[(tuple(min(node1, node2)), tuple(max(node1, node2)))] = color 

	def color_vertex(self, vertex, color):
		if vertex in self.vertices: self.vertices[vertex] += [color]
		else: raise Exception("Vertex "+str(vertex)+" does not exist.")

	def add_vertex(self, vertex, color="None"):
		if color == "None":	
			self.vertices[vertex] = []
		else: 
			self.vertices[vertex] = [color]

