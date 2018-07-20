# The linkdiagram class
# Hopefully, the link diagram class will eventually inherit from Sage's Link
# class, so that we can do Khovanov homology computations and such. For now, 
# it stands alone. 
# Eventually, two classes will inherit from LinkDiagram. The planardiagram
# class will pertain to classical diagrams, and the VirtualDiagram class
# will correspond to (possibly classical) diagrams with virtual crossings
# All of these use reduced Gauss codes (no obvious RI moves)

import turaev
from graphclass import *

from itertools import izip
from copy import deepcopy # copy lists

# cyclically ordered and not wrapping around twice
# example, mod 7:
# 3 5 0 1 is good
# 2 5 0 4 is not good
# but then we could also have counterclockwise cycles
# if I want to NOT allow repeats in the cycles i should make these <='s
def cyclically_ordered_mod_n(lst, n):
	if len(lst) == 1 or len(lst) == 2: return True 
	d = lst[1]-lst[0]
	i = 2
	m = len(lst)
	while i < m:
		if (lst[i]-lst[i-1])*d < 0 and (lst[0]-lst[i])*d < 0: return False 
		i+= 1
	return True 


def cyclically_ordered_sublist_of_consecutive_pairs(sublist,lst):
	i,k = 0,0
	j,l = -1,-1
	n = len(lst)
	while i < n:
		if [lst[i],lst[(i+1)%n]] == sublist[0:2]:
			j = (i+1)%n
			break
		elif [lst[(i+1)%n], lst[i]] == sublist[0:2]:
			j = i
			i = i + 1
			break
		else:
			i+= 1
	# as of now, i is the position of sublist[0] and j is the position of sublist[1]

	while k < n:
		if [lst[k],lst[(k+1)%n]] == sublist[2:4]:
			l = (k+1)%n
			break
		elif [lst[(k+1)%n], lst[k]] == sublist[2:4]:
			l = k
			k = k + 1
			break
		else:
			k+= 1
	# now k is the position of sublist[2] and l is the position of sublist[3]

	if i == n or k == n or j == -1 or l == -1: return False

	return cyclically_ordered_mod_n([i,j,k,l], n)


# find whether a sublist or its reverse is in a list
# where the list has at most 2 entries with a certain value (entries repeat at most once)
def contains_unoriented_sublist(sublist, lst):
	i = turaev.lst_find(sublist[0], lst)
	if i == -1: return False 
	j = turaev.lst_find(sublist[0], lst, i+1)
	forward = True 
	backward = True 
	n = len(lst)
	for step in range(1,len(sublist)):
		if sublist[step] != lst[(i + step) % n] and sublist[step] != lst[(j + step) % n]: 
			forward = False
		if sublist[step] != lst[(i - step) % n] and sublist[step] != lst[(j - step) % n]: 
			backward = False
	return (forward or backward)

