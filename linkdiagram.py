# The linkdiagram class
# Hopefully, the link diagram class will eventually inherit from Sage's Link
# class, so that we can do Khovanov homology computations and such. For now, 
# it stands alone. 
# Eventually, two classes will inherit from LinkDiagram. The planardiagram
# class will pertain to classical diagrams, and the VirtualDiagram class
# will correspond to (possibly classical) diagrams with virtual crossings
# All of these use reduced Gauss codes (no obvious RI moves)

import turaev
import graph

from itertools import izip
from copy import deepcopy # copy lists

# go through all pairs of a list
def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)

# the cycles are lists
# returns whether they abut at a crossing
def abut(cycle1, cycle2):
	for i in cycle1:
		if i in cycle2: return True
	return False

# the cycles are lsits
# returns whether they share an arc
def share_arc(cycle1, cycle2):
	n = len(cycle1)
	m = len(cycle2)
	i = 0
	while i < n:
		# arc = cycle1[i:(i + 2) % n]
		# wanna find this arc in cycle2
		j = turaev.lst_find(cycle1[i], cycle2)
		k = turaev.lst_find(cycle1[i], cycle2, j+1)
		if j == -1 and k == -1: 
			i += 1
		elif j >= 0:
			if (cycle2[(j + 1) % m] == cycle1[(i + 1) % n]) or (cycle2[(j - 1) % m] == cycle1[(i + 1) % n]): 
				return True
			else: 
				i += 1
		elif k >= 0:
			if (cycle2[(k + 1) % m] == cycle1[(i + 1) % n]) or (cycle2[(k - 1) % m] == cycle1[(i + 1) % n]): 
				return True
			else: 
				i += 1
	return False

# returs the actual arc which they share
def share_which_arc(cycle1, cycle2):
	n = len(cycle1)
	m = len(cycle2)
	i = 0
	while i < n:
		# arc = cycle1[i:(i + 2) % n]
		# wanna find this arc in cycle2
		j = turaev.lst_find(cycle1[i], cycle2)
		k = turaev.lst_find(cycle1[i], cycle2, j+1)
		if j == -1 and k == -1: 
			i += 1
		elif j >= 0:
			if (cycle2[(j + 1) % m] == cycle1[(i + 1) % n]) or (cycle2[(j - 1) % m] == cycle1[(i + 1) % n]): 
				if i + 2 >= n: return cycle1[i:] + cycle1[:(i+2)%n]
				else: return cycle1[i:i+2]
			else: 
				i += 1
		elif k >= 0:
			if (cycle2[(k + 1) % m] == cycle1[(i + 1) % n]) or (cycle2[(k - 1) % m] == cycle1[(i + 1) % n]): 
				if i + 2 >= n: return cycle1[i:] + cycle1[:(i+2)%n]
				else: return cycle1[i:i+2]
			else: 
				i += 1
	return []

# decomposes cycle into a sum of elements
# every time we find a repeated crossing that is a valid split (i.e. is in "splits") 
# in cycle, we decompose along it
def decompose(cycle, splits):
	found = False
	i = 0
	n = len(cycle)
	# while we haven't found a repeated element
	while not found and i < n:
		j = turaev.lst_find(cycle[i], cycle, i+1)
		if j != -1 and cycle[j] in splits: 
			found = True
		else: 
			i += 1 
	# if no repeats, return cycleq
	if i == n: 
		return [cycle]
	else:
		return decompose(cycle[i:j], splits) + decompose(cycle[j:] + cycle[:i], splits)


# Checks if Gauss code is valid
# TODO: could be made way more efficient. Right now I'm going through each pair 
#       of numbers twice
def str_gc_is_valid(gc):
	i = 0
	n = len(gc)
	while i < n:
		# Find other instance of number i
		j = max(gc.find(gc[i], 0, i), gc.find(gc[i], i+1, n))
		if j < 0: return False
		if gc[i][2] != gc[j][2]: return False
		if code[i+1] != code[j+1]: return False
		i += 2
	return True

def lst_gc_is_valid(gc):
	i = 0
	n = len(gc)
	while i < n:
		j = max(find_crossing(gc[i], gc, 0, i), find_crossing(gc[i], gc, i+1, n))
		if j < 0: return False
		if code[i][-1] != code[j][-1]: return False
	return True

# reduce str gc
# def reduce(gc):
# 	i = 0 
# 	while i < len(gc) - 2:
# 		j = (i + 2) % len(gc)
# 		if gc[i] == gc[j]: 
# 			gc = gc[0:i] + gc[j + 2:]
# 		else:
# 			i += 2
# 	if gc[-2] == gc[0]:
# 		gc = gc[2:-2]
# 	return gc

# takes in lst gc and reduces it

def turaev_orientable(gc, length):
	first_incid = -1
	
	for i in range(1, length / 2 + 1):
		for j in range(0, length):
			if first_incid == -1 and gc[j][0] == i:
				first_incid = j
			elif first_incid != -1 and gc[j][0] == i:
				if (first_incid - j) % 2 == 0:
					return False
				first_incid = -1
				break
	return True

# makes a diagram alternating by changing crossings (and writhe when crossing type [over <-> under] is changed)
# takes in lst format gauss code
def make_alternating(gc):
	# gc = turaev.process_code(gc)
	length = len(gc)
	if not turaev_orientable(gc, length):
		raise Exception("The following Gauss code was attempted to be made alternating:" + gc + ". It is not orientable.")
	for i in range(0, length / 2):
		if gc[2 * i][1] == 'U':
			gc[2 * i][1] = 'O'
			if gc[2 * i][2] == '+':
				gc[2 * i][2] = '-'
			else:
				gc[2 * i][2] = '+'
 		if gc[2 * i + 1][1] == 'O':
			gc[2 * i + 1][1] = 'U'
			if gc[2 * i + 1][2] == '+':
				gc[2 * i + 1][2] = '-'
			else:
				gc[2 * i + 1][2] = '+'
	return gc


