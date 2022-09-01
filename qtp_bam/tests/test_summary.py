# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from functools import partial
from unittest import main
from tempfile import mkdtemp
from os import remove
from os.path import exists, isdir, join, dirname
from shutil import rmtree
from json import dumps

from qiita_client.testing import PluginTestCase

from qtp_bam.summary import generate_local_summary


class SummaryTestsWith(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        self._clean_up_files = [self.out_dir]

        path_builder = partial(join, dirname(__file__), 'test_data')
        self.bamfile = path_builder('file.bam')

    def tearDown(self):
        for fp in self._clean_up_files:
            if exists(fp):
                if isdir(fp):
                    rmtree(fp)
                else:
                    remove(fp)

    def _create_job(self, artifact, command):
        """Creates a new job in Qiita so we can update its step during tests

        Parameters
        ----------
        artifact: int
            The artifact id to be validated during tests
        command: str (NOTE: changed from int)
            Qiita's command id for the 'Generate HTML summary' operation

        Returns
        -------
        str, dict
            The job id and the parameters dictionary
        """
        # Create a new job
        parameters = {"input_data": artifact}
        data = {
            "command": command,
            "parameters": dumps(parameters),
            "status": "running",
        }
        res = self.qclient.post("/apitest/processing_job/", data=data)
        job_id = res["job"]

        return job_id, parameters

    def test_generate_html_summary(self):
        # test server
        artifact_id = 9
        obs_success, obs_ainfo, obs_error = generate_local_summary(
            {'bam': [self.bamfile]}, self.out_dir, artifact_id
        )

        # asserting reply
        self.assertTrue(obs_success)
        self.assertIsNone(obs_ainfo)
        self.assertEqual(obs_error, "")

        # asserting content of html
        html_fp = join(self.out_dir, f'artifact_{artifact_id}')
        self._clean_up_files.append(html_fp)

        with open(html_fp) as html_f:
            html = html_f.read()

        self.assertEqual(html, EXP_HTML)


EXP_HTML = "--BAM SUMMARY--\n\
416648 + 0 in total (QC-passed reads + QC-failed reads)\n\
416398 + 0 primary\n\
0 + 0 secondary\n\
250 + 0 supplementary\n\
0 + 0 duplicates\n\
0 + 0 primary duplicates\n\
416648 + 0 mapped (100.00% : N/A)\n\
416398 + 0 primary mapped (100.00% : N/A)\n\
416398 + 0 paired in sequencing\n\
209686 + 0 read1\n\
206712 + 0 read2\n\
384858 + 0 properly paired (92.43% : N/A)\n\
415559 + 0 with itself and mate mapped\n\
839 + 0 singletons (0.20% : N/A)\n\
0 + 0 with mate mapped to a different chr\n\
0 + 0 with mate mapped to a different chr (mapQ>=5)\n"

if __name__ == "__main__":
    main()
