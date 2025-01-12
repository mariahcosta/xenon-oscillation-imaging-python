"""Scripts to run oscillation mapping pipeline in batches."""
import glob
import importlib
import logging
import os
import pdb

from absl import app, flags

from main import oscillation_mapping_readin, oscillation_mapping_reconstruction

FLAGS = flags.FLAGS

flags.DEFINE_string("cohort", "healthy", "cohort folder name in config folder")

CONFIG_PATH = "config/"


def main(argv):
    """Run the oscillation imaging pipeline in multiple subjects.

    Import the config file and run the oscillation imaging pipeline on all
    subjects specified in by the cohort flag.
    """
    if FLAGS.cohort == "healthy":
        subjects = glob.glob(os.path.join(CONFIG_PATH, "healthy", "*py"))
    elif FLAGS.cohort == "cteph":
        subjects = glob.glob(os.path.join(CONFIG_PATH, "cteph", "*py"))
    elif FLAGS.cohort == "ild":
        subjects = glob.glob(os.path.join(CONFIG_PATH, "ild", "*py"))
    elif FLAGS.cohort == "tyvaso":
        subjects = glob.glob(os.path.join(CONFIG_PATH, "tyvaso", "*py"))
    elif FLAGS.cohort == "jupiter":
        subjects = glob.glob(os.path.join(CONFIG_PATH, "jupiter", "*py"))
    elif FLAGS.cohort == "all":
        subjects = glob.glob(os.path.join(CONFIG_PATH, "healthy", "*py"))
        subjects += glob.glob(os.path.join(CONFIG_PATH, "cteph", "*py"))
        subjects += glob.glob(os.path.join(CONFIG_PATH, "ild", "*py"))
        subjects += glob.glob(os.path.join(CONFIG_PATH, "tyvaso", "*py"))
    elif "-" in FLAGS.cohort:
        cohorts = FLAGS.cohort.split("-")
        subjects = []
        for cohort in cohorts:
            if cohort == "healthy":
                subjects += glob.glob(os.path.join(CONFIG_PATH, "healthy", "*py"))
            elif cohort == "cteph":
                subjects += glob.glob(os.path.join(CONFIG_PATH, "cteph", "*py"))
            elif cohort == "ild":
                subjects += glob.glob(os.path.join(CONFIG_PATH, "ild", "*py"))
            elif cohort == "tyvaso":
                subjects += glob.glob(os.path.join(CONFIG_PATH, "tyvaso", "*py"))
            else:
                raise ValueError("Invalid cohort name")
    else:
        raise ValueError("Invalid cohort name")

    for subject in subjects:
        try:
            config_obj = importlib.import_module(
                name=subject[:-3].replace("/", "."), package=None
            )
            config = config_obj.get_config()
            logging.info("Processing subject: %s", config.subject_id)
            if FLAGS.force_recon:
                oscillation_mapping_reconstruction(config)
            elif FLAGS.force_readin:
                oscillation_mapping_readin(config)
            elif config.processes.oscillation_mapping_reconstruction:
                oscillation_mapping_reconstruction(config)
            elif config.processes.oscillation_mapping_readin:
                oscillation_mapping_readin(config)
            else:
                pass
        except:
            logging.warning("Failed to process subject: %s", subject)


if __name__ == "__main__":
    app.run(main)
