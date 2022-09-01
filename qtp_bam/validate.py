# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
import os
import shutil
from json import loads
from os.path import join, basename
import gzip
import pysam
from qiita_client import ArtifactInfo


def validate(qclient, job_id, parameters, out_dir):
    """Validate and fix a new artifact

    Parameters
    ----------
    qclient : qiita_client.QiitaClient
        The Qiita server client
    job_id : str
        The job id
    parameters : dict
        The parameter values to validate and create the artifact
    out_dir : str
        The path to the job's output directory

    Returns
    -------
    bool, list of qiita_client.ArtifactInfo, str
        Whether the job is successful
        The artifact information, if successful
        The error message, if not successful
    """

    # Step 1: Gather information from Qiita
    qclient.update_job_step(job_id, "Step 1: Collecting information")

    files = loads(
        parameters["files"])
    a_type = parameters["artifact_type"]

    if a_type.upper() != "BAM":
        return False, None, \
               f'Unknown artifact type {a_type}. Supported types: BAM'

    # unzip bam.gz files
    for bamfile in files["bam"]:
        if bamfile.endswith(".gz"):
            bamfilepath = os.path.abspath(files["bam"] + bamfile)
            with gzip.open(bamfilepath, "rb") as f_in, open(
                    bamfilepath.rsplit(".", 1)[0], "wb"
            ) as f_out:
                shutil.copyfileobj(f_in, f_out)

    # check for valid bam/bai pair (assumes bai is in 'bam' folder)
    for bamfile in files["bam"]:
        if bamfile.endswith(".bam") and bamfile + ".bai" not in files["bam"]:
            try:
                pysam.index(bamfile)
            except pysam.SamToolsError as e:
                return False, None, \
                       f"Unable to generate bai file for bam file {bamfile}.\n\
                        Error output: {e}"
            except Exception as e:
                return False, None, str(e)

    qclient.update_job_step(job_id, "Step 2: Validating files")

    for bamfile in files["bam"]:
        if not bamfile.endswith(".gz"):
            try:
                pysam.quickcheck(bamfile)
            except pysam.SamToolsError as e:
                return (
                    False,
                    None,
                    f'Error: {bamfile} failed sanity check. Error output: {e}'
                    f'\nVerify file is formatted properly'
                )
            except Exception as e:
                return False, None, str(e)

    filepaths = []
    new_bam_fp = join(out_dir, basename(files["bam"][0]))
    filepaths.append((new_bam_fp, "bam"))

    return True, [ArtifactInfo(None, a_type, filepaths)], ""
