import sys

name = "materials."+sys.argv[1]
__import__(name)
material = sys.modules[name]
print material.name,
print "binary", material.comment
print "%E "*11  % (material.energy_gap,\
		material.band_offset,\
		material.dielectric,\
		material.electron_mass,\
		material.cb_valley_degeneracy,\
		material.heavy_hole_mass,\
		material.light_hole_mass,\
		material.donor_ionization_energy,\
		material.acceptor_ionization,\
		material.deep_donor_ionization,\
		material.deep_acceptor_ionization)
