import turaev
import linkdiagram 

# Given a gauss code, this function constructs and returns a (multi)graph
# which is the 4-valent graph associated to the link projection associated
# to the code
def constr_graph(gc, is_link = False):
	length = len(gc)
	vertices = range(1, length / 2 + 1)
	edges = []
	for i in range(0, length):
		edges.append([gc[i][0],gc[(i + 1) % length][0]])
		edges.append([gc[(i + 1) % length][0],gc[i][0]])
	return Graph(vertices, edges)

# Given a raw gauss code (string), this function returns a reduced presentation 
# of the fundamental group of the associated Turaev surface
def fund_group(raw_code):
	gc = turaev.process_code(raw_code)
	if not linkdiagram.gc_is_valid(gc):
		raise Exception("Invalid Gauss code")
	graph = constr_graph(gc)
	print(graph.vertices)


# Class for 4-valent graphs associated to link projections.
class Graph:

	def __init__(self, vertices, edges):
		# self.dictionary = {}
		self.vertices = vertices
		self.edges = edges
