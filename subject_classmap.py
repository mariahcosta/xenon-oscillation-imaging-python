"""Module for oscillation imaging subject."""
import datetime
import glob
import logging
import os
import pdb

import nibabel as nib
import numpy as np
import scipy.io as sio
from ml_collections import config_dict

import segmentation
from utils import binning, constants, img_utils, io_utils, metrics, spect_utils


class Subject(object):
    """Module to for processing oscillation imaging.

    Attributes:
        config (config_dict.ConfigDict): config dict

    """

    def __init__(self, config: config_dict.ConfigDict):
        """Init object."""
        logging.info("Initializing oscillation imaging subject.")
        self.config = config
        self.gas_highSNR = np.array([0.0])
        self.manual_segmentation_filepath = str(config.manual_seg_filepath)
        self.rbc_m_ratio = 0.0
        self.segmentation_key = str(config.segmentation_key)
        self.dict_dyn = {}
        self.dict_dis = {}

    def read_files(self):
        """Read in files.

        Read in the dynamic spectroscopy (if it exists) and the dissolved-phase image
        data. Currently only supports twix files but will be extended to support
        other files.
        """
        self.dict_dyn = io_utils.read_dyn_twix(str(self.config.filepath_twix_dyn))
        self.dict_dis = io_utils.read_dis_twix(str(self.config.filepath_twix_dis))

    def calculate_static_spectroscopy(self):
        """Calculate static spectroscopy to derive the RBC:M ratio.

        If a manual RBC:M ratio is specified, use that instead.
        """
        if self.config.rbc_m_ratio > 0:  # type: ignore
            self.rbc_m_ratio = float(self.config.rbc_m_ratio)  # type: ignore
            logging.info("Using manual RBC:M ratio of {}".format(self.rbc_m_ratio))
        else:
            logging.info("Calculating RBC:M ratio from static spectroscopy.")
            self.rbc_m_ratio = spect_utils.calculate_static_spectroscopy(
                fid=self.dict_dyn[constants.IOFields.FIDS_DIS],
                dwell_time=self.dict_dyn[constants.IOFields.DWELL_TIME],
                tr=self.dict_dyn[constants.IOFields.TR],
                center_freq=self.dict_dyn[constants.IOFields.FREQ_CENTER],
                rf_excitation=self.dict_dyn[constants.IOFields.FREQ_EXCITATION],
                plot=False,
            )

    def readMatFile(self):
        """Read in Mat files."""
        return

    def reconstruction(self):

        return

    def segmentation(self):
        """Segment the thoracic cavity."""

        if self.segmentation_key == constants.SegmentationKey.CNN_VENT.value:
            logging.info("Performing neural network segmenation.")
            self.mask_reg = segmentation.predict(self.gas_highSNR)
        elif self.segmentation_key == constants.SegmentationKey.SKIP.value:
            self.mask_reg = np.ones_like(self.ventilation)
        elif self.segmentation_key == constants.SegmentationKey.MANUAL_VENT.value:
            logging.info("loading mask file specified by the user.")
            try:
                mask = glob.glob(self.manual_segmentation_filepath)[0]
                self.mask_reg = np.squeeze(np.array(nib.load(mask).get_fdata()))
            except ValueError:
                logging.error("Invalid mask nifti file.")
        elif self.segmentation_key == constants.SegmentationKey.THRESHOLD_VENT.value:
            logging.info("segmentation via thresholding.")
            self.mask_reg = (
                self.ventilation
                > np.percentile(
                    self.ventilation, constants._VEN_PERCENTILE_THRESHOLD_SEG
                )
            ).astype(bool)
            self.mask_reg = img_utils.remove_small_objects(self.mask_reg).astype(
                "float64"
            )
        else:
            raise ValueError("Invalid segmentation key.")

    def oscillation_binning(self):
        """Bin oscillation image to colormap bins."""
        bin_threshold = constants.REFERENCESTATS.REF_BINS_VEN_GRE
        (
            self.ventilation,
            self.ventilation_binning,
            self.mask_reg_vent,
        ) = binning.gasBinning(
            image=abs(self.ventilation_cor),
            bin_threshold=bin_threshold,
            mask=self.mask_reg,
            percentile=constants._VEN_PERCENTILE_RESCALE,
        )

    def generate_statistics(self):
        """Calculate ventilation image statistics."""

    def generate_figures(self):
        """Export image figures."""

    def generateHtmlPdf(self):
        """Generate HTML and PDF files."""

    def generateCSV(self):
        """Generate a CSV file."""

    def saveMat(self):
        """Save the instance variables into a mat file."""
        sio.savemat(os.path.join(self.data_dir, self.subject_id + ".mat"), vars(self))

    def savefiles(self):
        """Save select images to nifti files and instance variable to mat."""
        pathOutputcombinedmask = os.path.join(
            self.data_dir, constants.OutputPaths.GRE_MASK_NII
        )

        io_utils.export_nii(self.mask_reg, pathOutputcombinedmask)
        self.saveMat()
