import wave, cmath, math

def main():
	f = wave.open('audio/corto2.wav')
	N = f.getnframes()
	ks = []
	

	for i in range(N):
		ks.append(int.from_bytes(f.readframes(1), byteorder = 'little'))

	for i in range(10):
		print(ks[i])

	alphas = dft(ks)
	data = inverse_dft(alphas, N)

	print('------------------------------------------------')
	for i in range(10):
		print(round(abs(data[i])))
	

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
    return [x.real/len(v) for x in recursive_inverse_fft(v)]
	
	
if __name__ == '__main__':
	main()