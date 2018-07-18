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

# go through all pairs of a list
def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)

# the cycles are lists
def abut(cycle1, cycle2):
	for i in cycle1:
		if i in cycle2: return True
	return False

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
	gc = turaev.process_code(gc)
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
	print turaev.find_smoothing(gc, "a")

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
		gc_alter = make_alternating(gc)
		altern_a_smthing = find_smoothing(gc, "a")
		altern_b_smthing = find_smoothing(gc, "b")
		print alter_a_smthing
		self.dual_graph.set_vertices(altern_a_smthing + altern_b_smthing)

		# One set of edges links A smoothing circles that abut each other
		for a,b in pairwise(altern_a_smthing):
			if abut(a,b): self.dual_graph.add_edge(a,b)
		# One set of edges links B smoothing circles that abut each other
		for a,b in pairwise(altern_b_smthing):
			if abut(a,b): self.dual_graph.add_edge(a,b)

		# Now to color it
		# for red (A-smoothing) circles, cut accross the crossings that didn't change relative to the alternating gauss code
		# for blue (B-smoothing), cut accross those that did change
		# should probably make sure that all the code is right and len(gc) = len(gc_alter) at this pt
		a_cuts = []
		b_cuts = []
		for i in range(len(gc)):
			if gc_alter[i][1] == gc[i][1]: a_cuts += [gc[i][0]]
			else: b_cuts +=[gc[i][0]]

		for region in self.a_smoothing:
			basis_decomposition = decompose(region, a_cuts)
			# find these regions in the vertex list, in the order they appear in the cycle, using cyclic compare, and color some vertices
			# OH LOL WE DONT EVEN NEED THE GRAPH


	def __init__(self, gc, safe=False):
		LinkDiagram.__init__(self, gc, safe)
		self.a_smoothing = turaev.find_smoothing(self.gauss_code, "a")
		self.b_smoothing = turaev.find_smoothing(self.gauss_code, "b")
		self.dual_graph = graph.ColoredGraph()
		self.build_dual_graph()
		# self.atomic_regions = self. DONT NEED THIS BECAUSE THEYRE JUST THE VERTICES OF THE DUAL GRAPH
		# self.holes
		# self.dual_graph

	def set_gauss_code(self, gc):
		self.gauss_code = turaev.reduce_code(gc) #TODO: do this with a setter function for the parent class?
		# self.build_dual_graph()

