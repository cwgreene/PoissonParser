import sys
import os

#controllers
import generate
import batch_run
import get_energies
import numpy as np

def main(args):
	out = open("polarized_1-3_transition.txt","w")
	#generate.window_size=2 #flatband
	for well_width in np.arange(6,10.1,.5):
		generate.width2 = int(well_width*10)
		batch_run.main()
		options,args = get_energies.option_parser()
		options.file = "energy_data7/Qwell3"
		options.n=2
		options.n2=1
		options.n3=4
		print >>out,well_width,get_energies.main(options,args)[:3]
		os.system("gnuplot cmd_file.gnu")

if __name__=="__main__":
	main(sys.argv)
