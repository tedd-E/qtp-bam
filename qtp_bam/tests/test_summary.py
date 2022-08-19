# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import main
from tempfile import mkdtemp
from os import remove, environ
from os.path import exists, isdir
from shutil import rmtree
from json import dumps

from qiita_client.testing import PluginTestCase

from qtp_bam import generate_html_summary


class SummaryTestsWith(PluginTestCase):
    def setUp(self):
        self.out_dir = mkdtemp()
        self._clean_up_files = [self.out_dir]

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
        parameters = {'input_data': artifact}
        data = {'command': command,
                'parameters': dumps(parameters),
                'status': 'running'}
        res = self.qclient.post('/apitest/processing_job/', data=data)
        job_id = res['job']

        return job_id, parameters

    def test_generate_html_summary(self):
        # test server
        artifact_id = 420
        command = dumps(['BAM type', '0.0.1 - bam', 'Generate HTML summary'])
        job_id, parameters = self._create_job(artifact_id, command)

        obs_success, obs_ainfo, obs_error = generate_html_summary(
            self.qclient, job_id, parameters, self.out_dir)

        # asserting reply
        self.assertTrue(obs_success)
        self.assertIsNone(obs_ainfo)
        self.assertEqual(obs_error, "")

        # asserting content of html
        res = self.qclient.get("/qiita_db/artifacts/%s/" % artifact_id)
        html_fp = res['files']['html_summary'][0]
        self._clean_up_files.append(html_fp)

        with open(html_fp) as html_f:
            html = html_f.read()
        self.assertEqual(html, '\n'.join(EXP_HTML))

    # TODO: Write any other tests needed to get your coverage as close as
    # possible to 100%!!

# NOTE: might have to change this to html format (see qtp-sequencing)
EXP_HTML = "416648 + 0 in total (QC-passed reads + QC-failed reads)\n \
0 + 0 secondary\n\
250 + 0 supplementary\n\
0 + 0 duplicates\n\
416648 + 0 mapped (100.00% : N/A)\n\
416398 + 0 paired in sequencing\n\
209686 + 0 read1\n\
206712 + 0 read2\n\
384858 + 0 properly paired (92.43% : N/A)\n\
415559 + 0 with itself and mate mapped\n\
839 + 0 singletons (0.20% : N/A)\n\
0 + 0 with mate mapped to a different chr\n\
0 + 0 with mate mapped to a different chr (mapQ>=5)"

if __name__ == '__main__':
    main()
