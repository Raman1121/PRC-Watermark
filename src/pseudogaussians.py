import torch
from scipy.special import erf
from scipy.linalg import orth
import numpy as np


def sample(codeword, basis=None, target_shape=(4, 64, 64)):

    # Reshape codeword to the target 2D structure (e.g., C, H, W)
    codeword_reshaped = codeword.reshape(target_shape)
    codeword_np = codeword_reshaped.cpu().numpy() # Use cpu() if codeword might be on GPU

    # Generate noise with the target 2D shape directly
    noise = np.random.randn(*target_shape)
    noise_tensor = torch.tensor(noise, dtype=torch.float32) # Match typical FFT dtype

    # --- Perform 2D FFT operations ---
    # Put the noise in the fourier domain. Fourier transform of a gaussian is a gaussian
    # fft2 operates on the last two dimensions by default, which is (64, 64) here.
    fft_noise = torch.fft.fftshift(torch.fft.fft2(noise_tensor), dim=(-1, -2))

    # Ensure codeword_np is broadcastable if needed, but shape should match fft_noise now
    # Use torch operations for consistency and potential GPU acceleration
    # Using abs on the complex fft result
    coded_fourier_noise = torch.tensor(codeword_np, device=fft_noise.device) * torch.abs(fft_noise.real) # Apply codeword amplitude modulation in Fourier domain

    # Apply inverse shift and inverse FFT
    # ifftshift operates on the last two dimensions by default
    pseudogaussian = torch.fft.ifft2(torch.fft.ifftshift(coded_fourier_noise, dim=(-1, -2))).real

    if basis is None:
        return pseudogaussian
    return pseudogaussian @ basis.T

    # codeword_np = codeword.numpy()
    # pseudogaussian_np = codeword_np * np.abs(np.random.randn(*codeword_np.shape))
    # pseudogaussian = torch.from_numpy(pseudogaussian_np).to(dtype=torch.float64)
    # if basis is None:
    #     return pseudogaussian
    # return pseudogaussian @ basis.T

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
