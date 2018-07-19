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



# from collections import defaultdict
# from heapq import *

# def dijkstra(edges, f, t):
#     g = defaultdict(list)
#     for l,r,c in edges:
#         g[l].append((c,r))

#     q, seen, mins = [(0,f,())], set(), {f: 0}
#     while q:
#         (cost,v1,path) = heappop(q)
#         if v1 not in seen:
#             seen.add(v1)
#             path = (v1, path)
#             if v1 == t: return (cost, path)

#             for c, v2 in g.get(v1, ()):
#                 if v2 in seen: continue
#                 prev = mins.get(v2, None)
#                 next = cost + c
#                 if prev is None or next < prev:
#                     mins[v2] = next
#                     heappush(q, (next, v2, path))

#     return float("inf")

def shortestpath(graph, a, b, visited = []):
	possible_steps = []
	possible_paths = []

	for edge in graph.edges.keys():
		if a in edge:
			possible_steps += [edge]
	for edge in possible_steps:
		if b in edge:
			return [edge]
		else:
			other = list(edge)
			other.remove(a)
			new_a = other[0]
			if not (new_a in visited):
				possible_paths += [[edge] + shortestpath(graph, new_a, b, visited + [a])]

	if len(possible_paths) == 0:
		# print "currently at: "+str(a)
		# print "visited: "+str(visited)
		# print "possible steps: "+str(possible_steps)
		return [(0,0)]*(len(graph.vertices) + 1) 

	return min(possible_paths, key=len)

