import wave, cmath, math, numpy, os, huffman

def compress(file_name, L, epsilon):
	max_size = math.pow(2,L) - 1
	f = wave.open(file_name)
	N = f.getnframes()
	ks = get_samples(f)

	print('Compressing...')

	alphas = get_alphas(f, epsilon, ks)

	min_val, max_val = get_max_and_min(alphas)
	
	real_alphas, imag_alphas = quantisize(alphas, min_val, max_val, max_size)

	for i in range(100):
		print('real: ' + str(real_alphas[i]) + ' imag: ' + str(imag_alphas[i]))

	compressed_bits = huffman.estimate(real_alphas + imag_alphas)
	print('Compressed: ' + str(compressed_bits) + ' bits')
	print('Uncompressed: ' + str(N*16) + ' bits')
	print('Compression ratio: ' + str(((N*16)/compressed_bits)))

	print('Uncompressing...')

	new_alphas = de_quantisize(real_alphas, imag_alphas, min_val, max_val, max_size)

	output_name = os.path.splitext(file_name)[0] + '_compressed.wav'
	output = wave.open(output_name, 'wb')
	output.setparams(f.getparams())
	
	inverse_fft = numpy.fft.ifft(new_alphas)

	dis = math.sqrt(distortion(ks, (int(x.real) for x in inverse_fft))/N)
	print('Distortion: ' + str(dis))

	for num in inverse_fft:
		truncate = clamp(int(num.real), -32768, 32767)
		b = truncate.to_bytes(2, byteorder = 'little', signed = True)
		output.writeframes(b)

	print('Saved as audio ' + output_name)

def distortion(original, compressed):
	distortion = 0
	for o, c in zip(original, compressed):
		distortion += math.pow((o - c), 2)
	return distortion

def clamp(n, minn, maxx):
	return max(min(maxx, n), minn)

def quantisize(alphas, min_val, max_val, max_size):
	real_alphas = []
	imag_alphas = []
	fn  = lambda x: round((((x - min_val)/(max_val - min_val))* max_size))

	for alpha in alphas:
		real_alphas.append(fn(alpha.real))
		imag_alphas.append(fn(alpha.imag))
	return real_alphas, imag_alphas

def de_quantisize(real_alphas, imag_alphas, min_val, max_val, max_size):
	fn = lambda x: ((x/max_size)*(max_val - min_val)) + min_val
	new_alphas = []
	for i in range(len(real_alphas)):
		new_alphas.append(complex(fn(real_alphas[i]), fn(imag_alphas[i])))
	new_alphas.extend(new_alphas[1:])
	return new_alphas

def get_samples(f):
	ks = []
	for i in range(f.getnframes()):
		ks.append(int.from_bytes(f.readframes(1), byteorder = 'little', signed = True))
	return ks

def get_alphas(f, epsilon, ks):
	N = f.getnframes()
	epsilon = 0.1

	alphas = numpy.fft.fft(ks)
	n = math.floor(N/2) + 1
	alphas = alphas[:n]

	for i, alpha in enumerate(alphas):
		if (abs(alpha) < epsilon):
			alphas[i] = 0
	return alphas

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