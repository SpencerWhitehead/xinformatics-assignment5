import random
import numpy as np
import matplotlib.pyplot as plt

from pylab import plot, show

# The following code is designed to perform classification
# on the hand-written digits data from US Postal Service.
# Linear regression is used for classification and the
# pocket algorithm is used for improvement. This method
# is performed with and without a third order nonlinear
# transform. In particular, the classification is between
# the digits 1 and 5.


class ReadFile(object):
	"""Object for reading from data file """
	def __init__(self, fname):
		self.fname = fname

	# Iterate throught the file
	def __iter__(self):
		with open(self.fname, 'r') as f:
			for line in f:
				yield line.split()
		
class Perceptron(object):
	""" Perceptron learning algorithm """
	def __init__(self, train_data, w0=None):
		self.X = train_data
		if any(w0):
			self.W = w0
		else:
			self.W = [0.0 for i in xrange(len(train_data[0][0]))]
		self.min_w = None
		self.current_E_in = 0
		self.min_E_in = len(train_data)

	# Update weights of perceptron
	def update_w(self, misclass):
		current_x = misclass[0]
		current_y = misclass[1]
		temp_w = []

		updated_xy = [x0*current_y for x0 in current_x]
		for i in xrange(len(self.W)):
			temp_w.append(self.W[i]+updated_xy[i])
		self.W = temp_w

	# Find all misclassified points
	def find_misclassified(self, pock=False):
		missclass = []
		temp_e_in = 0.0
		for i in xrange(len(self.X)):
			pt = self.X[i][0]
			pt_class = self.X[i][1]
			dot_prod = np.dot(pt, self.W)
			if int(np.sign(dot_prod)) != pt_class:
				missclass.append(i)
				if pock:
					temp_e_in += 1.0
		if pock:
			self.current_E_in = temp_e_in/float(len(self.X))

		if any(missclass):
			return self.X[random.choice(missclass)]
		else:
			return None

	# Create line for plotting classifier
	def make_line(self, x1):
		m = (-1)*(self.W[1]/self.W[2])
		b = (-1)*(self.W[0]/self.W[2])
		p1y = (m*x1)+b
		return [x1,p1y]

	# Run perceptron with pocket algorithm
	def pocket(self, num_itrs):
		learned = False
		itrs = 0
		while itrs < num_itrs:
			miss_pt = self.find_misclassified(pock=True)
			if self.current_E_in < self.min_E_in:
				self.min_E_in = self.current_E_in
				self.min_w = self.W

			if not miss_pt:
				break
			self.update_w(miss_pt)
			itrs+=1
		self.W = self.min_w
		return itrs

class LinearRegression(object):
	""" Object for linear regression """
	def __init__(self, my_data):
		self.data = my_data
		self.W = None

	# Execute the pseudo-inverse algorithm
	def linear_regression(self):
		X = np.matrix([d[0] for d in self.data])
		y_bar = np.matrix([d[1] for d in self.data]).T
		X_cross = ((X.T*X).I)*X.T
		w_lin = (X_cross * y_bar).getA1()
		self.W = w_lin

	# Create line for plotting classifier
	def lin_reg_line(self, x1):
		m = (-1)*(self.W[1]/self.W[2])
		b = (-1)*(self.W[0]/self.W[2])
		p1y = (m*x1)+b
		return [x1,p1y]

# Find a particular digit in the data
def find_digit(d, data_obj, single=True):
	for point in data_obj:
		if point[0] in d:
			if single:
				d.remove(data[i][0])
			yield point

# Calculate intensity of each data point
def intensity(point):
	intense = 0.0
	for i in xrange(1, len(point)):
		intense += float(point[i])
	return intense/(len(point)-1)

# Calculate symmetry of each data point
def find_symmetry(original):
	flipped = original.copy()
	# Reverse the row
	for i in xrange(len(flipped)):
		flipped[i] = flipped[i][::-1]

	total = 0
	for i in xrange(len(original)):
		for j in xrange(len(original[i])):
			diff = float(original[i][j])-float(flipped[i][j])
			total += 1-abs(diff)
	return total/256.0

# Get feature vector and classification of each data point
# Features are symmetry and intensity
def get_features(point):
	h = np.asarray(point[1:len(point)])
	h = h.reshape(16,16)
	h_sym = find_symmetry(h)
	v_sym = find_symmetry(h.transpose())

	avg_sym = (h_sym+v_sym)/2.0
	p_intensity = intensity(point)
	classify = 1
	if point[0] != '1.0000':
		classify = -1
	return ((1, p_intensity, avg_sym), classify)

# Returns list of feature data points
# Each point is of the form:
#    [((1, intensity, symmetry), classification),...]
def collect_feature_data(data_obj):
	feature_data = []
	for loc in find_digit(['1.0000','5.0000'], data_obj, False):
		feature_data.append(get_features(loc))
	return feature_data

