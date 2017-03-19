import numpy as np
import seaborn as sns


def smoothProbabilities(p, degree):
    m = 1.0 / len(p)
    res = np.zeros(len(p), dtype='float')
    for i in xrange(len(p)):
        delta = m - p[i]
        if (delta > 0) :
            res[i] = p[i] + np.abs(delta) ** degree
        elif (delta < 0) :
            res[i] = p[i] - np.abs(delta) ** degree
        else :
            res[i] = p[i]
    return res/sum(res)

noteNames = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
chordNames = np.empty(24, dtype='object')
for i in xrange(12):
    p = i * 2
    chordNames[p] = noteNames[i]
    chordNames[p + 1] = noteNames[i] + ":min"

pOthers = np.array([
    113, 113, 1384, 1384, 410, 410, 326, 326, 2266, 2266, 20, 20, 2220, 2220, 412, 412, 454, 454, 1386, 1386,
    162, 162], dtype='float')
pOthers = pOthers / sum(pOthers)
pSelftransition = 5.0 / 8.0
pModeChange = 1.0 / 24.0
pMaj = np.concatenate((np.array([pSelftransition, pModeChange]), pOthers * (1.0 - pSelftransition - pModeChange)))
pMin = np.concatenate((np.array([pModeChange, pSelftransition]), pOthers * (1.0 - pSelftransition - pModeChange)))
pMaj = smoothProbabilities(pMaj, 1.055)
pMin = smoothProbabilities(pMin, 1.055)
transitionMatrix = np.zeros((24, 24))
for i in xrange(12):
    transitionMatrix[2 * i, :] = np.roll(pMaj, 2 * i)
    transitionMatrix[2 * i + 1, :] = np.roll(pMin, 2 * i)
transitionMatrix = 100 * transitionMatrix

ax = sns.heatmap(transitionMatrix, annot=True, fmt='.1f')
#ax.set_xticklabels(labels=noteNames, rotation=90)
#ax.set_yticklabels(labels=reversed(noteNames), rotation=30)
ax.set_xticklabels(labels=chordNames, rotation=90)
ax.set_yticklabels(labels=reversed(chordNames), rotation=30)
#sns.plt.gcf().subplots_adjust(bottom=0.35, left=0.19)
sns.plt.show()