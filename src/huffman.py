from heapq import heappush, heappop, heapify
from collections import defaultdict
from collections import Counter


def encode(symb2freq):
    if len(list(symb2freq.keys())) == 1:
        return {list(symb2freq.keys())[0]: '0'}
    heap = [[wt, [sym, ""]] for sym, wt in list(symb2freq.items())]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return dict(sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p)))


def estimate(v):
    counter = Counter(v)
    huff_dict = encode(counter)
    total_bits = 0
    symbols = list(set(v))
    total_bits += len(symbols)
    for symbol in symbols:
        total_bits += len(huff_dict[symbol])

    total_bits+= 64*2 + 32 + 8

    for k, v in list(counter.items()):
         total_bits += len(huff_dict[k])*v
    return total_bits
