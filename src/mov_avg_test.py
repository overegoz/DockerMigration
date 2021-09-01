import matplotlib.pyplot as plt
import random

def mov_avg(v, window):
    """이동평균 이용하여 초음파 거리 계산 (배치식)."""
    avg = []
    for i in range(len(v)):
        if i < window-1:
            avg.append(sum(v[:i+1]) / len(v[:i+1]))
        else:
            avg.append(sum(v[i-window+1:i+1]) / window)
    return avg

data = []
for i in range(100):
    data.append(random.randint(0,100))

avg = mov_avg(data, 3)
rg = list(range(100))
plt.plot(rg, data, rg, avg)
plt.show()