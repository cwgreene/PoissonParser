import os
import time

for x in range(6,20+1):
	vary = str(2+.1*x)
	os.system("sed -e 's/@@!@@/"+vary+"/' materials_src.txt > materials.txt")
	os.system("python batch_run.py")
	os.system("echo "+vary+
		  "`python get_energies.py -f energy_data7/Qwell2 | tail -1 `"+
		  ">> polarizations.txt")
	os.system("tail polarizations.txt")
	os.system("gnuplot cmd_file.gnu")
	print vary
	print "Continue?"
	time.sleep(.5)
