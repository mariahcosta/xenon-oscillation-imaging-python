"""Define important constants used throughout the pipeline."""
import enum

_FOVDIMSCALE = 10
_FOVINFLATIONSCALE2D = 10000.0
_FOVINFLATIONSCALE3D = 1000.0

_NUM_SLICE_GRE_MONTAGE = 14
_NUM_ROWS_GRE_MONTAGE = 2
_NUM_COLS_GRE_MONTAGE = 7

_DEFAULT_SLICE_THICKNESS = 3.125
_DEFAULT_PIXEL_SIZE = 3.125
_DEFAULT_MAX_IMG_VALUE = 255.0

_RAYLEIGH_FACTOR = 0.66
GRYOMAGNETIC_RATIO = 11.777  # MHz/T
_VEN_PERCENTILE_RESCALE = 99.0
_VEN_PERCENTILE_THRESHOLD_SEG = 80
_PROTON_PERCENTILE_RESCALE = 99.8


class IOFields(object):
    """General IOFields constants."""

    BIASFIELD_KEY = "biasfield_key"
    DWELL_TIME = "dwell_time"
    FA_DIS = "fa_dis"
    FA_GAS = "fa_gas"
    FIDS_DIS = "fids_dis"
    FIDS_GAS = "fids_gas"
    FOV = "fov"
    FOV = "fov"
    FREQ_CENTER = "freq_center"
    FREQ_EXCITATION = "freq_excitation"
    IMAGE = "image"
    INFLATION = "inflation"
    MASK_REG_NII = "mask_reg_nii"
    NPTS = "npts"
    ORIENTATION = "orientation"
    OUTPUT_PATH = "output_path"
    PIXEL_SIZE = "pixel_size"
    PROCESS_DATE = "process_date"
    PROTOCOL_NAME = "protocol_name"
    PROTON_DICOM_DIR = "proton_dicom_dir"
    PROTON_REG_NII = "proton_reg_nii"
    RAMP_TIME = "ramp_time"
    RAW_PROTON_MONTAGE = "raw_proton_montage"
    REGISTRATION_KEY = "registration_key"
    REMOVEOS = "removeos"
    SCAN_DATE = "scan_date"
    SCAN_TYPE = "scan_type"
    SEGMENTATION_KEY = "segmentation_key"
    SITE = "site"
    SLICE_THICKNESS = "slice_thickness"
    SOFTWARE_VERSION = "software_version"
    SUBJECT_ID = "subject_id"
    TE90 = "te90"
    TR = "tr"
    TR_DIS = "tr_dis"
    VEN_COR_MONTAGE = "bias_cor_ven_montage"
    VEN_CV = "ven_cv"
    VEN_DEFECT = "ven_defect"
    VEN_HIGH = "ven_high"
    VEN_HIST = "ven_hist"
    VEN_LOW = "ven_low"
    VEN_MEAN = "ven_mean"
    VEN_MEDIAN = "ven_median"
    VEN_MONTAGE = "ven_montage"
    VEN_SKEW = "ven_skewness"
    VEN_SNR = "ven_snr"
    VEN_STD = "ven_std"
    VENT_DICOM_DIR = "vent_dicom_dir"
    GRAD_DELAY_X = "grad_delay_x"
    GRAD_DELAY_Y = "grad_delay_y"
    GRAD_DELAY_Z = "grad_delay_z"
    N_SKIP_START = "n_skip_start"
    N_SKIP_END = "n_skip_end"
    N_FRAMES = "n_frames"


class OutputPaths(object):
    """Output file names."""

    GRE_MASK_NII = "GRE_mask.nii"
    GRE_REG_PROTON_NII = "GRE_regproton.nii"
    GRE_VENT_RAW_NII = "GRE_ventraw.nii"
    GRE_VENT_COR_NII = "GRE_ventcor.nii"
    GRE_VENT_BINNING_NII = "GRE_ventbinning.nii"
    VEN_RAW_MONTAGE_PNG = "raw_ven_montage.png"
    PROTON_REG_MONTAGE_PNG = "raw_proton_montage.png"
    VEN_COR_MONTAGE_PNG = "bias_cor_ven_montage.png"
    VEN_COLOR_MONTAGE_PNG = "ven_montage.png"
    VEN_HIST_PNG = "ven_hist.png"
    REPORT_CLINICAL_HTML = "report_clinical.html"
    TEMP_GRE_CLINICAL_HTML = "temp_clinical_gre.html"
    HTML_TMP = "html_tmp"
    REPORT_CLINICAL = "report_clinical"


