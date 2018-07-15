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

	# numbers can appear up to twice in a loop
	rot = s2.find(s1[0])
	rot2 = s2.find(s1[0], rot + 1) # look for the possible second instance after rot

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
# get to a crossing -> check if done -> change strands -> toggle direction -> move
def find_loop(code, i, smoothing_type):
	# toggle direction (with or against the grain)
	forward = True
	n = len(code)

	# if only "a" or "b" is given as smoothing type, it is the all-A smoothing
	# or the all-B smoothing
	if len(smoothing_type) == 1:
		smoothing_type *= n
	elif len(smoothing_type) != maxint(code):
		raise Exception("find_loop: Failed to specify smotthing type for all crossings")

	# as we traverse a certain circle in the state, we will record it here
	# in order to count circles later on
	statecircle = code[i]
	
	# traversal index
	j = i

	while True:
		# Step 1: Change strand
		# find the other ocurrence of crossing code[j] in code
		# find returns -1 if not found and the position within the 
		# global string if found within the specified substring
		j = max(code.find(code[j], 0, j), code.find(code[j], j+1, n))

		if j == -1:
			raise Exception("The Gauss code " + code + " only contains one copy of" + code[j])

		# Step 2: possibly toggle direction
		# int(current_crossing) gives the number of the current crossing
		# and since smoothing_type is indexed at 0 but the crossings are 
		# indexed at 1, we subract 1
		if (smoothing_type[int(code[j]) - 1] == "a" and code[j+1] == "-") or (smoothing_type[int(code[j]) - 1] == "b" and code[j+1] == "+"):
			forward = not forward

		# Step 3: move to next crossing according to direction
		if forward: 
			# move forward, wrap around the Gauss code if needed
			j = (j + 2) % n 
		else: 
			# move backward, wrap around if needed
			j = (j - 2) % n
		
		# Step 4: Get to a crossing and record it in the state circle
		statecircle += code[j]

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
		loop = find_loop(code,i, smoothing_type)
		if not search(loop, loops, cyclic_compare):
			print loop, "is not in", loops
			loops += [loop]
		i +=2
	return loops

def turaev_genus(code):
	return 0.5*(maxint(code) - len(find_smoothing(code, "a")) - len(find_smoothing(code, "b")) + 2)