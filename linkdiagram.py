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
	self.dual_graph = graph.ColoredGraph()

	def build_dual_graph(self):
		gc_alter = make_alternating(gc)
		altern_a_smthing = find_smoothing(gc, "a")
		altern_b_smthing = find_smoothing(gc, "b")
		print alter_a_smthing
		self.dual_graph.set_vertices(altern_a_smthing + altern_b_smthing)




	def __init__(self, gc, safe=False):
		LinkDiagram.__init__(self, gc, safe)

		# self.build_dual_graph()
		# self.atomic_regions
		# self.holes
		# self.dual_graph

	def set_gauss_code(self, gc):
		self.gauss_code = turaev.reduce_code(gc) #TODO: do this with a setter function for the parent class?
		# self.build_dual_graph()