import re
import optparse
import sys
import os
import awklib
import generate #needed to figure out what well_widths are
import itertools as it

def get_max_waves(wavefile):
	max = []
	wave_file = open(wavefile)
	#skip over header line
	line=wave_file.readline()

	#exclued the first line from the max list
	line =wave_file.readline().split()[1:]
	max = map(lambda x: (0,float(x)),line)
	#Run over each line and each amplitude  and see if it beats
	#out if it beats the current
	#maximum for that wave. If so record that maximum and it's
	#position
	for line in wave_file:
		line = map(float,line.split())
		for i in range(1,len(line)): #exclude first line
			if abs(line[i]) > max[i-1][1]: #max has one less column than line
				max[i-1] = line[0],abs(line[i])
	return max

def extract_width(filename,mat1,mat2):
	afile = open(filename)
	width1,width2 = 0,0
	for line in afile:
		print line
		for match in re.findall("^"+mat1+"\tt=([0-9]+)",line):
			width1 = match
		for match in re.findall("^"+mat2+"\tt=([0-9]+)",line):
			width2 = match
		if width1 != 0 and width2 != 0:
			break
	if width1 == 0 or width2 == 0:
		raise "not found"
	return int(width1),int(width2)

#same well as the nth electron
def get_restricted_wells(n,max_waves,num_types,filename):
	#get restricted electrons
	
	#restrict dict is return value
	restrict_dict = {"el":[],"hh":[],"lh":[]}

	#extract data from generate.py. assume
	#the current values in generate.py are valid.
	width1,width2 = extract_width(filename,"AlGaN","GaN")
	print width1,width2
	well_size = width1+width2
	start_well = width1
	
	#start and end positions for max_waves lookup
	start,end = 0,0
	
	#Which Well are we looking at? Figure out based on n
	which_well = int((max_waves[n-1][0] - start_well)/well_size)+1 #which well are we looking at
	
	#loop over each type, need num_type to find particle location in max_waves
	for type,num_type in zip(("el","hh","lh"),num_types):
		end += num_type
		#check all the maximum positions of each wave type
		for i,(x,val) in zip(it.count(),max_waves[start:end]):
			if x >= start_well+well_size*(which_well-1) and x < start_well+well_size*which_well:
				restrict_dict[type].append(i+1)
		start += num_type
	print restrict_dict
	return restrict_dict	

#hmm... most of the arguments for get_awk_overlap
#seem unused.
def get_awk_overlap(n,file,num_elec,num_hholes,num_lholes):
	hole_offset = 1+num_elec
	awk_cmd = "{sum += $("+str(n+1)+")*$("+str(n+1)+")}END{print sum}"
	norm = awklib.awk(awk_cmd,file)[0]
	print norm
	print file
	#for each wave function at point x, overlap+= \psi_n(x)*\psi_i(x)
	#for each wavefunction we print out a pair on it's own line:
	# wave_number, overlap_value
	#Each line is then parsed using the int_float function define below
	awk_cmd = (("""{for(i = 1; i <= #num_hholes#;i++)
			 sum[i] += ($#n#/#norm#)*($(i+#hole_offset#)/#norm#);
			}END{
			for(i = 1; i <= #num_hholes#;i++) 
			print i,sum[i];}""")
				.replace("#num_hholes#",str(num_hholes))
				.replace("#hole_offset#",str(hole_offset))
				.replace("#n#",str(n+1))
				.replace("#norm#",norm))
	result=  awklib.awk(awk_cmd,file)
	
	#parser for awk output, lambda got ugly
	def int_float(x,y):
		return int(x),float(y)
	res=map(lambda x: int_float(*x.split()), result)
	return res

#Make sures 3 is shown as 003
def add_zeros(num):
	num = str(num)
	while len(num) < 3:
		num = "0"+num
	return num

def option_parser():
	parser = optparse.OptionParser()
	parser.add_option("-n",type="str",dest="n",default="1")
	parser.add_option("-f",type="str",dest="file",default="Qwell080")
	parser.add_option("--el",type="str",dest="el",default=None)
	parser.add_option("--lh",type="str",dest="lh",default=None)
	parser.add_option("--hh",type="str",dest="hh",default=None)
	options,args = parser.parse_args(sys.argv)
	#handle selection of transitions
	if options.n.find(",") != -1:
		options.n,options.n2 = options.n.split(",")
		options.n = int(options.n)
		#are we only looking at a specific transition?
		if options.n2.find(":") != -1:
			options.n2,options.n3 = map(int,options.n2.split(":"))
		else:
			options.n2 = int(options.n2)
			options.n3 = None
	else:
		options.n = int(options.n)
		options.n2 = None
		options.n3 = None
	return options,args


def get_input(options,filename):
	input = open(filename)
	wave_line = input.readline()
	print wave_line
	#and here the magic happens
	num_elec = len(re.findall("el eval [0-9]+",wave_line)) #hack!
	num_hholes = len(re.findall("hh eval ([0-9]+)",wave_line))
	num_lholes = len(re.findall("lh eval ([0-9]+)",wave_line))
	print num_elec,num_hholes,num_lholes
	energy_line = input.readline().split() #I think this isn't used anymore
	return energy_line,(num_elec,num_hholes,num_lholes)