class CNNPaths(object):
    """Paths to saved model files."""

    DEFAULT = "GREModel_20190323.h5"


class ImageType(enum.Enum):
    """Segmentation flags."""

    VENT = "vent"
    UTE = "ute"


class SegmentationKey(enum.Enum):
    """Segmentation flags."""

    CNN_VENT = "cnn_vent"
    CNN_PROTON = "cnn_proton"
    MANUAL_VENT = "manual_vent"
    MANUAL_PROTON = "manual_proton"
    SKIP = "skip"
    THRESHOLD_VENT = "threshold_vent"


class ScanType(enum.Enum):
    """Scan type."""

    NORMALDIXON = "normal"
    MEDIUMDIXON = "medium"
    FASTDIXON = "fast"


class Site(enum.Enum):
    """Site name."""

    DUKE = "duke"
    UVA = "uva"


class Platform(enum.Enum):
    """Scanner platform."""

    SIEMENS = "siemens"


class TrajType(object):
    """Trajectory type."""

    SPIRAL = "spiral"
    HALTON = "halton"
    HALTONSPIRAL = "haltonspiral"
    SPIRALRANDOM = "spiralrandom"
    ARCHIMEDIAN = "archimedian"
    GOLDENMEAN = "goldenmean"


class Orientation(object):
    """Image orientation."""

    CORONAL = "coronal"
    AXIAL = "axial"
    TRANSVERSE = "transverse"


class DCFSpace(object):
    """Defines the DCF space."""

    GRIDSPACE = "gridspace"
    DATASPACE = "dataspace"


class STATSIOFields(object):
    """Statistic IO Fields."""

    SUBJECT_ID = "subject_id"
    VEN_DEFECT = "ven_defect"
    VEN_LOW = "ven_low"
    VEN_HIGH = "ven_high"
    VEN_CV = "ven_cv"
    VEN_SKEW = "ven_skewness"
    VEN_SNR = "ven_snr"
    INFLATION = "inflation"
    VEN_MEDIAN = "ven_median"
    VEN_MEAN = "ven_mean"
    VEN_STD = "ven_std"
    SCAN_DATE = "scan_date"
    PROCESS_DATE = "process_date"


class VENHISTOGRAMFields(object):
    """Ventilation historam fields."""

    COLOR = (0.4196, 0.6824, 0.8392)
    XLIM = 1.0
    YLIM = 0.07
    NUMBINS = 50
    REFERENCE_FIT = (0.04462, 0.52, 0.2713)


class PDFOPTIONS(object):
    """PDF Options dict."""

    VEN_PDF_OPTIONS = {
        "page-width": 256,  # 320,
        "page-height": 160,  # 160,
        "margin-top": 1,
        "margin-right": 0.1,
        "margin-bottom": 0.1,
        "margin-left": 0.1,
        "dpi": 300,
        "encoding": "UTF-8",
        "enable-local-file-access": None,
    }


class REFERENCESTATS(object):
    """Reference statistics."""

    ref_stats_ven_gre_dict = {
        "r_ven_defect_ave": "2.6",
        "r_ven_defect_std": "1.8",
        "r_ven_low_ave": "17.5",
        "r_ven_low_std": "5.7",
        "r_ven_high_ave": "16.7",
        "r_ven_high_std": "3.3",
        "r_ven_skewness_ave": "0",
        "r_ven_skewness_std": "0.11",
        "r_ven_CV_ave": "0.37",
        "r_ven_CV_std": "0.04",
        "r_ven_tcv_ave": "3.8",
        "r_ven_tcv_std": "0.6",
    }

    REF_MEAN_VENT = 0.58
    REF_STD_VENT = 0.19
    REF_BINS_VEN_GRE = [
        REF_MEAN_VENT - 2 * REF_STD_VENT,
        REF_MEAN_VENT - REF_STD_VENT,
        REF_MEAN_VENT,
        REF_MEAN_VENT + REF_STD_VENT,
        REF_MEAN_VENT + 2 * REF_STD_VENT,
    ]


class NormalizationMethods(object):
    """Image normalization methods."""

    VANILLA = "vanilla"
    PERCENTILE = "percentile"


class BIN2COLORMAP(object):
    """Maps of binned values to color values."""

    VENT_BIN2COLOR_MAP = {
        1: [0, 0, 0],
        2: [1, 0, 0],
        3: [1, 0.7143, 0],
        4: [0.4, 0.7, 0.4],
        5: [0, 1, 0],
        6: [0, 0.57, 0.71],
        7: [0, 0, 1],
    }
