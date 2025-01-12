"""Signal processing util functions."""
import pdb
import sys
from typing import Any, Literal, Tuple

sys.path.append("..")
import numpy as np
import pywt
import scipy.optimize as optimize
import scipy.signal as signal
import scipy.stats as stats

from utils import constants


def _movmean(x: np.ndarray, n: int) -> np.ndarray:
    """Compute moving mean of x over n points.

    Args:
        x (np.ndarray): input data of shape (n,)
        n (int): number of points to average over

    Returns:
        np.ndarray: moving mean of shape (n,)
    """
    return np.convolve(x, np.ones((n,)) / n, mode="same")


def _getxygrid(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Get x and y grid.

    This is a lazy implementation of the Matlab function getxygrid in sethandles.m
    Args:
        x (np.ndarray): x data of shape (n,) must have at least 2 elements
            x cannot also have repeated x entries.
        y (np.ndarray): y data of shape (n,) must have at least 2 elements
    Returns:
        Tuple of x and y grid respectively
    """
    # check number of data points to be > 2
    assert len(x) > 2, "x must have at least 2 elements"
    # sort data points to be in order of increasing x
    sort_idx = np.argsort(x)
    x = x[sort_idx]
    y = y[sort_idx]

    return (x, y)


def _sinnstart(x: np.ndarray, y: np.ndarray, n: int) -> np.ndarray:
    """Get starting points fit for sum of n sine functions.

    Computes a starting for the parameters of a sum of n sine functions. By
    Running the y data through a fft, and then locating peaks in results, we
    can find the starting value of the frequency of each sine function 'b'
    in the function y = a*sin(b*x+c). Because a phase-shifted sine function
    is separable and can be converted to a sum of sine and cosine functions,
    starting values for amplitude 'a' and phase 'c' can be found.

    Returns:
        Starting values for the parameters of a sum of n sine functions of
            shape (n * 3, )
    """
    lenx = len(x)
    x, y = _getxygrid(x, y)
    # if data size is too small, cannot find starting values
    if len(x) < 2:
        return np.random.rand(n * 3)
    # loop for sum of sines functions
    start = np.zeros(3 * n)
    oldpeaks = np.array([])
    freqs = np.zeros(n)
    res = np.copy(y)
    for i in range(n):
        # apply fft to the current residuals
        fy = np.fft.fft(res)
        # omit frequencies already used
        if len(oldpeaks) > 0:
            fy[oldpeaks] = 0
        # get starting value for frequency using fft peaks
        maxloc = np.argmax(np.abs(fy[np.arange(0, np.floor(lenx / 2)).astype(int)]))
        np.append(oldpeaks, maxloc)
        w = 2 * np.pi * max((0.5, maxloc)) / (x[-1] - x[0])
        freqs[i] = w
        # compute fourier terms using all frequencies we have so far
        X = np.zeros((lenx, 2 * (i + 1)))
        for j in range(i + 1):
            X[:, 2 * j] = np.sin(freqs[j] * x)
            X[:, 2 * j + 1] = np.cos(freqs[j] * x)
        # fit these terms to get the non-frequency starting values
        ab = np.linalg.lstsq(X, y, rcond=None)[0]
        if i < n:
            res = y - np.matmul(X, ab)
    # all frequencies found, now compute starting values from all
    # frequencies and the corresponding coefficients.
    for i in range(n):
        start[3 * i] = np.sqrt(ab[2 * i] ** 2 + ab[2 * i + 1] ** 2)
        start[3 * i + 1] = freqs[i]
        start[3 * i + 2] = np.arctan2(ab[2 * i + 1], ab[2 * i])
    return start


def _sinbounds(n: int) -> Tuple[np.ndarray, np.ndarray]:
    """Get bounds for sum of n sine functions.

    Upper bounds are inf. Lower bounds are [-inf, 0, -inf] repeated n times.

    Args:
        n (int): number of sine functions
    Returns:
        Tuple of lower and upper bounds respectively of length n * 3
    """
    return (
        np.tile([-np.inf, 0, -np.inf], n),
        np.tile([np.inf, np.inf, np.inf], n),
    )


def boxcox(data: np.ndarray):
    """Apply box cox transformation on data.

    Args:
        data (np.ndarray): data to be transformed of shape (n,)
    Returns:
        Tuple of transformed data and box cox lambda
    """
    return stats.boxcox(data)


def inverse_boxcox(
    boxcox_lambda: float, data: np.ndarray, scale_factor: float
) -> np.ndarray:
    """Apply inverse box cox transformation on data.

    Args:
        boxcox_lambda (float): box cox lambda
        data (np.ndarray): data to be transformed of shape (n,)
        scale_factor (float): scale factor to be applied to the data
    """
    return np.power(boxcox_lambda * data + 1, 1 / boxcox_lambda) - scale_factor


def remove_gasphase_contamination(
    data_dissolved: np.ndarray,
    data_gas: np.ndarray,
    dwell_time: float,
    freq_gas_acq_diss: float,
    phase_gas_acq_diss: float,
    area_gas_acq_diss: float,
    fa_gas: float,
) -> np.ndarray:
    """Remove gas phase contamination in dissolved k-space.

    Takes gas phase k-space and modifies it using NMR fits and gas phase k0
    to produce the expected gas phase contamination k-space data which is
    then removed from the initial contaminated dissolved phase k-space.

    Args:
        data_dissolved (np.ndarray): dissolved k-space data of shape
            (n_projections, n_points)
        data_gas (np.ndarray): gas phase k-space data of shape
            (n_projections, n_points)
        dwell_time (float): dwell time in seconds.
        freq_gas_acq_diss (float): gas frequency offset in dissolved
            spectra acquisition in Hz.
        phase_gas_acq_diss (float): gas phase in dissolved spectra acquisition.
            in degrees.
        area_gas_acq_diss (float): gas area in dissolved spectra acquisition.
        fa_gas (float): gas flip angle in degrees.
    Returns:
        Gas phase corrected dissolved k-space data of shape (n_projections, n_points)
    Author: Matt Willmering
    Paper: https://pubmed.ncbi.nlm.nih.gov/33665905/
    """
    # step 0: calculate parameters
    arr_t = dwell_time * np.arange(data_dissolved.shape[1])
    # step 1: modulate contamination (gas) to dissolved frequency - first order
    # phase approximation
    phase_shift1 = 2 * np.pi * freq_gas_acq_diss * arr_t  # calculate phase accumulation
    contamination_kspace1 = data_gas * np.exp(1j * phase_shift1)
    # step 2: zero order phase shift of contamination estimation
    phase_shift2 = phase_gas_acq_diss - 180 / np.pi * np.mean(np.angle(data_gas[:, 0]))
    contamination_kspace2 = contamination_kspace1 * np.exp(
        1j * np.pi / 180 * phase_shift2
    )
    # step 3: scale contamination estimation
    scale_factor = area_gas_acq_diss / _movmean(np.abs(data_gas[:, 0]), 100)[-1]
    contamination_kspace3 = (
        contamination_kspace2 * scale_factor / np.cos(np.pi / 180 * fa_gas)
    )
    # step 4: return subtracted contamination
    return data_dissolved - contamination_kspace3


def dixon_decomposition(
    data_dissolved: np.ndarray,
    rbc_m_ratio: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Apply 1-point dixon decomposition on FID data.

    Applies phase shift to the dissolved data such that the RBC and membrane are
    separated into the imaginary and real channel respectively.
    Does NOT also apply B0 inhomogeneity correction.

    Args:
        data_dissolved (np.ndarray): dissolved FID data of shape
            (n_projections, n_points)
        rbc_m_ratio (float): RBC:m ratio
    Returns:
        Tuple of decomposed RBC and membrane data respectively
    """
    desired_angle = np.arctan2(rbc_m_ratio, 1.0)
    # use k0 to determine the phase shift
    total_dissolved = np.sum(data_dissolved[:, 0])
    current_angle = np.arctan2(np.imag(total_dissolved), np.real(total_dissolved))
    delta_angle = desired_angle - current_angle

    rotated_data = np.multiply(data_dissolved, np.exp(1j * delta_angle))
    return np.imag(rotated_data), np.real(rotated_data)


def smooth(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    """Smooth response data.

    Implements a smoothing function that is equivalent to the MATLAB smooth function.
    Source: https://www.mathworks.com/help/curvefit/smooth.html

    Args:
        data (np.ndarray): 1-D array data to be smoothed.
        window_size (int): size of the smoothing window. Defaults to 5.
    Returns:
        Smoothed data.
    """
    out0 = np.convolve(data, np.ones(window_size, dtype=int), "valid") / window_size
    r = np.arange(1, window_size - 1, 2)
    start = np.cumsum(data[: window_size - 1])[::2] / r
    stop = (np.cumsum(data[:-window_size:-1])[::2] / r)[::-1]
    return np.concatenate((start, out0, stop))


def bandpass(data: np.ndarray, lowcut: float, highcut: float, fs: float) -> np.ndarray:
    """Bandpass filter.

    Implements a bandpass filter using a butterworth filter.
    Equivalent to MATLAB bandpass filter.

    Args:
        data (np.ndarray): 1-D array data to be filtered.
        lowcut (float): lowcut frequency in Hz.
        highcut (float): highcut frequency in Hz.
        fs (float): sampling frequency.
    Returns:
        Filtered data.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(6, [low, high], analog=False, btype="bandpass", output="sos")
    return np.array(signal.sosfiltfilt(sos, data))


def lowpass(data: np.ndarray, highcut: float, fs: float) -> np.ndarray:
    """Bandpass filter.

    Implements a bandpass filter using a butterworth filter.
    Equivalent to MATLAB bandpass filter.

    Args:
        data (np.ndarray): 1-D array data to be filtered.
        highcut (float): highcut frequency in Hz.
        fs (float): sampling frequency.
    Returns:
        Filtered data.
    """
    nyq = 0.5 * fs
    high = highcut / nyq
    sos = signal.butter(6, high, btype="lowpass", output="sos")
    return np.array(signal.sosfiltfilt(sos, data))


def fit_sine(data: np.ndarray) -> np.ndarray:
    """Fit the data to a sum of 8 sine waves.

    Args:
        data (np.ndarray): 1-D array data to be fitted.
    Returns:
        Fitted data. Same shape as input data.
    """
    x = np.arange(data.shape[0])
    y = data

    def func(x, *args):
        return (
            args[0] * np.sin(args[1] * x + args[2])
            + args[3] * np.sin(args[4] * x + args[5])
            + args[6] * np.sin(args[7] * x + args[8])
            + args[9] * np.sin(args[10] * x + args[11])
            + args[12] * np.sin(args[13] * x + args[14])
            + args[15] * np.sin(args[16] * x + args[17])
            + args[18] * np.sin(args[19] * x + args[20])
            + args[21] * np.sin(args[22] * x + args[23])
        )

    p0 = _sinnstart(x, y, 8)
    bounds = _sinbounds(8)
    popt, _ = optimize.curve_fit(
        func,
        x,
        y,
        p0=p0,
        bounds=bounds,
    )
    return func(x, *popt)


def moving_average_filter(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Apply a moving average filter to 1D data.

    Args:
        data (np.ndarray): 1D array of data.
        window_size (int): Size of the moving window for averaging.

    Returns:
        np.ndarray: Filtered data after applying the moving average.

    Raises:
        ValueError: If the window size is not a positive odd integer.

    """
    if window_size <= 0 or window_size % 2 == 0:
        raise ValueError("Window size must be a positive odd integer.")

    half_window = window_size // 2
    filtered_data = np.convolve(data, np.ones(window_size) / window_size, mode="same")
    return filtered_data[half_window:-half_window]


def median_filter(data: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    Apply a median filter to 1D data.

    Args:
        data (np.ndarray): 1D array of data.
        window_size (int): Size of the moving window for median filtering.

    Returns:
        np.ndarray: Filtered data after applying the median filter.

    Raises:
        ValueError: If the window size is not a positive odd integer.

    """
    if window_size <= 0 or window_size % 2 == 0:
        raise ValueError("Window size must be a positive odd integer.")

    half_window = window_size // 2
    filtered_data = np.zeros_like(data)
    for i in range(half_window, len(data) - half_window):
        window = data[i - half_window : i + half_window + 1]
        filtered_data[i] = np.median(window)

    return filtered_data


def wavelet_denoise(
    signal: np.ndarray, wavelet: str = "db4", level: int = 1
) -> np.ndarray:
    """
    Apply wavelet denoising to a 1D signal.

    Args:
        signal (np.ndarray): Input signal.
        wavelet (str): Name of the wavelet function to use. Defaults to 'db4'.
        level (int): Decomposition level for the wavelet transform. Defaults to 1.

    Returns:
        np.ndarray: Denoised signal.

    """
    # Perform wavelet decomposition
    coeffs = pywt.wavedec(signal, wavelet, level=level)

    # Estimate the noise level based on the standard deviation of the highest-frequency coefficients
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745

    # Apply soft thresholding to the detail coefficients
    denoised_coeffs = [pywt.threshold(c, value=sigma, mode="soft") for c in coeffs]

    # Reconstruct the denoised signal
    denoised_signal = pywt.waverec(denoised_coeffs, wavelet)

    return denoised_signal


def detrend(data: np.ndarray) -> np.ndarray:
    """Remove bi-exponential trend along axis from data.

    Fits the data to a bi-exponential decay function and removes the trend.

    Args:
        data (np.ndarray): 1-D array data to be detrended.
    Returns:
        Detrended data. Same shape as input data.
    """
    x = np.arange(data.shape[0])
    y = data

    def func(x, a, b, c, d):
        return a * np.exp(-b * x) + c * np.exp(-d * x)

    popt, _ = optimize.curve_fit(
        func,
        x,
        y,
        p0=[1, 0.1, 1, 0.1],
        method="trf",
        ftol=1e-6,
        xtol=1e-6,
        max_nfev=600,
    )
    return data - func(x, *popt)


def find_peaks(data: np.ndarray, distance: int = 5) -> np.ndarray:
    """Find peaks in data.

    Implements a peak finding function using scipy.signal.find_peaks.

    Args:
        data (np.ndarray): 1-D array data to be filtered.
        distance (int): minimum distance between peaks. Defaults to 5. Units are
        number of points.

    Returns:
        Array of indices of peaks.
    """
    peaks, _ = signal.find_peaks(data, distance=distance)
    return peaks[np.argwhere(data[peaks] > 0).flatten()]


def get_heartrate(data: np.ndarray, ts: float) -> float:
    """Calculate heart rate from data.

    Implements a heart rate calculation function by finding the strongest peak
    in the fourier domain of the data.

    Args:
        data (np.ndarray): 1-D array data to be filtered.
        ts (float): sampling period in seconds.

    Returns:
        Heart rate in beats per minute.
    """
    fft_data = np.abs(np.fft.fftshift(np.fft.fft(data)))
    freq = np.fft.fftshift(np.fft.fftfreq(len(data), ts))
    # Exclude the DC frequency by considering only non-DC frequencies
    non_dc_indices = np.nonzero(freq)
    fft_data_non_dc = fft_data[non_dc_indices]
    freq_non_dc = freq[non_dc_indices]

    return np.abs(freq_non_dc[np.argmax(fft_data_non_dc)] * 60)


def awgn(sig: np.ndarray, SNR: float) -> np.ndarray:
    """Add white gaussian noise.

    Args:
        sig (np.ndarray): signal to be added with noise.
        SNR (float): signal to noise ratio in dB.
    """
    sig_power = np.sum(np.abs(sig) ** 2) / len(sig)
    noise_power = sig_power / (10 ** (SNR / 10))

    if np.isreal(sig):
        noise = np.sqrt(noise_power) * np.random.randn(len(sig))
    else:
        noise = np.sqrt(noise_power / 2) * (
            np.random.randn(len(sig)) + 1j * np.random.randn(len(sig))
        )
    return sig + noise


def find_high_low_indices(
    data: np.ndarray,
    peak_distance: int,
    distance_threshold: float = 0.2,
    same_length: bool = True,
    method: str = constants.BinningMethods.PEAKS,
) -> Tuple[np.ndarray, np.ndarray]:
    """Find indices of high and low signal bins.

    Args:
        data (np.ndarray): RBC 1-D data of shape (n_projections,)
        peak_distance (int): distance between peaks in number of points.
        distance_threshold (float): threshold for neighbouring peaks. Defaults to 0.2.
            Value must be between 0 and 1 with 0 being taking only the found peaks and 1
            being taking all points between the peaks.
        same_length (bool): whether to force high and low bins are of the same length.

    Returns:
        Tuple of indices of high and low signal bins respectively.
    """
    high_indices = np.array([])
    low_indices = np.array([])

    if method == constants.BinningMethods.PEAKS:
        high_peaks = find_peaks(data=data, distance=int(0.6 * peak_distance))
        low_peaks = find_peaks(data=-data, distance=int(0.6 * peak_distance))

        left = np.ceil(peak_distance * distance_threshold / 2).astype(int)
        right = left + 1
        for peak in high_peaks:
            high_indices = np.append(high_indices, np.arange(peak - left, peak + right))
        for peak in low_peaks:
            low_indices = np.append(low_indices, np.arange(peak - left, peak + right))
    elif method == constants.BinningMethods.THRESHOLD:
        data_norm = (data - np.mean(data)) / np.std(data)
        high_indices = np.argwhere(data_norm > 0.7).flatten()
        low_indices = np.argwhere(data_norm < -0.7).flatten()
    else:
        raise ValueError(f"Method {method} not implemented.")

    # remove indices that go are below zero and above length of the data
    high_indices = np.delete(high_indices, np.argwhere(high_indices < 0))
    low_indices = np.delete(low_indices, np.argwhere(low_indices < 0))
    high_indices = np.delete(high_indices, np.argwhere(high_indices >= len(data)))
    low_indices = np.delete(low_indices, np.argwhere(low_indices >= len(data)))
    if same_length:
        if len(high_indices) > len(low_indices):
            high_indices = high_indices[: len(low_indices)]
        elif len(low_indices) > len(high_indices):
            low_indices = low_indices[: len(high_indices)]
    return np.sort(high_indices).astype(int), np.sort(low_indices).astype(int)
