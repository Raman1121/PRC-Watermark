import torch
from scipy.special import erf
from scipy.linalg import orth
import numpy as np


def sample(codeword, basis=None):
    # pseudogaussian = codeword * torch.abs(torch.randn_like(codeword, dtype=torch.float64))
    codeword_np = codeword.numpy()
    noise = np.random.randn(*codeword_np.shape)
    # Putting the noise in the fourier domain. Fourier transform of a gaussian is a gaussian
    try:
        fft_noise = torch.fft.fftshift(torch.fft.fft2(torch.tensor(noise)), dim=(-1, -2))
        coded_fourier_noise = codeword_np * np.abs(fft_noise.numpy())
        pseudogaussian = torch.fft.ifft2(torch.fft.ifftshift(coded_fourier_noise, dim=(-1, -2))).real
    except:
        import pdb; pdb.set_trace()
    
    if basis is None:
        return pseudogaussian
    return pseudogaussian @ basis.T


def recover_posteriors(z, basis=None, variances=None):
    if variances is None:
        default_variance = 1.5
        denominators = np.sqrt(2 * default_variance * (1+default_variance)) * torch.ones_like(z)
    elif type(variances) is float:
        denominators = np.sqrt(2 * variances * (1 + variances))
    else:
        denominators = torch.sqrt(2 * variances * (1 + variances))

    if basis is None:
        return erf(z / denominators)
    else:
        return erf((z @ basis) / denominators)

def random_basis(n):
    gaussian = torch.randn(n, n, dtype=torch.double)
    return orth(gaussian)