# forgets overs and unders, i.e. turns Gauss code from a "1U+2O-" format to a 
# "1+2-" format
# def forget_crossings(gc):

def test(gc):
	gc = turaev.process_code(gc)
	# print turaev.find_smoothing(gc, "a")

# def gc_is_virtual(gc):


class LinkDiagram:
	# Class variables shared by all elements of the class
	# none for now

	# initialization function
	# takes in a Gauss code, and an optional safe option. If you initialize with
	# the safe option, it verifies that your Gauss code is valid
	def __init__(self, gc, safe = False):
		if safe:
			if not gc_is_valid(gc):
				raise Exception("Invalid Gauss Code " + gc)

		self.gauss_code = turaev.reduce_code(gc)
		self.a_state = turaev.find_smoothing(gc, "a")
		self.b_state = turaev.find_smoothing(gc, "b")

	def turaev_genus(self):
		return 0.5*(turaev.crossing_number(self.gauss_code) - len(turaev.find_smoothing(self.gauss_code, "a")) - len(turaev.find_smoothing(self.gauss_code, "b")) + 2)

# Classical link diagrams
class PlanarDiagram(LinkDiagram):
	# self.dual_graph = graph.ColoredGraph()
 
	def build_dual_graph(self):
		# lists are passed by reference so I had to use deepcopy to pass by value
		gc_alter = make_alternating(deepcopy(self.gauss_code))
		# print str(gc_alter)
		altern_a_smthing = turaev.find_smoothing(gc_alter, "a")
		altern_b_smthing = turaev.find_smoothing(gc_alter, "b")
		# print "Alternating a smoothing: "+str(altern_a_smthing)
		# print "Alternating b smoothing: "+str(altern_b_smthing)
		self.dual_graph.set_uncolored_vertices(altern_a_smthing + altern_b_smthing)

		# add edge between each pair of regions that are connected by an arc
		# note that this is only true if they are from opposite smoothings in the alterating thing
		for a_region in altern_a_smthing:
			for b_region in altern_b_smthing:
				if share_arc(a_region, b_region):
					self.dual_graph.add_edge(a_region, b_region)

		# Now to color the vertices
		# for red (A-smoothing) circles, cut accross the crossings that didn't change relative to the alternating gauss code
		# for blue (B-smoothing), cut accross those that did change
		# should probably make sure that all the code is right and len(self.gauss_cde) = len(gc_alter) at this pt
		a_cuts = []
		b_cuts = []
		for i in range(len(self.gauss_code)):
			if gc_alter[i][1] == self.gauss_code[i][1]: 
				# print str(gc_alter[i])+"and"+str(self.gauss_code[i])
				a_cuts += [self.gauss_code[i][0]]
			else: b_cuts +=[self.gauss_code[i][0]]

		# print "B cuts: "+str(b_cuts)

		for region in self.a_smoothing:
			# decompose this a_smoothing (red) region into its constituent atomic regions
			basis_decomposition = decompose(region, a_cuts)
			# print "Basis decomposition of "+ str(region)+" in A smoothing:"
			# print "\t"+str(basis_decomposition)
			for loop in basis_decomposition:
				# find these regions in the vertex list, in the order they appear in the cycle, using cyclic compare, and color the vertices
				for vertex in self.dual_graph.vertices.keys():
					if turaev.cyclic_compare(loop, vertex): 
						self.dual_graph.color_vertex(vertex, "red")
		for region in self.b_smoothing:
			basis_decomposition = decompose(region, b_cuts)
			# print "Basis decomposition of "+ str(region)+" in B smoothing:"
			# print "\t"+str(basis_decomposition)
			for loop in basis_decomposition:
				for vertex in self.dual_graph.vertices.keys():
					if turaev.cyclic_compare(loop, vertex):
						self.dual_graph.color_vertex(vertex, "blue")

	def __init__(self, gc, safe=False):
		# super(PlanarDiagram, self).__init__(gc, safe)
		LinkDiagram.__init__(self, gc, safe)
		self.a_smoothing = turaev.find_smoothing(self.gauss_code, "a")
		self.b_smoothing = turaev.find_smoothing(self.gauss_code, "b")
		self.dual_graph = graph.ColoredGraph()
		self.build_dual_graph()

		# keep track of original crossing number for purposes of when we add new link components, knowing which crossings corresponded to the original
		self.crossing_number = turaev.crossing_number(self.gauss_code)
		
		# self.atomic_regions = self. DONT NEED THIS BECAUSE THEYRE JUST THE VERTICES OF THE DUAL GRAPH
		# self.holes
		# self.dual_graph

	def set_gauss_code(self, gc):
		self.gauss_code = turaev.reduce_code(gc) #TODO: do this with a setter function for the parent class?
		# self.build_dual_graph()

	def find_holes(self):
		holes = []
		for vertex in self.dual_graph.vertices.keys():
			if len(self.dual_graph.vertices[vertex]) == 0:
				holes += [vertex]
			# elif len(self.dual_graph.vertices[vertex]) == 1:
			# 	raise Exception("Vertex "+str(vertex)+" has only one side capped off (only one color).")
		return holes 


		# I will choose the outside to be whichever one has 1 in it and is longestt
