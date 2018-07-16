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
def reduce(gc):
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

# makes a diagram alternating by changing crossings
# takes in lst format gauss code
# def make_alternating(gc):
# 	i = 0
# 	n = len(gc)
# 	if n % 2 == 1: raise Exception("Gauss code " + str(gc) + " cannot be made alternating.")
# 	for i in range(1, n):
# 		if gc[i-1][-2]


# forgets overs and unders, i.e. turns Gauss code from a "1U+2O-" format to a 
# "1+2-" format
# def forget_crossings(gc):


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

		self.gauss_code = reduce(gc)
		self.a_state = turaev.find_smoothing(gc, "a")
		self.b_state = turaev.find_smoothing(gc, "b")

	def turaev_orientable(self):
		i = 0
		n = len(gc)
		while i < n:
			# Find other instance of number i
			j = max(find_crossing(gc[i], gc, 0, i), find_crossing(gc[i], gc, i+1, n))
			# OUOUOU
			if (j - i) % 2 == 0: return False
		return True 

	def turaev_genus(self):
		return 0.5*(turaev.crossing_number(self.gauss_code) - len(turaev.find_smoothing(self.gauss_code, "a")) - len(turaev.find_smoothing(self.gauss_code, "b")) + 2)

# Classical link diagrams
class PlanarDiagram(LinkDiagram):
	# def build_dual_graph(self):
		# alt_gcq = 

	def __init__(self, gc, safe=False):
		LinkDiagram.__init__(self, gc, safe)

		# self.build_dual_graph()
		# self.atomic_regions
		# self.holes
		# self.dual_graph

	def set_gauss_code(self, gc):
		self.gauss_code = reduce(gc) #TODO: do this with a setter function for the parent class?
		# self.build_dual_graph()