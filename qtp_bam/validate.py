# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from json import loads
from os.path import join, basename

import pysam
from qiita_client import ArtifactInfo

"""
def validate(qclient, job_id, parameters, out_dir)

qclient = qiita client instance (use for getting "res" (see biom test_validate line 52?)
job id = string (not important)
parameters = {'template': 1,
              'files': dumps(filepaths),
              'artifact_type': 'BIOM',
              'analysis': 1}
out_dir = mkdtemp()   (outputs files to a temp dir) 

NOTE that dumps(filepaths) is the JSON string format of filepaths, where...
filepaths = {'biom': [join(fp_support_files, 'sepp.biom')],
                     'preprocessed_fasta': [join(fp_support_files, 'sepp.fa')],
                     'plain_text': [join(fp_support_files, 'sepp.tre')]}
aka 
    filepaths = {
                'biom': [fp_support_files/sepp.biom],
                 'preprocessed_fasta': [fp_support_files/sepp.fa')],
                 'plan_text': [join(fp_support_files/sepp.tre')]
                 }
such that...
parameters = {'template': 1,
              'files': {'biom': [join(fp_support_files, 'sepp.biom')],
                     'preprocessed_fasta': [join(fp_support_files, 'sepp.fa')],
                     'plain_text': [join(fp_support_files, 'sepp.tre')]},
              'artifact_type': 'BIOM',
              'analysis': 1}
"""
# can ignore qclient, seems to just log the current step
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
    # These are the 3 parameters provided by Qiita:
    # - prep_id: An integer with the prep information id
    # - files: A dictionary of the format {str: list of str}, in which keys
    #          are the filepath type and values a list of filepaths
    # - a_type: A string with the artifact type to be validated
    # From here, the developer should be able to gather any further information
    # needed to validate the files

    # You may/may not need the prep information contents. If you need it,
    # uncomment the line below. Prep info is a dictionary with the following
    # format: {sample_id: {column_name: column_value}}
    # prep_info = qclient.get("/qiita_db/prep_template/%s/data/" % prep_id)['data']

    # Step 1: Gather information from Qiita

    qclient.update_job_step(job_id, "Step 1: Collecting information")
    prep_id = parameters['template']    # prep information id (integer)
    analysis_id = parameters['analysis']   # also an int (not important)
    files = loads(parameters['files'])  # dictionary {str:filepath-type: list:filepaths}
    a_type = parameters['artifact_type']    # str:artifact-type

    # don't know if need yet:
    prep_info = qclient.get("/qiita_db/prep_template/%s/data/" % prep_id)['data']   # metadata in bam

    if a_type.upper() != "BAM":
        return False, None, "Unknown artifact type %s. Supported types: BAM" % a_type

    # check for valid bam/bai pair (assumes bai is in 'bam' folder), generate if missing .bai
    for bamfile in files['bam']:
        if bamfile[-4:] == '.bam' and bamfile+'.bai' not in files['bam']:
            try:
                pysam.index(bamfile)
            except Exception:
                return False, None, "Unable to generate bai file for bam file %s" % bamfile


    qclient.update_job_step(job_id, "Step 2: Validating files")
    # Validate if the files provided by Qiita generate a valid artifact of type "a_type"
    # ACTUAL COMMAND: samtools quickcheck *.bam && echo 'all ok' || echo 'fail'
    # TODO: check exception catches
    for bamfile in files['bam']:
        try:
            pysam.quickcheck(bamfile)
        except Exception:
            return False, None, "Error: %s failed sanity check. Verify file is formatted properly" % bamfile

    # alternative version of above for loop?
    # try:
    #     pysam.quickcheck(join(basename(files['bam'][0]), "*.bam"))
    # except Exception:
    #     return False, None, "Error: a file failed sanity check. Verify file is formatted properly"
    #

    # NOTE: im skipping this part for now (low priority)
    # qclient.update_job_step(job_id, "Step 3: Fixing files")
    # TODO: If the files are not creating a valid artifact but they can be corrected, correct them here

    # fill filepaths with a list of tuples with (filepath, filepath type)
    filepaths = []
    new_bam_fp = join(out_dir, basename(files['bam'][0]))

    filepaths.append((new_bam_fp, 'bam'))

    return True, [ArtifactInfo(None, a_type, filepaths)], ""
