# July 2018
# Natalia Pacheco-Tallaj
# As part of the Williams SMALL REU
# This program will take a Gauss code and determine the genus of the turaev
# surface for the corresponding link diagram
# The Gauss code will omit the over and under crossings, since they are not 
# relevant toward determining the genus of the turaev surface
# As such, the Gauss code will be of the format "1-2+3+7-(...)", only indicating
# crossing and writhe. 

# determines if two strings are a cyclic permutation of each other
# unit tested (vaguely)
def cyclic_compare(s1, s2):
	# keep track of whether they are the same in the same or opposite direction
	forward = True
	backward = True
	
	n1 = len(s1)

	if n1 != len(s2):
		return False

	rot = s2.find(s1[0])

	if rot == -1: 
		return False
	
	for i in range(1,n1):
		if forward and s1[i] != s2[(i + rot) % n1]:
			forward = False
		if backward and s1[i] != s2[(rot - i) % n1]:
			backward = False
 
	return forward or backward
	

# search obj in lst using compare_function
def search(obj, lst, compare_function):
	for thing in lst:
		if compare_function(obj, thing): return True
	
	return False

# finds maximum integer appearing in a string. returns -1 if no integers
def maxint(string):
	maxint = -1
	for character in string:
		if character.isdigit():
			if int(character) > maxint:
				maxint = int(character)
	return maxint

# traverse a single smoothing loop starting at index i in the code
# smoothing_type indicates whether its all A or all B smoothing
# returns the crossings touched by the state circle in cyclic order
# general process: get to a crossing, change strand, possibly toggle direction, 
# move to next crossing according to direction
# unit tested (5 ish cases)
def find_loop(code, i, smoothing_type):
	# toggle direction (with or against the grain)
	forward = True
	n = len(code)

	# keep track of the current crossing to be able to stop once you get
	# back to the initial crossing
	initial_crossing = code[i]
	current_crossing = ""

	# as we traverse a certain circle in the state, we will record it here
	# in order to count circles later on
	statecircle = initial_crossing
	
	# traversal index
	j = i

	while current_crossing != initial_crossing:
		# Step 1: Change strand
		# find the other ocurrence of crossing code[j] in code
		# find returns -1 if not found and the position within the 
		# global string if found within the specified substring
		j = max(code.find(code[j], 0, j), code.find(code[j], j+1, n))

		if j == -1:
			print "The Gauss code", code, "only contains one copy of", current_crossing
			return "error" # find out how to flag errors or something

		# Step 2: possibly toggle direction
		if (smoothing_type == "a" and code[j+1] == "-") or (smoothing_type == "b" and code[j+1] == "+"):
			forward = not forward

		# Step 3: move to next crossing according to direction
		if forward: 
			# move forward, wrap around the Gauss code if needed
			j = (j + 2) % n 
		else: 
			# move backward, wrap around if needed
			j = (j - 2) % n
		
		current_crossing = code[j]
		statecircle += current_crossing
	
	# the first one gets repeted at the end so we remove it when returning
	return statecircle[:-1]

# calculates the amount of circles in the state with smoothing_type 
def find_smoothing(code, smoothing_type):
	n = len(code)
	loops = []
	i = 0
	while i < n:
		loop = find_loop(code,i, smoothing_type)
		if not search(loop, loops, cyclic_compare):
			loops += [loop]
		i +=2
	return loops



def turaev_genus(code):
	return 0.5*(maxint(code) - len(find_smoothing(code, "a")) - len(find_smoothing(code, "b")) + 2)
