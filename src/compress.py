import wave, cmath, math, numpy, os, huffman, matplotlib.pyplot as plt

def compress(file_name, L, epsilon):
    max_size = math.pow(2,L) - 1
    f = wave.open(file_name)
    N = f.getnframes()
    ks = get_samples(f)

    print('Compressing...')

    alphas = get_alphas(N, epsilon, ks)

    min_val, max_val = get_max_and_min(alphas)
    
    real_alphas, imag_alphas = quantisize(alphas, min_val, max_val, max_size)


    compressed_bits = huffman.estimate(real_alphas + imag_alphas)
    print('Compressed: ' + str(compressed_bits) + ' bits')
    print('Uncompressed: ' + str(N*16) + ' bits')
    print('Compression ratio percentage: ' + str(((N*16)/compressed_bits) * 100))

    print('Uncompressing...')

    new_alphas = de_quantisize(real_alphas, imag_alphas, min_val, max_val, max_size)

    output_name = os.path.splitext(file_name)[0] + '_compressed.wav'
    output = wave.open(output_name, 'wb')
    output.setparams(f.getparams())
    
    compressed = inverse(new_alphas)

    dis = distortion(ks, compressed)
    print('Distortion: ' + str(dis))

    # Si el número se excede de 2 bytes se trunca al máximo o mínimo tamaño de un short.
    # Esto puede pasar ya que al cuantificar el coeficiente, se pierde mucha presición (Sobre todo 
    # si se elije un L chico). Entonces, al descuantificar se puede ir de rango. Por ejemplo si al
    # cuantificarlo el valor es 3.12 y, el mínimo es negativo al truncarlo eso da 3. Luego al 
    # descuantificar se hace ((3*A)/B) + min, siendo A = (max -min) y B = 2^L -1. 
    # ((3*A)/B) < ((3.12*A)/B) y min es negativo por lo que el resultado es más chico que el
    #  coeficiente original. Es más, puede irse de rango siendo menor a -32768.
    print('Saving file...')
    for num in compressed:
        b = num.to_bytes(2, byteorder = 'little', signed = True)
        output.writeframes(b)

    print('Saved as audio ' + output_name)

def plot_epsilon(L, start, end, step, n):
    cr_array =[]
    dis_array = []
    epsilons = numpy.arange(start,end + step, step)
    print('Starting...')
    for epsilon in epsilons:
        dis = 0
        compression_ratio = 0
        for i in range(n):
            f = wave.open('audio/sample' + str(i + 1) + '.wav')
            aux_dis, aux_cr = get_compression_and_distortion(f, epsilon, L)
            dis += aux_dis
            compression_ratio += aux_cr
        print('Calculated for epsilon = ' + str(epsilon))

        cr_array.append(compression_ratio/n)
        dis_array.append(dis/n)
    print('Plotting...')
    plot(cr_array, epsilons, 'Epsilon', 'Compression ratio', 'compression_ratio_epsilon', 0.1, start, end, step, 'Compression rate vs. epsilon')
    plot(dis_array, epsilons, 'Epsilon', 'Distortion', 'distortion_epsilon', 0.1, start, end, step, 'Distortion vs. epsilon')
    print('Plotted')

def plot_L(epsilon, n):
    cr_array =[]
    dis_array = []
    print('Starting...')
    for L in range(1,9):
        dis = 0
        compression_ratio = 0
        for i in range(n):
            f = wave.open('audio/sample' + str(i + 1) + '.wav')
            aux_dis, aux_cr = get_compression_and_distortion(f, epsilon, L)
            dis += aux_dis
            compression_ratio += aux_cr
        print('Calculated for L = ' + str(L))
        cr_array.append(compression_ratio/n)
        dis_array.append(dis/n)
    print('Plotting...')
    plot(cr_array, [1,2,3,4,5,6,7,8], 'L = number of bits', 'Compression ratio', 'compression_ratio_L', 1.5, 1, 9, 1, 'Compression rate vs. L')
    plot(dis_array, [1,2,3,4,5,6,7,8], 'L = number of bits', 'Distortion', 'distortion_L', max(dis_array)/10, 1, 9, 1, 'Distortion vs. L')
    print('Plotted')

def plot(array, x, x_label, ylabel, file_name, label_inc, start, end, step, title):
    y_max = max(array)
    y_max += label_inc*5
    y_min = max(min(array)-(label_inc*5), 0)
    plt.figure().suptitle(title)
    plt.ylabel(ylabel)
    plt.xlabel(x_label)
    plt.plot(x, array, 'ro')
    plt.axis([x[0] - step , x[-1] + step, y_min, y_max])
    prev_val = 0
    alternate = False
    for i,j in zip(numpy.arange(start, end, step),array):
        if abs(prev_val - j) > 0.0001 :
            plt.annotate(str(round(j,2)),xy=(i-step/2, j + label_inc))
        prev_val=j
        label_inc= -label_inc
    plt.savefig('graphs/' + file_name + '.png', format = 'png')
    plt.clf()
    

def get_compression_and_distortion(f, epsilon, L):
    N = f.getnframes()
    max_size = math.pow(2,L) - 1
    uncompressed_bits = N*16
    ks = get_samples(f)
    coefs  = get_alphas(N, epsilon, ks)

    min_val, max_val = get_max_and_min(coefs)
    real_coefs, imag_coefs = quantisize(coefs, min_val, max_val, max_size)
    compressed_bits = huffman.estimate(real_coefs + imag_coefs)
    compression_ratio = uncompressed_bits/compressed_bits
    new_coefs = de_quantisize(real_coefs, imag_coefs, min_val, max_val, max_size)

    compressed_coefs = inverse(new_coefs)
    dis = distortion(ks, compressed_coefs)
    return dis, compression_ratio

def inverse(coefs):
    inverse_fft = numpy.fft.ifft(coefs)
    ans = []
    for num in inverse_fft:
        truncate = clamp(int(num.real), -32768, 32767)
        ans.append(truncate)
    return ans

def distortion(original, compressed):
    distortion = 0
    for o, c in zip(original, compressed):
        distortion += math.pow((o - c), 2)
    return math.sqrt(distortion/len(original))

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

def get_alphas(N, epsilon, ks):
    alphas = numpy.fft.fft(ks)
    n = math.floor(N/2) + 1
    alphas = alphas[:n]

    for i, alpha in enumerate(alphas):
        if (abs(alpha) < epsilon):
            alphas[i] = complex(0,0)
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