def dict_energies(energy_line,num_types,restriction=None):
	num_elec,num_hholes,num_lholes = num_types
	energy_dict = {"el":[],"lh":[],"hh":[]}
	#Go through the *_St_Out.txt file
	#and get first the electrons, then the heavy holes, 
	#thane the light hole. Ignore restricted ones, 
	#this function is really about grabbing energies from the line in *_St_Out.txt
	for x in xrange((num_elec)):
		offset = 8+x #first 8 are non energies
		energy_dict["el"].append((offset-8,x+1,energy_line[offset]))
	#	if (restriction == None or "el" not in restriction) or x in restriction["el"]:
	#		print "el",x+1, energy_line[offset],offset
	for x in xrange(num_hholes):
		offset = 8+x+num_elec
		energy_dict["hh"].append((offset-8,x+1,energy_line[offset]))
	#	if (restriction == None or "hh" not in restriction) or  x in restriction["el"]:
	#		print "hh",x+1, energy_line[8+x+num_elec],offset
	for x in xrange(num_lholes):
		offset = 8+x+num_elec+num_hholes
		energy_dict["lh"].append((offset-8,x+1,energy_line[offset]))
	#	if (restriction == None or "lh" not in restriction) or x in restriction["el"]:
	#		print "lh",x+1, energy_line[offset],offset
	return energy_dict

def get_restriction(string):
	return eval(string)

def get_status(filename):
	statfile = open(filename)
	text = "\n".join(statfile.readlines())
	energy_line = [0]*8
	for num,energy in re.findall("Electron eigenvalue ([0-9]+) =([ ]+.*) eV",text):
		num = int(num)
		energy = float(energy)
		energy_line.append(energy)
	for num,energy in re.findall("Heavy hole eigenvalue ([0-9]+) =([ ]+.*) eV",text):
		num = int(num)
		energy = float(energy)
		energy_line.append(energy)
	for num,energy in re.findall("Light hole eigenvalue ([0-9]+) =([ ]+.*) eV",text):
		num = int(num)
		energy = float(energy)
		energy_line.append(energy)
	print len(energy_line)
	return energy_line

def gnu_line():
	return \
	"\t'%s' using ($1):($%d+%s) with lines notitle,\\\n"

#Generates gnuplot command file
def plot_energy(energies,filename,wavefile,restriction=None):
	cmd_string = "set terminal aqua enhanced title '"+str(generate.width2)+"'\n"
	cmd_string += ("plot '%s' using 1:2 with lines title 'CB',"
			+ "'%s' using 1:3 with lines title 'VB',")%(filename,filename)
	cmd_file = open("cmd_file.gnu","w")
	r_cmd = "c(" #this is a hack, this should probably be in a seperate function
	for type in energies:
		for offset,id,energy in energies[type]:
			if (restriction == None or type not in restriction)\
			   or id in restriction[type]:
				if type == "hh":
					r_cmd+=str(-energy+.42)+","
				print id,offset,energy
				cmd_string += (gnu_line() %(wavefile,offset+2,energy))
	r_cmd = r_cmd[:-1]+")" 
	print r_cmd #hack for using R, note it goes to std_out, not the command file
	cmd_string = cmd_string[:-3]
	print >>cmd_file,cmd_string
	#os.system("gnuplot cmd_file.gnu")

def main(options,ags):
	n = options.n
	file_start = options.file
	#Determine file names of st_out and st_wave from base string
	filename =  file_start+"_St_Out.txt"
	wavefile =  file_start+"_St_Wave.txt"

	#Use _St_Out to figure out how many different wave functions there are,
	#and their energies. I think Energy_line doesn't do anythig anymore.
	energy_line,num_types = get_input(options,filename)
	num_elec,num_hholes,num_lholes = num_types #for convenience

	#Figure out which waves are in the same well as n. If n2 has been 
	#specified, then we the n2th wave function in the well
	restricted_waves = get_restricted_wells(n,get_max_waves(wavefile),num_types,file_start+".txt")
	if options.n2 != None:
		nindex = restricted_waves["el"][options.n2-1]
	else:
		nindex = options.n
	#Check if we're only looking at specific transition
	if options.n3 != None:
		restricted_waves["lh"] = [restricted_waves["lh"][options.n3-1]]*7
	
	#Calculate overlap integrals
	overlap = get_awk_overlap(nindex,wavefile,num_elec,num_hholes,num_lholes)
	
	#figure out the energies from status file
	#I think I found this to be more reliable to parse than the _St_Out file
	#not sure why. This seems to make the previous energy_line calculation redundant?
	energy_line=get_status(file_start+"_St_Status.txt")

	#Parse the energy line into a dictionary for each type of particle
	energies = dict_energies(energy_line,num_types) 
	
	#figure out which waves we want to plot and then dump them into gnuplot cmd
	#file
	#restricted_waves = get_restricted_wells(n,get_max_waves(wavefile),num_types)
	print restricted_waves
	plot_energy(energies,filename, wavefile,
			restriction={"el":restricted_waves["el"][:4],
				     "lh":[],
                                     "hh":restricted_waves["hh"][:4]})

	#print out most likely transition for the nth state, as determined by the
	#overlap integral between it and all other hole wave functions
	rates = []
	print "electron energies:"
	for i in restricted_waves["el"]:
		print "",energies["el"][i-1]
	print "hole energies:"
	for i in restricted_waves["lh"]:
		print "",energies["lh"][i-1]
	for i in range(len(overlap)):
		if (i+1) in restricted_waves["lh"][:-1]:
			energy_diff = -energies["lh"][i][2]+energies["el"][nindex-1][2]
			rate = (overlap[i][1]**2*energy_diff**3)
			rates.append((i+1,rate,energy_diff,restricted_waves["lh"].index(i+1)+1))
			print i+1,rates[i][1],100*rate,energy_diff,energies["lh"][i],restricted_waves["lh"].index(i+1)+1
		else:
			rates.append((i+1,0,0))
	return [x for x in reversed(sorted(rates,key=lambda x: x[1]))]

if __name__=="__main__":
	options,args = option_parser()
	print "max", main(options,args)
