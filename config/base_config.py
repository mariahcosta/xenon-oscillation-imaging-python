"""Base configuration file."""
import sys

import numpy as np
from ml_collections import config_dict

# parent directory
sys.path.append("..")

from utils import constants


class Config(config_dict.ConfigDict):
    """Base config file.

    Attributes:
        data_dir: str, path to the data directory
        manual_seg_filepath: str, path to the manual segmentation nifti file
        remove_contamination: bool, whether to remove gas contamination
        remove_noisy_projections: bool, whether to remove noisy projections
        processes: Process, the evaluation processes
        params: Params, the important parameters
        platform: Platform, the scanner vendor platform
        scan_type: str, the scan type
        segmentation_key: str, the segmentation key
        site: str, the scan site
        subject_id: str, the subject id
        rbc_m_ratio: float, the RBC to M ratio
    """

    def __init__(self):
        """Initialize config parameters."""
        super().__init__()
        self.data_dir = ""
        self.manual_seg_filepath = ""
        self.processes = Process()
        self.recon = Recon()
        self.params = Params()
        self.platform = constants.Platform.SIEMENS.value
        self.scan_type = constants.ScanType.NORMALDIXON.value
        self.segmentation_key = constants.SegmentationKey.CNN_VENT.value
        self.site = constants.Site.DUKE.value
        self.dose = Dose()
        self.subject_id = "test"
        self.rbc_m_ratio = 0.0
        self.remove_contamination = False
        self.remove_noisy_projections = True


class Process(object):
    """Define the evaluation processes.

    Attributes:
        oscillation_mapping_recon: bool, whether to perform oscillation mapping
            with reconstruction
        oscillation_mapping_readin: bool, whether to perform oscillation mapping
            by reading in the mat file
    """

    def __init__(self):
        """Initialize the process parameters."""
        self.oscillation_mapping_recon = True
        self.oscillation_mapping_readin = False


class Recon(object):
    """Define reconstruction configurations.

    Attributes:
        kernel_sharpness_lr: float, the kernel sharpness for low resolution, higher
            SNR images
        kernel_sharpness_hr: float, the kernel sharpness for high resolution, lower
            SNR images
        n_skip_start: int, the number of frames to skip at the beginning
        n_skip_end: int, the number of frames to skip at the end
        key_radius: int, the key radius for the keyhole image
    """

    def __init__(self):
        """Initialize the reconstruction parameters."""
        self.kernel_sharpness_lr = 0.14
        self.kernel_sharpness_hr = 0.32
        self.n_skip_start = 100
        self.n_skip_end = 0
        self.key_radius = 9
        self.key_radius_pct = 0.3
        self.recon_size = 128
        self.recon_proton = False


class Params(object):
    """Define important parameters.

    Attributes:
        threshold_oscillation: np.ndarray, the oscillation amplitude thresholds for
            binning
        threshold_rbc: np.ndarray, the RBC thresholds for binning
    """

    def __init__(self):
        """Initialize the reconstruction parameters."""
        # used in the bugged matlab pipeline
        # self.threshold_oscillation = np.array(
        #     [-3.6436, 0.2917, 9.3565, 17.9514, 28.7061, 42.6798, 61.8248]
        # )
        # reprocessed with the new pipeline
        self.threshold_oscillation = np.array(
            [-2.02, 0.53, 3.66, 7.63, 12.99, 21.07, 35.56]
        )
        self.threshold_rbc = np.array([0.066, 0.250, 0.453, 0.675, 0.956]) / 2.0


class Dose(object):
    """Define dose details.

    These are not used in the pipeline, but are useful for creating statistics for
    paper writing.

    Attributes:
        de_spect: dose equivalent in ml of spectroscopy scan.
        de_dixon: dose equivalent in ml of dixon scan.
    """

    def __init__(self):
        """Initialize the scan parameters."""
        self.de_spect = 0.0
        self.de_dixon = 0.0


def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()