# Perform third order nonlinear transform on data point
def nonlinear_transform(x0, x1, x2):
	return (x0, x1, x2, x1**2, x1*x2,
			x2**2, x1**3, x2*(x1**2), x1*(x2**2), x2**3)

# Go through and transform each sdata points
def transform_points(data):
	transform_data = []
	for i in xrange(len(data)):
		x0 = data[i][0][0]
		x1 = data[i][0][1]
		x2 = data[i][0][2]
		temp = nonlinear_transform(x0, x1, x2)
		transform_data.append((temp, data[i][1]))
	return transform_data

# Determine the classification of a data point
def find_class(x, y, w):
	dot_prod = 0
	temp = nonlinear_transform(1, x, y)
	dot_prod = np.dot(temp, w)
	if int(np.sign(dot_prod)) > 0:
		return 1
	else:
		return -1

# Determine test error
def find_E_test(data, p):
	E_test = 0.0
	for j in xrange(len(data)):
		dot_prod = np.dot(data[j][0], p.W)
		if int(np.sign(dot_prod)) != data[j][1]:
			E_test += 1.0
	return E_test/float(len(data))

# Plot data and linear classifier
def make_plot(data, pla=None, lin_reg=None, interval=[-1,0.2], name=None):
	cols = {1:'bo', -1:'rx'}
	for x in data:
		plt.plot(x[0][1], x[0][2], cols[x[1]])

	if pla:
		p1 = pla.make_line(interval[0])
		p2 = pla.make_line(interval[1])
		plt.plot([p1[0], p2[0]], [p1[1], p2[1]], label='PLA')

	if lin_reg:
		l1 = lin_reg.lin_reg_line(interval[0])
		l2 = lin_reg.lin_reg_line(interval[1])
		plt.plot([l1[0], l2[0]], [l1[1], l2[1]], label='Linear Regression')

	plt.xlabel('Average Intensity')
	plt.ylabel('Symmetry')
	if name:
		if name == 'train.txt':
			plt.title('Training Data')
			plt.savefig('train_curve.png')
		elif name == 'test.txt':
			plt.title('Testing Data')
			plt.savefig('test_cure.png')
	plt.close()

# Plot data and nonlinear classifier
def make_nonlin_plot(data, pla=None, interval=[-1,0.2], name=None):
	cols = {1:'#698bd3', -1:'#d46a6a'}

	dx1 = abs(float(interval[1]-interval[0])/100.0) 
	dx2 = 1.0/100.0
	for k in xrange(101):
		for m in xrange(101):
			x_val = interval[0]+(k*dx1)
			y_val = m*dx2
			plt.scatter(x_val, y_val,
				color=cols[find_class(x_val, y_val, pla.W)],
				marker='s', edgecolors='none')

	cols = {1:'bo', -1:'rx'}
	for x in data:
		plt.plot(x[0][1], x[0][2], cols[x[1]])

	plt.xlim(interval[0],interval[1])
	plt.ylim(0,1)
	plt.xlabel('Average Intensity')
	plt.ylabel('Symmetry')
	if name:
		if name == 'train.txt':
			plt.title('Training Data')
			plt.savefig('nonlin_train_curve.png')
		elif name == 'test.txt':
			plt.title('Testing Data')
			plt.savefig('nonlin_test_curve.png')
	plt.close()

# Execute linear regression for classification for
# classification and pocket algorithm for improvement
def run_learning_algo(data, num_pocket_itrs=500):
	lin = LinearRegression(data)
	lin.linear_regression()
	p = Perceptron(data, lin.W)
	p.pocket(num_pocket_itrs)
	return p

def main():
	num_pocket_itrs = 1000
	interval = [-1,0.2]

	train_f = 'train.txt'
	test_f = 'test.txt'
	train_data = ReadFile(train_f)
	feature_data = collect_feature_data(train_data)

	test_data = ReadFile(test_f)
	nonlin_test_feature_data = collect_feature_data(test_data)

	percep = run_learning_algo(feature_data)
	print 'Training error without nonlinear transform: ', percep.min_E_in
	make_plot(feature_data, pla=percep, interval=[-1,0.4], name=train_f)

	test_feature_data = collect_feature_data(test_data)
	E_test = find_E_test(test_feature_data, percep)
	print 'Test error without nonlinear transform: ',E_test
	make_plot(test_feature_data, pla=percep, interval=[-1,0.4], name=test_f)


	nonlin_data = transform_points(feature_data)
	nonlin_percep = run_learning_algo(nonlin_data)
	print 'Training error with nonlinear transform: ', nonlin_percep.min_E_in
	make_nonlin_plot(nonlin_data, pla=nonlin_percep, interval=[-1,0.4], name=train_f)

	nonlin_data = transform_points(nonlin_test_feature_data)
	E_test = find_E_test(nonlin_data, nonlin_percep)
	print 'Test error with nonlinear transform: ',E_test
	make_nonlin_plot(nonlin_data, pla=nonlin_percep, interval=[-1,0.4], name=test_f)


if __name__ == '__main__':
	main()