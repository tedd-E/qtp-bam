# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from base64 import b64encode
from io import BytesIO

import pysam
import pysamstats
import matplotlib.pyplot as plt
from os.path import join


def generate_html_summary(qclient, job_id, parameters, out_dir):
    """Generates the HTML summary of an artifact

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
    bool, None, str
        Whether the job is successful
        Ignored
        The error message, if not successful
    """
    # Step 1: gather file information from qiita using REST api
    qclient.update_job_step(job_id, "Step 1: Gathering information from Qiita")
    # This is the only parameter provided by Qiita: the artifact id. From here,
    # the developer should be able to retrieve any further information needed
    # to generate the HTML summary
    artifact_id = parameters['input_data']
    qclient_url = "/qiita_db/artifacts/%s/" % artifact_id
    artifact_info = qclient.get(qclient_url)
    artifact_files = artifact_info['files']    # Get the artifact files

    # Step 2: generate HTML summary
    qclient.update_job_step(job_id, "Step 2: Generating HTML summary")
    # commands in pysam equivalent to:
    # samtools stats <file.bam> | grep "is sorted:"
    # samtools flagstat test.bam (gets summary)

    # NOTE: for now, assumes bam
    artifact_information = "--BAM SUMMARY,--"
    for bamfile in artifact_files['files']['bam']:
        artifact_information += '\n' + str(pysam.flagstat(bamfile))

    # Work on this part if we have time to make visualization for the summary
    # code from https://pypi.org/project/pysamstats/0.14/
    # mybam = pysam.Samfile(artifact_files[0])
    # a = pysamstats.load_coverage(mybam, chrom='Pf3D7_01_v3', start=10000, end=20000)
    # plt.plot(a.pos, a.reads_all)
    # plot = BytesIO()
    # plt.savefig(plot, format='png')
    # artifact_information = [(
    #     '<img src = "data:image/png;base64,{}"/>'.format(
    #         b64encode(plot.getvalue()).decode('utf-8')))]

    of_fp = join(out_dir, "artifact_%d.html" % artifact_id)
    with open(of_fp, "w") as summaryfile:
        summaryfile.write(artifact_information)
    html_summary_fp = join(out_dir, "summary.html")

    # Step 3: add the new file to the artifact using REST api
    qclient.update_job_step(job_id, "Step 3: Transferring summary to Qiita")
    success = True
    error_msg = ""
    try:
        qclient.patch(qclient_url, 'add', '/html_summary/',
                      value=html_summary_fp)
    except Exception as e:
        success = False
        error_msg = str(e)

    return success, None, error_msg
