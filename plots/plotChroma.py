import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

nnls_treble=[69.641, 68.667, 61.956]
rosa_stft=[45.958, 42.4316, 38.907]
rosa_cqt=[51.929, 51.202, 48.335]
essentia=[60.8324, 57.841, 50.676]
muller_clp=[60.8993, 60.278, 56.404]
muller_crp=[57.459, 57.279, 52.722]


x = np.arange(3)
plt.plot(x , nnls_treble, label='NNLS Chroma (treble)')
plt.plot(x , muller_clp, label='CLP (Muller)')
plt.plot(x , essentia, label='essentia hpcp')
plt.plot(x , muller_crp, label='CRP (Muller)')
plt.plot(x , rosa_cqt, label='librosa cqt chroma')
plt.plot(x , rosa_stft, label='librosa stft chroma')
LABELS = ["4 beats", "2 beats", "1 beat"]
plt.xticks(x, LABELS)
plt.ylabel('chord detection accuracy %')
plt.xlabel('averaging window length')
plt.legend()
plt.show()

