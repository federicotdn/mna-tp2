import compress, sys

def print_help():
	print('Use: python3 main.py problem[ 2 | 3a | 3b ] file_name L epsilon')
	print(' - Example: python3 main.py problema2 \'audio/sample1.wav\' 4 0.1')


def main():
	if (len(sys.argv) != 5):
		print_help()
		return
		
	file_name = str(sys.argv[2])
	L = int(sys.argv[3])
	epsilon = float(sys.argv[4])
	
	option = sys.argv[1]
	
	if option == 'problem2':
		compress.compress(file_name, L, epsilon)
			
				
	
		




	
if __name__ == '__main__':
	main()