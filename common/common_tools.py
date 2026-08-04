import time

def perf_test(func, data, rounds=30, sample=100, mode=''):
    results = []

    for _ in range(rounds):
        start = time.perf_counter()
    
        func(data[:sample])
    
        end = time.perf_counter()
        results.append(end-start)

    return sum(results)/rounds
