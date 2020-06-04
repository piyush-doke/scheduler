# Required Modules --------------------------------------------------------------------------------
import json
import time
import datetime as dt
from z3 import *
from itertools import *
# -------------------------------------------------------------------------------------------------
startTime = time.time()


# Functions ---------------------------------------------------------------------------------------
# Find all the different time slots for any given entity --------------------------------
def getTimeSlots(name, slots):
	timeSlots = list()
	for day in range(5):
		for half in institueTime: # for different halfs ---------------------------
			for slot in set(slots): # for different types of slots ----------------
				# Find all possible time slots ------------------------------------
				tempTime = half[0]
				while True:
					# Create a new time slot which starts from tempTime -----------
					endTime = dt.time(hour = int((tempTime.hour*60 + tempTime.minute + slot*60)//60), minute = int((tempTime.hour*60 + tempTime.minute + slot*60)%60))
					# Check if we go over the institute time limit ----------------
					if endTime > half[1]: break
					timeSlots.append(name+'_'+str(tempTime)+'_'+str(endTime)+'_day'+str(day))
					# Increment the tempTime --------------------------------------
					if tempTime.minute + 30 >= 60: tempTime = dt.time(hour = tempTime.hour + 1, minute = 0)
					else: tempTime = dt.time(hour = tempTime.hour, minute = tempTime.minute+30)
	return timeSlots
# ---------------------------------------------------------------------------------------

# Check if two time slots overlap -------------------------------------------------------
def overlaps(a, b):
	d = len(a.split('_')) - 1
	(a, b) = (a.split('_'), b.split('_'))
	# If days are not the same ------------------------------------------------
	if a[d] != b[d]: return False
	# If they are the same, then check for time -------------------------------
	(a_s, a_f) = (dt.time(hour = int((a[d-2].split(':'))[0]), minute = int((a[d-2].split(':'))[1])), dt.time(hour = int((a[d-1].split(':'))[0]), minute = int((a[d-1].split(':'))[1])))
	(b_s, b_f) = (dt.time(hour = int((b[d-2].split(':'))[0]), minute = int((b[d-2].split(':'))[1])), dt.time(hour = int((b[d-1].split(':'))[0]), minute = int((b[d-1].split(':'))[1])))
	if (a_f > b_s and a_s < b_f)  or (b_f > a_s and b_s < a_f) or (b_s <= a_s and b_f >= a_f) or (a_s <= b_s and a_f >= b_f): return True 
	return False
# ---------------------------------------------------------------------------------------

# Print the time-table ------------------------------------------------------------------
def printTimeTable(result):
	dSpace = '		'
	sSpace = '		'
	print('')
	# Print using the day -----------------------------------------------------
	for day in range(5): # for each day
		if day == 0: print('-------------------------------------------------------------------------------------------\n', 'Monday:\n', '------')
		if day == 1: print('-------------------------------------------------------------------------------------------\n', 'Tuesday:\n', '-------')
		if day == 2: print('-------------------------------------------------------------------------------------------\n', 'Wednesday:\n', '---------')
		if day == 3: print('-------------------------------------------------------------------------------------------\n', 'Thursday:\n', '--------')
		if day == 4: print('-------------------------------------------------------------------------------------------\n', 'Friday:\n', '------')
		print(dSpace, 'Class', dSpace, 'Start Time', dSpace, 'End Time', dSpace, 'Venue')
		print(dSpace, '-----', dSpace, '----------', dSpace, '--------', dSpace, '-----')
		for c in result: # print all the courses that are to happen on this day
			if (c.split('_'))[4] == 'day'+str(day):
				if len((c.split('_'))[0]) > 5: sSpace = '	'
				print(dSpace, (c.split('_'))[0], sSpace, (c.split('_'))[2], dSpace, (c.split('_'))[3], dSpace, (c.split('_'))[1])
				sSpace = '		'
	print('-------------------------------------------------------------------------------------------')
	return
# ---------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------


# Initialize Variables ----------------------------------------------------------------------------
# Get data from the JSON file -----------------------------------------------------------
inputFilePath = input("Give an input file: ")
with open(inputFilePath) as fileHandle:
	a = fileHandle.read()
	a.strip()
data = json.loads(a)
# ---------------------------------------------------------------------------------------

# Find the institute time ---------------------------------------------------------------
institueTime = list()
for t in data['Institute time']:
	temp = list()
	temp.append(dt.time(hour = int(t[0]), minute = int((t[0]-int(t[0]))*100)))
	temp.append(dt.time(hour = int(t[1]), minute = int((t[1]-int(t[1]))*100)))
	institueTime.append(temp)
# ---------------------------------------------------------------------------------------

# Create look-up tables -----------------------------------------------------------------
# Room-freq dictionary --------------------------------------------------------
roomFreq = dict() # store the frequency of different types of rooms
for room in data['Classrooms']:
	roomFreq[room[1]] = roomFreq.get(room[1], 0) + 1
# Course-room dictionary ------------------------------------------------------
courseRoom = dict() # store the course to room mapping
for course in data['Courses']:
	courseRoom[course[0]] = course[1]
# Room-course dictionary ------------------------------------------------------
roomCourse = dict()
for i in roomFreq.keys():
	for j in range(roomFreq[i]):
		roomCourse[i+str(j)] = list()
		for k in range(len(data['Courses'])):
			if i == data['Courses'][k][1]: roomCourse[i+str(j)].append(k)
# Instructor-course dictionary ------------------------------------------------
insCourse = dict() # store the instructor to course mapping
instructors = set() # store all the instructors
# Find all the instructors ----------------------
for course in data['Courses']:
	for i in course[3]:
		instructors.add(i)
# Create the desired mapping --------------------
for instructor in instructors:
	insCourse[instructor] = list()
	for i in range(len(data['Courses'])):
		if instructor in data['Courses'][i][3]:
			insCourse[instructor].append(i)
# Batch-course dictionary -----------------------------------------------------
batchCourse = dict() # store the batch to course mapping
batches = set() # store all the batches
# Find all the batches --------------------------
for course in data['Courses']:
	batches.add(str(course[4]))
# Create the desired mapping --------------------
for batch in batches:
	batchCourse[batch] = list()
	for i in range(len(data['Courses'])):
		if int(batch) == data['Courses'][i][4]:
			batchCourse[batch].append(i)
# ---------------------------------------------------------------------------------------

# Make main propositions ----------------------------------------------------------------
propDict = dict() # store all name to proposition mapping
# Course Propostions ----------------------------------------------------------
courseP = list() # list of list
for course in data['Courses']:
	courseP.append(getTimeSlots(course[0], course[2]))
# Create course-time proposition mapping --------------------------------------
for i in courseP:
	for j in i:
		propDict[j] = Bool(j)
# ---------------------------------------------------------------------------------------

'''
# Debugging Purpose ---------------------------------------------------------------------
for i in courseP:
	for j in i:
		print(j)
	break
'''
# ---------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------


# Split Constraints -------------------------------------------------------------------------------
# Split course into sub-courses ---------------------------------------------------------
subCourseP = list() # list of list of list
for i in range(len(courseP)): # pick one course
	t0_subCourseP = list()
	for j in range(len(data['Courses'][i][2])): # for each subpart to be created
		t1_subCourseP = list()
		for k in courseP[i]: # for each time of a particular course
			pos = k.find('_')
			t1_subCourseP.append(k[:pos]+'_'+str(j)+k[pos:])
			# Create subcourse-time mapping -----------------------------------
			propDict[k[:pos]+'_'+str(j)+k[pos:]] = Bool(k[:pos]+'_'+str(j)+k[pos:])
		t0_subCourseP.append(t1_subCourseP)
	subCourseP.append(t0_subCourseP)
# ---------------------------------------------------------------------------------------

# Split courses into room based courses -------------------------------------------------
courseRoomP = list() # list of list of list
for i in courseP: # pick one course
	t0_courseRoomP = list()
	for j in range(roomFreq[courseRoom[(i[0].split('_'))[0]]]): # for each room of a course
		t1_courseRoomP = list()
		for k in i: # for each time of a particular course
			pos = k.find('_')
			t1_courseRoomP.append(k[:pos]+'_'+(courseRoom[(i[0].split('_'))[0]])+str(j)+'_'+k[pos+1:])
			# Create subcourse-time mapping -----------------------------------
			propDict[k[:pos]+'_'+(courseRoom[(i[0].split('_'))[0]])+str(j)+'_'+k[pos+1:]] = Bool(k[:pos]+'_'+(courseRoom[(i[0].split('_'))[0]])+str(j)+'_'+k[pos+1:])
		t0_courseRoomP.append(t1_courseRoomP)
	courseRoomP.append(t0_courseRoomP)
# ---------------------------------------------------------------------------------------

'''
# Debugging Purpose ---------------------------------------------------------------------
for i in courseRoomP:
	for j in i:
		for k in j:
			print(k)
# ---------------------------------------------------------------------------------------
'''
# -------------------------------------------------------------------------------------------------



# Form Constraints --------------------------------------------------------------------------------
print('Encoding the problem ... ', end='')
# C1_1 => Subcourses of the same course do not overlap ----------------------------------
tempAnd = list()
for i in range(len(subCourseP)): # for each course list
	for j in range(len(subCourseP[i])): # for each subcourse list
		for k in range(len(subCourseP[i][j])): # for each subcourse at a particular time
			prop1 = propDict[subCourseP[i][j][k]]
			tempNot = list()
			# Find all overlapping subcourses of the same course --------------
			for l in range(len(subCourseP[i])): # for each subcourse list again
				if j == l: continue
				for m in range(len(subCourseP[i][l])): # for each subcourse at a particular time again
					if overlaps(subCourseP[i][j][k], subCourseP[i][l][m]): tempNot.append(Not(propDict[subCourseP[i][l][m]]))
			tempAnd.append(Implies(prop1, And(tempNot)))
C1_1 = And(tempAnd)
# print(C1_1)
# ---------------------------------------------------------------------------------------

# C1_2 => Each subcourse should be conducted at most once -------------------------------
tempAnd = list()
for i in range(len(subCourseP)): # for each course list
	for j in range(len(subCourseP[i])): # for each subcourse list
		for k in range(len(subCourseP[i][j])): # for each subcourse at a particular time
			prop1 = propDict[subCourseP[i][j][k]]
			tempNot = list()
			# Find all the same subcourses with different time slots ----------
			for l in range(len(subCourseP[i][j])):
				if k == l: continue
				tempNot.append(Not(propDict[subCourseP[i][j][l]]))
			tempAnd.append(Implies(prop1, And(tempNot)))
C1_2 = And(tempAnd)
# print(C1_2)
# ---------------------------------------------------------------------------------------

# C1_3 => Each subcourse should be conducted at least once ------------------------------
tempOr = list()
for i in range(len(subCourseP)): # for each course list
	for j in range(len(subCourseP[i])): # for each subcourse list
		tempProp = [propDict[k] for k in subCourseP[i][j]]
		tempOr.append(Or(tempProp))
C1_3 = And(tempOr)
# print(C1_3)
# ---------------------------------------------------------------------------------------


# C2_1 => Conversion from subcourses to courses -----------------------------------------
tempAnd = list()
for i in range(len(courseP)): # for each course list
	for j in range(len(courseP[i])): # for each course at a particular time
		prop2 = propDict[courseP[i][j]]
		for k in range(len(subCourseP[i])): # for each subcourse at a particular time
			prop1 = propDict[subCourseP[i][k][j]]
			tempAnd.append(Implies(prop1, prop2))
C2_1 = And(tempAnd)
# print(C2_1)
# ---------------------------------------------------------------------------------------

# C2_2 => Conversion from courses to subcourses -----------------------------------------
tempAnd = list()
for i in range(len(courseP)): # for each course list
	for j in range(len(courseP[i])): # for each course at a particular time
		prop1 = propDict[courseP[i][j]]
		tempOr = list()
		for k in range(len(subCourseP[i])): # for each subcourse at a particular time
			tempOr.append(propDict[subCourseP[i][k][j]])
		tempAnd.append((Implies(prop1, Or(tempOr))))
C2_2 = And(tempAnd)
# print(C2_2)
# ---------------------------------------------------------------------------------------

# C2_3 => If two different courses have the same instructor -----------------------------
tempAnd = list()
for ins, course in insCourse.items():
	for i in combinations(course, 2):
		# Find all the courses that overlap -----------------------------------
		for j in range(len(courseP[i[0]])):
			for k in range(len(courseP[i[1]])):
				if overlaps(courseP[i[0]][j], courseP[i[1]][k]): tempAnd.append(Implies(propDict[courseP[i[0]][j]], Not(propDict[courseP[i[1]][k]])))
C2_3 = And(tempAnd)
# print(C2_3)
# ---------------------------------------------------------------------------------------

# C2_4 => If two different courses have the same batch ----------------------------------
tempAnd = list()
for batch, course in batchCourse.items():
	for i in combinations(course, 2):
		# Find all the courses that overlap -----------------------------------
		for j in range(len(courseP[i[0]])):
			for k in range(len(courseP[i[1]])):
				if overlaps(courseP[i[0]][j], courseP[i[1]][k]): tempAnd.append(Implies(propDict[courseP[i[0]][j]], Not(propDict[courseP[i[1]][k]])))
C2_4 = And(tempAnd)
# print(C2_4)
# ---------------------------------------------------------------------------------------


# C3_1 => Conversion from course-room-time to course-time -------------------------------
tempAnd = list()
for i in range(len(courseP)): # for each course list
	for j in range(len(courseP[i])): # for each course at a particular time
		prop2 = propDict[courseP[i][j]]
		for k in range(len(courseRoomP[i])): # for each course-room at a particular time
			prop1 = propDict[courseRoomP[i][k][j]]
			tempAnd.append(Implies(prop1, prop2))
C3_1 = And(tempAnd)
# print(C3_1)
# ---------------------------------------------------------------------------------------

# C3_2 => Conversion from course-room-time to course-time -------------------------------
tempAnd = list()
for i in range(len(courseP)): # for each course list
	for j in range(len(courseP[i])): # for each course at a particular time
		prop1 = propDict[courseP[i][j]]
		tempOr = list()
		for k in range(len(courseRoomP[i])): # for each course-room at a particular time
			tempOr.append(propDict[courseRoomP[i][k][j]])
		tempAnd.append((Implies(prop1, Or(tempOr))))
C3_2 = And(tempAnd)
# print(C3_2)
# ---------------------------------------------------------------------------------------

# C3_3 => During a particular course, the corresponding room in not available -----------
tempAnd = list()
for i in roomCourse.keys(): # for each room
	for j in roomCourse[i]: # for each course conducted in that room
		for k in roomCourse[i]: # for each course conducted in that room
			for prop1 in courseRoomP[j][int(i[len(i)-1])]:
				for prop2 in courseRoomP[k][int(i[len(i)-1])]:
					if prop1 == prop2: continue
					if overlaps(prop1, prop2): tempAnd.append(Implies(propDict[prop1], Not(propDict[prop2])))
C3_3 = And(tempAnd)
# print(C3_3)
# ---------------------------------------------------------------------------------------

# C3_4 => Same course should not be conducted in different rooms at overlapping times ---
tempAnd = list()
for i in range(len(courseRoomP)): # for each course
	for j in range(len(courseRoomP[i])): # for each room where the course can be conducted
		for k in range(len(courseRoomP[i])): # for each room where the course can be conducted
			if k == j: continue
			for prop1 in courseRoomP[i][j]:
				for prop2 in courseRoomP[i][k]:
					if overlaps(prop1, prop2): tempAnd.append(Implies(propDict[prop1], Not(propDict[prop2])))
C3_4 = And(tempAnd)
# print(C3_4)
print('done!')
# ---------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------


# Using Sat Solver --------------------------------------------------------------------------------
# Initialize the solver -----------------------------------------------------------------
finalLogic = And([C1_1, C1_2, C1_3, C2_1, C2_2, C2_3, C2_4, C3_1, C3_2, C3_3, C3_4])
s = Solver()
s.add(finalLogic)
# ---------------------------------------------------------------------------------------

# Check for satisfiability --------------------------------------------------------------
result = list()
print('Checking for Constraints ... ', end='')
if s.check() == sat:
	print('Time-table is possible!', end='\n\n')
	# Store the time table --------------------------------------------------------------
	print('The time table is as follows:')
	m = s.model()
	for i in m: # print all the true values, which are in course-room-time format
		if m[i]:
			c = str(i)
			r = (c.split('_'))[1]
			if r in roomCourse.keys():
				c = str.replace(c, 'big', 'LH')
				c = str.replace(c, 'small', 'T')
				result.append(c)
	# -----------------------------------------------------------------------------------
	# Print the time table --------------------------------------------------------------
	printTimeTable(result)
	# -----------------------------------------------------------------------------------

else: print('Time-table is not possible!')
# -------------------------------------------------------------------------------------------------

endTime = time.time()
print('\nTotal time taken: ', endTime-startTime)