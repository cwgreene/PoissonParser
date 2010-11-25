import sys

width1 = 10
width2 = 90
width3 = 1000
window_size = 3
repeat_wells = 10
big_width = 1

def generate(numstr):
	aFile = \
"""# obA single quantum well.  Quantized states are found automatically.

surface schottky = 3 v1"""+"\n"+\
("""AlGaN	t=$1 x=1.0
GaN	t=$2"""+"\n")*repeat_wells+\
(("GaN	t="+str(width3)+"\n")*big_width+
#("""AlGaN	t=10 x=1.0
#GaN	t=$2"""+"\n")*6+\
"""AlGaN	t=$1 x=1.0
substrate schottky = 3 v2

fullyionized
#v1 0.0 -1.0 -0.5
v1 0.0
v2 0.0
schrodingerstart=$start
schrodingerstop=$end
find quantized states
stop on will robinson
temp=300K
dy=0.1""")
	iwidth1,iwidth2=int(width1),int(width2)
	ibounds_start =0+2*(width2+width1) #int(bounds_start(numstr))
	aFile = (aFile.replace("$1",str(width1))).\
		replace("$2",str(width2)).\
		replace("$end",str(ibounds_start+(iwidth1+iwidth2)*window_size)).\
		replace("$start",str(ibounds_start))
#			bounds_start_off(ibounds_start,iwidth1+iwidth2))
	dest = open("Qwell"+numstr+".txt","w")
	dest.write(aFile)
	dest.close()

def bounds_up(numstr):
	print str((int(numstr)+10)*13+1200)
	return str((int(numstr)+10)*13+500)#str(min((max(1000,1000+(int(numstr)-150)*13)),2500))
def bounds_start(numstr):
	return int(numstr)*(int(width1)+int(width2))

def bounds_start_off(start,width):
	res = start - width*.5
	return start
	if res < 0:
		res = 0
	return str(res)
