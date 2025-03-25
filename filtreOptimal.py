import numpy as np
from scipy import signal
from scipy.linalg import toeplitz
import scipy.io.wavfile as swav

s_tr = swav.read("file.wav")

K = 200

Gam = signal.correlate(s_tr.astype(np.float32), s_tr.astype(np.float32), mode='full', method='auto')
Gam /= len(s_tr)
Gam = Gam[len(Gam)//2 - K:len(Gam)//2 + K + 1]
lags = signal.correlation_lags(len(s_tr), len(s_tr), mode="full")
lags = lags[len(lags)//2 - K:len(lags)//2 + K + 1]

M = 38

# matrice du systeme lineaire 
G = toeplitz(c= Gam[K:K+M+1], r = Gam[K:K+M+1]) #Attention aux indices...

# second membre du systeme lineaire
b = np.zeros(M+1)
b[0] = -1


# solution du systeme G.Phi = b
Phi = np.linalg.pinv(G) @ b

# coefficients du filtre de Wiener
h = -Phi/Phi[0]

# puissance de l'erreur
sigma = np.sqrt(-1/Phi[0])



s_hat = np.zeros(len(s_tr))
for i in range(len(s_tr)):
    for k in range(M):
        s_hat[i] += h[k]*s_tr[i-k]

eps_causal = s_tr - s_hat


s_anti_hat = np.zeros(len(s_tr))
s_tr = np.flip(s_tr)
for i in range(len(s_tr)):
    for k in range(M):
        s_anti_hat[i] += h[k]*s_tr[i-k]
s_anti_hat = np.flip(s_anti_hat)
eps_anticausal = s_tr - s_anti_hat