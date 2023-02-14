"""Base configuration file."""
import sys

from ml_collections import config_dict

# parent directory
sys.path.append("..")

from config import base_config
from utils import constants


class Config(base_config.Config):
    """Base config file."""

    def __init__(self):
        """Initialize config parameters."""
        super().__init__()
        self.data_dir = "/mnt/d/Patients/007-028B/"
        self.platform = constants.Platform
        self.scan_type = constants.ScanType.NORMALDIXON.value
        self.segmentation_key = constants.SegmentationKey.CNN_VENT.value
        self.site = constants.Site.DUKE.value
        self.subject_id = "test"
        self.rbc_m_ratio = 0.0
        self.kernel_sharpness = 0.14


def get_config() -> config_dict.ConfigDict:
    """Return the config dict. This is a required function.

    Returns:
        a ml_collections.config_dict.ConfigDict
    """
    return Config()