# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from json import loads

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
    prep_id = parameters['template']    # An integer with the prep information id
    analysis_id = parameters['analysis']   # ??? lol
    files = loads(parameters['files'])  # A dictionary of the format {str:filepath-type: list:filepaths}
    a_type = parameters['artifact_type']    # str:artifact-type
    prep_info = qclient.get("/qiita_db/prep_template/%s/data/" % prep_id)['data']   # metadata in biom

    if a_type.upper() != "BAM":
        return False, None, "Unknown artifact type %s. Supported types: BAM" % a_type

    # check for valid bam/bai pair
    if files


    qclient.update_job_step(job_id, "Step 2: Validating files")
    # TODO: Validate if the files provided by Qiita generate a valid artifact of type "a_type"

    # NOTE: if filepath doesn't actually point to a file thats gonna be problems
    for _, filepath in files:
        samfile = pysam.Samfile(filepath)







    # skip this part for now v
    # qclient.update_job_step(job_id, "Step 3: Fixing files")
    # TODO: If the files are not creating a valid artifact but they can be corrected, correct them here

    # TODO: fill filepaths with a list of tuples with (filepath, filepath type)
    filepaths = []
    return True, [ArtifactInfo(None, a_type, filepaths)], ""
