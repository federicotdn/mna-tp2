import compress, sys

def print_help():
	print('Use: python3 main.py compress file_name L epsilon')
	print(' - Example: python3 main.py compress \'audio/sample1.wav\' 4 0.1')
	print('Use: python3 main.py plot_epsilon L start end step number_of_samples')
	print(' - Example: python3 main.py plot_epsilon 4 0 10 0.5 30')
	print('Use: python3 main.py plot_L epsilon number_of_samples')
	print(' - Example: python3 main.py plot_L 0.1 30')

def main():
	
		
	option = sys.argv[1]
	
	try:
	
		if option == 'compress':
			if (len(sys.argv) != 5):
				raise Error()
			file_name = str(sys.argv[2])
			L = int(sys.argv[3])
			epsilon = float(sys.argv[4])
			compress.compress(file_name, L, epsilon)
		elif option == 'plot_epsilon':
			if (len(sys.argv) != 7):
				raise Error()
			L = float(sys.argv[2])
			start = float(sys.argv[3])
			end = float(sys.argv[4])
			step =  float(sys.argv[5])
			n = int(sys.argv[6])
			compress.plot_epsilon(L, start, end, step,n)
		elif option == 'plot_L':
			if (len(sys.argv) != 4):
				raise Error()
			epsilon = float(sys.argv[2])
			n = int(sys.argv[3])
			compress.plot_L(epsilon,n)
		else:
			raise Error()

	except:
		print('Error processing paramters.')
		print_help()


				
	
		




	
if __name__ == '__main__':
	main()