# true if arc is in one of the circles in circle_list
def arc_in_circles(arc, circle_list):
	for circle in circle_list:
		if contains_unoriented_sublist(arc, circle): return True
	return False

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
		self.dual_graph = ColoredGraph()
		self.build_dual_graph()

		# keep track of original crossing number for purposes of when we add new link components, knowing which crossings corresponded to the original
		self.crossing_number = turaev.crossing_number(self.gauss_code)

		self.holes = []
		self.outside_hole = []

		self.montesinos_gc = []

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
		self.holes = holes 

	def pick_outside_hole(self):
		self.outside_hole = max(self.holes, key=len)
		self.holes.remove(self.outside_hole)

	# for genus <= 1
	def add_montesino_link_small_genus(self):
		g = turaev.turaev_genus(self.gauss_code)
		if g == 0:
			self.gc_with_meridians = self.gauss_code
		elif g == 1:
			if self.outside_hole == [] or self.holes == []: raise Exception("Uh oh! You have not picked out holes!!!")
			elif len(self.holes) != 1: raise Exception("There are more than g holes! Uh oh! Here's the knot that hecked up: "+str(self.gauss_code))

			new_gc = deepcopy(self.gauss_code)
			meridian_path = shortest_path(self.dual_graph, self.outside_hole, self.holes[0])
			gc_of_the_meridian = []

			prev_left, prev_right = -1,-1

			# for each hole, find shortest path to outside. then add along the meeting faces of the vertices in the path. 
			# be conscious that multiple meridians could get looped on the same arc
			# the genus 1 case is different than the greater genus case! the genus 0 case is also different

			print "Meridian path: "+str(meridian_path)
			for edge in meridian_path:
				new_gc_ln = len(new_gc)
				new_gc_crossing_num = turaev.crossing_number(new_gc)

				# see which arc the step in this path shares
				arc = share_which_arc(edge[0],edge[1])
				print "Arc: "+ str(arc)
				if len(arc)!= 2: raise Exception("Uh oh! This arc is not length 2!: " + str(arc)+" What are you doing! ")
				# find the arc in the gauss code
				i = turaev.find_crossing((arc[0],"",""), new_gc)
				j = turaev.find_crossing((arc[0],"",""), new_gc, i+1)

				left,right = -1,-1
				# figure out which is the arc endpoint on the left and right at the place where the arc occurs in the Gauss code
				# same_crossing takes tuple inputs (num, "O/U", "+/-")
				if turaev.same_crossing((arc[1],"","" ), new_gc[i+1]):
					left, right = i, i+1 
				if turaev.same_crossing((arc[1],"","" ), new_gc[(i-1) % new_gc_ln]):
					left, right = (i-1) % new_gc_ln, i
				if turaev.same_crossing((arc[1],"","" ), new_gc[(j+1) % new_gc_ln]):
					if (left, right) != -1,-1:
						# the arc happens twice. 
						# want the one that doesnt occur right after another crossing in edge[0]
						# i dont think this casework is airtight oops
						# cause what if i just have a braid oh lmao big rip
					else: 
						left, right = j, (j+1) % new_gc_ln
				if turaev.same_crossing((arc[1],"","" ), new_gc[j-1]):
					if (left, right) != -1,-1:
						# the arc happens twice
					else:
						left, right = j-1, j


				# print "prev left, prev right, left, right: "+str([new_gc[prev_left][0],new_gc[prev_right][0],new_gc[left][0], new_gc[right][0]])
				# print "cycle "+str(edge[0])
				if (prev_left, prev_right) == (-1,-1):
					new_gc = new_gc[:left+1] + [(new_gc_crossing_num + 1, 'O', '+'), (new_gc_crossing_num + 2, 'U', '+')] + new_gc[(new_gc_ln if right == 0 else right):] 
					gc_of_the_meridian = [(new_gc_crossing_num + 1, 'U', '+')] + gc_of_the_meridian + [(new_gc_crossing_num + 2, 'O', '+')]
				# if the cyclic order in edge[0] is prev_left->prev_right->left->right, then we add U-O- to the original knot component
				elif cyclically_ordered_sublist_of_consecutive_pairs([new_gc[prev_left][0],new_gc[prev_right][0],new_gc[left][0], new_gc[right][0]], edge[0]):
					# print "hi1"
					new_gc = new_gc[:left+1] + [(new_gc_crossing_num + 1, 'U', '-'), (new_gc_crossing_num + 2, 'O', '-')] + new_gc[(new_gc_ln if right == 0 else right):] 
					gc_of_the_meridian = [(new_gc_crossing_num + 2, 'U', '-')] + gc_of_the_meridian + [(new_gc_crossing_num + 1, 'O', '-')]
				# if the cyclic order in edge[0] is prev_left->prev_right->right->left, then we add O+U+ to the original knot component
				elif cyclically_ordered_sublist_of_consecutive_pairs([new_gc[prev_left][0],new_gc[prev_right][0], new_gc[right][0],new_gc[left][0]], edge[0]):
					# print "hi2"
					new_gc = new_gc[:left+1] + [(new_gc_crossing_num + 1, 'O', '+'), (new_gc_crossing_num + 2, 'U', '+')] + new_gc[(new_gc_ln if right == 0 else right):] 
					gc_of_the_meridian = [(new_gc_crossing_num + 1, 'U', '+')] + gc_of_the_meridian + [(new_gc_crossing_num + 2, 'O', '+')]	

				prev_left, prev_right = left, right + 2 #we've added 2 things in the middle of left, right


			# for a consecutive triple of crossings a,b,c around the hole, we can find whether the longitude goes under or over b
			# if a,b,c all appear consecutively in a red circle, b is a red crossing
			# ELSE if a,b and b,c are in two different red circles or two disjoint portions of a red circle, b is a blue crossing (putting this else after the previous if is important, see knot 9_42)
			# else if a,b,c appear consecutively in a blue circle, b is a blue crossing
			# else if a,b and b,c appear on two different blue circles or two disjoint portions of a blue circle, b is a red crossing
			# i think these criteria only work for crossings around a hole (see that one 8 crossing knot that gives some stacked red regions)
			# ALSO i think we dont need the last two else ifs? so I'm not gonna put them in for now

			# the orientation of the longitude will be the same as the orientation of the hole
			# writhe depends on the orientation of the knot

			gc_of_the_longitude = []

			# for each crossing b in the hole
			i = 0
			n = len(self.holes[0])
			for i in range(n):
				new_gc_ln = len(new_gc)
				new_gc_crossing_num = turaev.crossing_number(new_gc)

				b = self.holes[0][i]
				a = self.holes[0][(i-1) % n]
				c = self.holes[0][(i+1) % n]

				# z comes before a so we can look at the color of a and see if a->b changed
				z = self.holes[0][(i-2) % n]

				# consec in a red circle
				if arc_in_circles([a,b,c], self.a_smoothing):
					# B IS RED
					if arc_in_circles([z,a,b], self.a_smoothing):
						# A is also red, do nothing
						pass
					else:
						# A IS BLUE
						# now the longitude has to go under on the A side and over on the B side of the arc
						# if a is on the left in the Gauss code and B is on the right, writhe is positive on both crossings, otherwise it is negative
						# now when determining where a and b are, I have to take into account meridian intersections manifesting in the gauss code
						# so any crossings that is greater than self.crossing_number should be ignored
						# actually though maybe i can just find a, b in the original gauss code 

						i = turaev.find_crossing((a,"",""), self.gauss_code)
						j = turaev.find_crossing((a,"",""), self.gauss_code, i+1)
						if turaev.same_crossing((b,"","" ), self.gauss_code[i+1]):
							# they appear on the first instance of a, a is left, b is right
							i = turaev.find_crossing((a,"",""), new_gc)
							# a -> new over + -> new under + -> possibly some meridian stuff -> b
							new_gc = new_gc[:i+1] + [(new_gc_crossing_num + 1, 'O', '+'), (new_gc_crossing_num + 2, 'U', '+')] + new_gc[i+1:] 
							# for longitude gc add first the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 1, 'U', '+'), (new_gc_crossing_num + 2, 'O', '+')]
						elif turaev.same_crossing((b,"","" ), self.gauss_code[(i-1) % len(self.gauss_code)]):
							# they appear on the first instance of a, b is left, a is right
							i = turaev.find_crossing((a,"",""), new_gc)
							# b -> possibly some meridian stuff -> new under - -> new over - -> a
							new_gc = new_gc[:i] + [(new_gc_crossing_num + 1, 'U', '-'), (new_gc_crossing_num + 2, 'O', '-')] + new_gc[i:]
							# first add the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 2, 'U', '-'), (new_gc_crossing_num + 1, 'O', '-')] 
						elif turaev.same_crossing((b,"","" ), self.gauss_code[(j+1) % len(self.gauss_code)]):
							# they appear on the second instance of a, a is left, b is right
							i = turaev.find_crossing((a,"",""), new_gc)
							i = turaev.find_crossing((a,"",""), new_gc, i+1)
							# a -> new over + -> new under + -> possibly some meridian stuff -> b
							new_gc = new_gc[:i+1] + [(new_gc_crossing_num + 1, 'O', '+'), (new_gc_crossing_num + 2, 'U', '+')] + new_gc[i+1:] 
							# for longitude gc add first the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 1, 'U', '+'), (new_gc_crossing_num + 2, 'O', '+')]
						elif turaev.same_crossing((b,"","" ), self.gauss_code[j-1]):
							# they appear on the second instance of a, b is left, a is right
							i = turaev.find_crossing((a,"",""), new_gc)
							i = turaev.find_crossing((a,"",""), new_gc, i+1)
							# b -> possibly some meridian stuff -> new under - -> new over - -> a
							new_gc = new_gc[:i] + [(new_gc_crossing_num + 1, 'U', '-'), (new_gc_crossing_num + 2, 'O', '-')] + new_gc[i:]
							# first add the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 2, 'U', '-'), (new_gc_crossing_num + 1, 'O', '-')] 
				else:
					# B IS RED
					if arc_in_circles([z,a,b], self.a_smoothing):
						# A IS RED
						i = turaev.find_crossing((a,"",""), self.gauss_code)
						j = turaev.find_crossing((a,"",""), self.gauss_code, i+1)
						if turaev.same_crossing((b,"","" ), self.gauss_code[i+1]):
							# they appear on the first instance of a, a is left, b is right
							i = turaev.find_crossing((a,"",""), new_gc)
							# a -> new over + -> new under + -> possibly some meridian stuff -> b
							new_gc = new_gc[:i+1] + [(new_gc_crossing_num + 1, 'U', '-'), (new_gc_crossing_num + 2, 'O', '-')] + new_gc[i+1:] 
							# for longitude gc add first the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 1, 'O', '-'), (new_gc_crossing_num + 2, 'U', '-')]
						elif turaev.same_crossing((b,"","" ), self.gauss_code[(i-1) % len(self.gauss_code)]):
							# they appear on the first instance of a, b is left, a is right
							i = turaev.find_crossing((a,"",""), new_gc)
							# b -> possibly some meridian stuff -> new under - -> new over - -> a
							new_gc = new_gc[:i] + [(new_gc_crossing_num + 1, 'O', '+'), (new_gc_crossing_num + 2, 'U', '+')] + new_gc[i:]
							# first add the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 2, 'O', '+'), (new_gc_crossing_num + 1, 'U', '+')] 
						elif turaev.same_crossing((b,"","" ), self.gauss_code[(j+1) % len(self.gauss_code)]):
							# they appear on the second instance of a, a is left, b is right
							i = turaev.find_crossing((a,"",""), new_gc)
							i = turaev.find_crossing((a,"",""), new_gc, i+1)
							# a -> new over + -> new under + -> possibly some meridian stuff -> b
							new_gc = new_gc[:i+1] + [(new_gc_crossing_num + 1, 'U', '-'), (new_gc_crossing_num + 2, 'O', '-')] + new_gc[i+1:] 
							# for longitude gc add first the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 1, 'O', '-'), (new_gc_crossing_num + 2, 'U', '-')]
						elif turaev.same_crossing((b,"","" ), self.gauss_code[j-1]):
							# they appear on the second instance of a, b is left, a is right
							i = turaev.find_crossing((a,"",""), new_gc)
							i = turaev.find_crossing((a,"",""), new_gc, i+1)
							# b -> possibly some meridian stuff -> new under - -> new over - -> a
							new_gc = new_gc[:i] + [(new_gc_crossing_num + 1, 'O', '+'), (new_gc_crossing_num + 2, 'U', '+')] + new_gc[i:]
							# first add the a side then the b side
							gc_of_the_longitude += [(new_gc_crossing_num + 2, 'O', '+'), (new_gc_crossing_num + 1, 'U', '+')] 
					else:
						# A is also blue, do nothing
						pass

		print "Longitude: "+str(gc_of_the_longitude)
		print "Meridian: "+str(gc_of_the_meridian)
		self.montesinos_gc = [new_gc, gc_of_the_meridian, gc_of_the_longitude]


		# I will choose the outside to be whichever one has 1 in it and is longestt


def test():
	print "Declaring planar diagram ..."
	J = PlanarDiagram([[1, 'O', '+'], [2, 'U', '+'], [3, 'O', '+'], [4, 'U', '+'], [5, 'U', '-'], [6, 'O', '-'], [7, 'O', '-'], [8, 'U', '-'], [4, 'O', '+'], [3, 'U', '+'], [8, 'O', '-'], [7, 'U', '-'], [9, 'O', '+'], [1, 'U', '+'], [2, 'O', '+'], [5, 'O', '-'], [6, 'U', '-'], [9, 'U', '+']])
	print "Finding holes ..."
	J.find_holes()
	print "Holes are: "+str(J.holes)
	print "Picking outside hole ..."
	J.pick_outside_hole()
	print "Outside hole is: "+str(J.outside_hole)
	print "Adding montesino link ..."
	J.add_montesino_link_small_genus()
	print "The link is: "+str(J.montesinos_gc)
