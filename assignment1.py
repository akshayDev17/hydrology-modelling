import geopandas as gpd
import numpy as np
from matplotlib import path
import matplotlib.pyplot as plt

def giveMask(fileName):
	shape = gpd.read_file(fileName)
	shapeArr = [i for i in shape.geometry]
	x,y = shapeArr[0].exterior.coords.xy

	left = min(x) -0.5
	right = max(x) +0.5
	up = max(y) +0.5
	down = min(y) -0.5
	resolv = 0.02

	len1, len2 = int((right-left) / resolv)+1, int((up-down) / resolv)+1 
	zeroes = [ [0 for i in range(len2)] for j in range(len1)]
	a1, a2 = [left + resolv*i for i in range(len1)], [down + resolv*i for i in range(len2)]
	p = path.Path([(x[i], y[i]) for i in range(len(x))])

	for i in range(len1):
		for j in range(len2):
			if p.contains_points([(a1[i], a2[j])]):
				zeroes[i][j] = 1
			else:
				zeroes[i][j] = 0

	zeroes = np.array(zeroes).T.tolist()
	plt.figure(0)
	plt.imshow(zeroes)
	plt.set_cmap('gray')
	plt.ylim((0,150))

	plt.figure(1)
	plt.plot(x,y)
	plt.show()
