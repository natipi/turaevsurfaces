### This is some code which computes the fundamental group of the Turaev surface 
### of a given (potentially virtual) knot Gauss code. Support for links on the to do list.

import copy

# Performs all trivial type 1 reidemeister simplifications
def reduce_code(gc):
	i = 0
	while i < len(gc) - 1:
		j = (i + 1) % len(gc)
		if gc[i][0] == gc[j][0]:
			gc = gc[0:i] + gc[j + 1:]
		else: 
			i += 1
	if len(gc) > 0:
		if gc[-1][0] == gc[0][0]:
			gc = gc[1:-1]
	return gc

# Processes raw gauss code inputed as a string into a list of lists
def process_code(raw_code):
	raw_code_list = raw_code.split(',')
	gc = []
	for raw_entry in raw_code_list:
		length = len(raw_entry)
		proc_entry = [int(raw_entry[0:(length - 2)]), raw_entry[(length - 2): (length - 1)], raw_entry[(length - 1) : length]]
		gc.append(proc_entry)
	gc = reduce_code(gc)
	return gc

# Checks if processed Gauss code is valid
def gc_is_valid(gc):
	length = len(gc)
	if (length % 2) != 0:
		return False
	num_vert = 0
	cross_type = ''
	writhe = ''
	for i in range(1, length / 2 + 1):
		for j in range(0, length):
			if gc[j][0] == i:
				num_vert += 1
				if num_vert == 1:
					cross_type = gc[j][1]
					writhe = gc[j][2]
					if not (writhe == '+' or writhe == '-'):
						return False
				else:
					if not writhe == gc[j][2]:
						return False
					if not((cross_type == 'O' and gc[j][1] == 'U') or (cross_type == 'U' and gc[j][1] == 'O')):
						return False
		if num_vert != 2:
			return False
		num_vert = 0
	return True

# Given a gauss code, this function constructs and returns a (directed multi)graph
# which is the 4-valent graph associated to the link projection associated
# to the code
def constr_graph(gc, is_link = False):
	length = len(gc)
	vertices = range(1, length / 2 + 1)
	edges = []
	for i in range(0, length):
		edges.append([gc[i],gc[(i + 1) % length]])
	return Graph(vertices, edges)

# Returns a set of edges in the (connected) graph which correspond to circles in the
# bouqet which is gotten by collapsing the maximal tree with root the vertex 1 to 
# a point
def constr_bouqet(graph):
	num_verts = len(graph.vertices)
	next_verts = [1]
	prev_verts = []
	traversed_verts = [1]
	bouqet = graph.edges
	while len(next_verts) > 0:
		prev_verts = next_verts
		next_verts = []
		for vert in prev_verts:
			for arc in list(bouqet):
				if (arc[0][0] == vert) and (arc[1][0] not in traversed_verts):
					bouqet.remove(arc)
					next_verts.append(arc[1][0])
					traversed_verts.append(arc[1][0])
				elif (arc[1][0] == vert) and (arc[0][0] not in traversed_verts):
					bouqet.remove(arc)
					next_verts.append(arc[0][0])
					traversed_verts.append(arc[0][0])
	return bouqet

# Takes in a (processed) Gauss code graph, returning the cycles in the Turaev
# state smoothing in the form of lists of edges (arcs) in the graph
def constr_turaev_state(graph):
	a_smoothing, b_smoothing = [], []
	for smoothing_type in ["a", "b"]:
		edges = copy.deepcopy(graph.edges)
		for starting_edge in edges:
			if starting_edge in edges:
				forward = True
				loop = []
				prev_edge = starting_edge
				next_edge = []
				while next_edge != starting_edge:
					prev_edge.append(forward)
					loop.append(prev_edge)
					if forward:
						if (smoothing_type == "a" and prev_edge[1][2] == '+') or (smoothing_type == "b" and prev_edge[1][2] == '-'):
							for edge in edges:
								if edge[0] == [prev_edge[1][0], 'U' if prev_edge[1][1] == 'O' else 'O', '+' if prev_edge[1][2] == '+' else '-']:
									next_edge = edge
									break
						else:
							for edge in edges:
								if edge[1] == [prev_edge[1][0], 'U' if prev_edge[1][1] == 'O' else 'O', '+' if prev_edge[1][2] == '+' else '-']:
									next_edge = edge
									forward = False
									break
					else: 
						if (smoothing_type == "a" and prev_edge[0][2] == '+') or (smoothing_type == "b" and prev_edge[0][2] == '-'):
							for edge in edges:
								if edge[1] == [prev_edge[0][0], 'U' if prev_edge[0][1] == 'O' else 'O', '+' if prev_edge[0][2] == '+' else '-']:
									next_edge = edge
									break
						else:
							for edge in edges:
								if edge[0] == [prev_edge[0][0], 'U' if prev_edge[0][1] == 'O' else 'O', '+' if prev_edge[0][2] == '+' else '-']:
									next_edge = edge
									forward = True
									break
					if prev_edge == next_edge:
						raise Exception("Mayday, mayday: coder's smoothing skills ain't shit")
					prev_edge = next_edge
				if smoothing_type == "a": a_smoothing.append(loop)
				else: b_smoothing.append(loop)
				edges = [edge for edge in edges if edge not in loop]
		edges = copy.deepcopy(graph.edges)
	print("a_smoothing =") 
	print a_smoothing
	print("\n b_smoothing=")
	print b_smoothing
# Given a raw Gauss code (string), this function returns a reduced presentation 
# of the fundamental group of the associated Turaev surface
def fund_group(raw_code):
	gc = process_code(raw_code)
	if not gc_is_valid(gc):
		raise Exception("Invalid Gauss code")
	graph = constr_graph(gc)
	constr_turaev_state(graph)
	bouqet = constr_bouqet(graph)
	


# Class for 4-valent graphs associated to link projections.
class Graph:

	def __init__(self, vertices, edges):
		# self.dictionary = {}
		self.vertices = vertices
		self.edges = edges
