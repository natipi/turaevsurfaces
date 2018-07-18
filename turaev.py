# July 2018
# Natalia Pacheco-Tallaj
# As part of the Williams SMALL REU
# This program will take a Gauss code and determine the genus of the turaev
# surface for the corresponding link diagram
# The Gauss code will omit the over and under crossings, since they are not 
# relevant toward determining the genus of the turaev surface
# As such, the Gauss code will be of the format "1-2+3+7-(...)", only indicating
# crossing and writhe. 

from linkdiagram import *

# search obj in lst using compare_function
def contained(obj, lst, compare_function):
	for thing in lst:
		if compare_function(obj, thing): return True
	return False

# determines if entries a,b in gauss code have the same crossing
def same_crossing(a ,b):
	return a[0] == b[0]

# taked Gauss code entry and finds Gauss code entry with same crossing 
def find_crossing(thing, lst, start = 0, end = -1):
	if end == -1: n = len(lst)
	else: n = end 
	for i in range(start, n): 
		if same_crossing(thing, lst[i]): return i 
	return -1

# finds maximum integer appearing in a string. returns -1 if no integers
def maxint(string):
	maxint = -1
	for character in string:
		if character.isdigit():
			if int(character) > maxint:
				maxint = int(character)
	return maxint

# finds crossing number of a Gauss code
def crossing_number(gc):
	if len(gc) == 0: return 0
	maxint = -1
	for entry in gc:
		if entry[0] > maxint:
				maxint = entry[0]
	return maxint

def lst_find(thing, lst, start = 0, end = -1):
	if end == -1: n = len(lst)
	else: n = end 
	for i in range(start, n): 
		if thing == lst[i]: return i 
	return -1

# determines if two lists are a cyclic permutation of each other
# unit tested (vaguely)
# for use with comparing state cycles
def cyclic_compare(s1, s2):
	# keep track of whether they are the same in the same or opposite direction
	forward = True
	backward = True
	
	n1 = len(s1)

	if n1 != len(s2):
		return False

	# numbers can appear up to twice in a loop
	rot = lst_find(s1[0], s2)
	rot2 = lst_find(s1[0], s2, rot + 1) # look for the possible second instance after rot

	if rot == -1:
		# print "I think rot is -1" 
		return False
	
	for i in range(1,n1):
		if forward and s1[i] != s2[(i + rot) % n1] and s1[i] != s2[(i + rot2) % n1]:
			# print "I think position", i, "and position", (i+rot)%n1, "are different"
			forward = False
		if backward and s1[i] != s2[(rot - i) % n1] and s1[i] != s2[(rot2 - i) % n1]:
			# print "I think position", i, "and position", (i-rot)%n1, "are different"
			backward = False
 
	return (forward or backward)

# traverse a single smoothing loop starting at index i in the code
# smoothing_type indicates whether its all A or all B smoothing
# returns the crossings touched by the state circle in cyclic order
# general process: get to a crossing, change strand, possibly toggle direction, 
# move to next crossing according to direction
# unit tested (5 ish cases)
# get to a crossing -> check if done -> change strands -> toggle direction -> move
def find_loop(code, i, smoothing_type):
	# toggle direction (with or against the grain)
	forward = True
	n = len(code)

	# if only "a" or "b" is given as smoothing type, it is the all-A smoothing
	# or the all-B smoothing
	if len(smoothing_type) == 1:
		smoothing_type *= n
	elif len(smoothing_type) != crossing_number(code):
		raise Exception("find_loop: Failed to specify smoothing type for all crossings")

	# as we traverse a certain circle in the state, we will record it here
	# in order to count circles later on
	statecircle = [code[i][0]]
	
	# traversal index
	j = i

	while True:
		# Step 1: Change strand
		# find the other ocurrence of crossing code[j] in code
		# find returns -1 if not found and the position within the 
		# global string if found within the specified substring
		j = max(find_crossing(code[j], code, 0, j), find_crossing(code[j], code, j+1, n))

		if j == -1:
			raise Exception("The Gauss code " + code + " only contains one copy of" + code[j])

		# Step 2: possibly toggle direction
		# int(current_crossing) gives the number of the current crossing
		# and since smoothing_type is indexed at 0 but the crossings are 
		# indexed at 1, we subract 1
		if (smoothing_type[int(code[j][0]) - 1] == "a" and code[j][-1] == "-") or (smoothing_type[int(code[j][0]) - 1] == "b" and code[j][-1] == "+"):
			forward = not forward

		# Step 3: move to next crossing according to direction
		if forward: 
			# move forward, wrap around the Gauss code if needed
			j = (j + 1) % n 
		else: 
			# move backward, wrap around if needed
			j = (j - 1) % n
		
		# Step 4: Get to a crossing and record it in the state circle
		statecircle += [code[j][0]]

		# Step 5: check if done
		if j == i and forward:	
			break
	# the first one gets repeted at the end so we remove it when returning
	return statecircle[:-1]

# calculates the amount of circles in the state with smoothing_type 
def find_smoothing(code, smoothing_type):
	n = len(code)
	loops = []
	i = 0
	while i < n:
		loop = find_loop(code, i, smoothing_type)
		print loop
		if not contained(loop, loops, cyclic_compare):
			print loop, "is not in", loops
			loops += [loop]
		i +=1
	return loops

#performs all trivial type 1 reidemeister simplifications.
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

# processes raw gauss code inputed as a string into a list of lists.
def process_code(raw_code):
	raw_code_list = raw_code.split(',')
	gc = []
	for raw_entry in raw_code_list:
		length = len(raw_entry)
		proc_entry = [int(raw_entry[0:(length - 2)]), raw_entry[(length - 2): (length - 1)], raw_entry[(length - 1) : length]]
		gc.append(proc_entry)
	gc = reduce_code(gc)
	return gc

# computes turaev genus of a gauss code inputed as a string
def turaev_genus(raw_code):
	gc = process_code(raw_code)
	if len(gc) == 0: return 0.0
	else: return 0.5*(crossing_number(gc) - len(find_smoothing(gc, "a")) - len(find_smoothing(gc, "b")) + 2)