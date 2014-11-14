import wave, cmath, math, numpy, sys, huffman

def main():
	f = wave.open('audio/corto2.wav')
	N = f.getnframes()
	ks = []
	epsilon = 0.1
	L = 8
	max_size = math.pow(2,L) - 1
	

	for i in range(N):
		ks.append(int.from_bytes(f.readframes(1), byteorder = 'little'))

	for i in range(10):
		print(ks[i])
	print('------------------------------------------------------------')

	alphas = numpy.fft.fft(ks)
	n = math.floor(N/2) + 1
	alphas = alphas[:n]

	for i, alpha in enumerate(alphas):
		if (abs(alpha) < epsilon):
			alphas[i] = 0

	min_val, max_val = get_max_and_min(alphas)
	
	real_alphas = []
	imag_alphas = []
	fn  = lambda x: int(((x - min_val)/(max_val - min_val))* max_size)

	for alpha in alphas:
		real_alphas.append(fn(alpha.real))
		imag_alphas.append(fn(alpha.imag))

	

	# compressed_bits = huffman.estimate(real_alphas + imag_alphas)
	# print('Compressed: ' + str(compressed_bits))
	# print('Uncompressed: ' + str(N*16))

	fn = lambda x: ((x/max_size)*(max_val - min_val)) + min_val
	new_alphas = []
	for i in range(n):
		new_alphas.append(complex(fn(real_alphas[i]), fn(imag_alphas[i])))

	print('------------------------------------------------------------')
	for i in range(10):
		print('old: ' + str(alphas[i]) + ' new: ' + str(new_alphas[i]))

	output = wave.open('audio/output.wav', 'wb')
	output.setparams(f.getparams())
	new_alphas.extend(reversed(new_alphas[1:]))
	inverse_fft = numpy.fft.ifft(new_alphas)

	for i in range(10):
		print(int(inverse_fft[i].real))

	bytes = []
	for num in inverse_fft:
		bytes.append(int(abs(num.real)).to_bytes(2, byteorder = 'little'))

	output.writeframes(bytes)


	# alphas = dft(ks)
	# max_real = max((n.real for n in alphas))
	# min_real = min((n.real for n in alphas))
	# max_imag = max((n.imag for n in alphas))
	# min_imag = min((n.imag for n in alphas))

	# print('max real ' + str(max_real))
	# print('min real ' + str(min_real))
	# print('max imag ' + str(max_imag))
	# print('min imag '  + str(min_imag))

	# for i in range(len(alphas)):
	# 	aux = alphas[i]
	# 	# alpha = complex((alphas[i].real*math.pow(2,3))/(max_real - min_real), (alphas[i].imag*math.pow(2,3))/(max_imag - min_imag))
	# 	alpha = complex((alphas[i].real - min_real) /(max_real - min_real))
	# 	alphas[i] = alpha
	# 	print(str(alpha) + '  vs  ' +  str(aux))


	# data = inverse_dft(alphas, N)

	# print('------------------------------------------------')
	# for i in range(10):
	# 	print(round(abs(data[i])))
	

def get_max_and_min(v):
	min_val = v[0].real
	max_val = v[0].real

	for num in v:
		if (num.real < min_val):
			min_val = num.real
		elif (num.real > max_val):
			max_val = num.real

		if (num.imag < min_val):
			min_val = num.imag
		elif (num.imag > max_val):
			max_val = num.imag

	return min_val, max_val

def dft(ks):
	N = len(ks)
	N_opt = (int) ((N/2) + 1) if (N % 2 == 0) else math.ceil(N/2)
	epsilon = 0.0001
	alphas =[]
	for n in range(N_opt):
		alpha = 0
		for k in range(N):
			f_k = ks[k]
			alpha += f_k * cmath.exp((complex(0,1) * 2 * cmath.pi * n * k)/ N)
		alpha /= N
		if (abs(alpha) < epsilon):
			alpha = 0
		alphas.append(alpha)
	return alphas

def inverse_dft(alphas, N):
	N_opt = (int) ((N/2) + 1) if (N % 2 == 0) else math.ceil(N/2)
	data = []
	for k in range(N):
		f_k = 0
		for n in range(N_opt):
			f_k += alphas[n] * cmath.exp((complex(0,-1) * 2 * cmath.pi * k *n)/N)
		aux = 0
		if (N % 2 == 0):
			aux = N_opt -1
		else:
			aux = N_opt
		ranges = zip(reversed(range(1, aux)), range(N_opt, N))
		for i,n in ranges:
			f_k += alphas[i].conjugate() * cmath.exp((complex(0,-1) * 2 * cmath.pi * k *n)/N)
			
		data.append(f_k)
	return data


def fft(v):
    n = len(v)
    if n == 1:
        return v
    evenfft = fft(v[0:][::2])
    oddfft = fft(v[1:][::2])
    result = [0]*n
    for k in range(n//2):
        (x, y) = butterfly(evenfft[k], oddfft[k], n, k)
        result[k] = x
        result[k + n//2] = y
    return result

def butterfly(x, y, N, j):
    w = cmath.exp(-2.0j*math.pi*j/N)
    # return ((x + w*y)/math.sqrt(2), (x - w*y)/math.sqrt(2))
    return (x + w*y, x - w*y)

def inverse_fft(v):
    def recursive_inverse_fft(v):
        n = len(v)
        if n == 1:
            return v
        evenfft = recursive_inverse_fft(v[0:][::2])
        oddfft = recursive_inverse_fft(v[1:][::2])
        result = [0]*n
        for k in range(n//2):
            (x, y) = butterfly(evenfft[k], oddfft[k], n, -k)
            result[k] = x
            result[k + n//2] = y
        return result
    return (x.real/len(v) for x in recursive_inverse_fft(v))
	
	
if __name__ == '__main__':
	main()