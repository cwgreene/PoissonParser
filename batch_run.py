import time
import os
import generate

batch_run = []

def print_safe(string):
	print >> batch_run, string

def run_parameter(numstr):
	print_safe("1")
	print_safe("Qwell"+numstr)
	print_safe("y")
	print_safe("y")
	print_safe("y")
	print_safe("7")

def main():
	global batch_run
	for i in range(1):
		batch_run = open("batch_run.txt","w")
		width = 100
		numstr = str(width)
		numstr="0"*(3-len(numstr))+numstr
		run_parameter(str(numstr))
		batch_run.close()
		generate.width2 = width
		generate.generate(numstr)
	#	time.sleep(.3)numstr
		os.system("cat batch_run.txt | ./1D\ Poisson"  )
		print numstr
	#	time.sleep(.1)
		os.system("mv Qwell"+str(numstr)+"* energy_data7")

if __name__=="__main__":
	main()
	print "batch run done!"
