import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from src.detecteurs_stat import cusum

x = np.random.default_rng(0).normal(0, 1, 3000)
x[2000:] += 3                       # un saut de 3 à t = 2000
print(cusum(x)[:3])                 # première alerte juste après 2000 (environ 2005)