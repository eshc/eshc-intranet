# sum.py

# p1
ebay = [
	43.25,
	3.75,
# p2
	32.43,
	19.27,
# p3
	19.27,
	3.75,
	43.25,
# p4
	6.95,
	83.30,
# p5
	4.50+1.98,
	17.85,
	21.75,
# p6
	13.75,
	13.75,
	9.38,
# p7
	7.50,
	24.39,
# p8
	89.99,
	17.97,
]
r1 = [113.40] # batteries
r2 = [279.40] # tools
r3 = [7.52] # food

thistle = [148.21]
x = ebay + r1 + r2 + r3 + thistle
print('filip:', sum(x))
print('r:', sum(r1+r2+r3))
print('ebay:', sum(ebay))

screws = 32.43 + 19.27 + 19.27
bolts = 43.25 + 43.25
washers = 3.75 + 3.75
nuts = 6.95
knee_pads = 17.85
mitre_saw = 89.99
screwdrivers = 17.97
hazard = 4.50 + 1.98
boyle = [
# screws 50mm 	
70.97, # 32.43 + 19.27 + 19.27
# screws 70mm
# screws 90mm
# bolts M10 150mm
86.5, # 43.25 + 43.25
# washers
7.5, # 3.75 + 3.75
# nuts M10 	
6.95,
# knee pads 	
17.85,
# mitre saw 	
89.99,
# pozi screwdrivers 	
17.97,
# hazard tape 	
6.48,
# wood 47x 98 	
148.21,
# truss clips 47x98
# brackets 40x60mm 	
83.3,
# more screws (100X 30, 40, 50) 	
49.25,
# more bolts (38x M8 110mm) 	
33.77,
# nuts (50x m10) 	
7.5,
# food 	
7.52,
# tools 	
279.4,
# batteries 	
113.4,
# total 	1026.56
]
print('boyle:', sum(boyle))
