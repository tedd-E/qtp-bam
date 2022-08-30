# -----------------------------------------------------------------------------
# Copyright (c) 2022, Qiita development team.
#
# Distributed under the terms of the Apache Software License 2.0 License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from qiita_client import QiitaTypePlugin, QiitaArtifactType

from .validate import validate
from .summary import generate_html_summary

# Define the supported artifact types
# Here is an example on how to create a type
# artifact_types = [
#     QiitaArtifactType('BIOM', 'BIOM table', False, False,
#                       [('biom', True), ('directory', False), ('log', False),
#                        ('preprocessed_fasta', False)])]
# Below is the API of the QiitaArtifactType class:
# QiitaArtifactType(TYPE_NAME, TYPE_DESCRIPTION, CAN_BE_SUBMITED_TO_EBI,
#                   CAN_BE_SUBMITED_TO_VAMPS, LIST_OF_ACCEPTED_FILEPATH_TYPES)
# Where the list of accepted filepaths is a list of 2-tuples in which the
# first element of the tuple is the filepath type and the seconf element
# is a boolean indicating if the filepath type is required to successfully
# create an artifact of the given type

# NOTE FROM NIEMA: The example above seems to be out of date:
#                  it doesn't match the current BIOM example https://github.com/qiita-spots/qtp-biom/blob/731b5529fc5f559a868c1d3a6e14cecf4e59198b/qtp_biom/__init__.py#L16-L19
#                  because it's missing the IS_USER_UPLOADABLE boolean https://github.com/qiita-spots/qiita_client/blob/0e04e78578c8924f65e12ef6813ebadd2886c5e9/qiita_client/plugin.py#L126-L128

# Initialize the plugin

# NOTE: may have to revisit LIST_OF_ACCEPTED_FILEPATH_TYPE
artifact_types = [
    QiitaArtifactType('BAM', 'BAM file', False, False, True, [('tgz', True), ('directory', False), ('log', False)])
]

plugin = QiitaTypePlugin('BAM type', '0.0.1 - bam',
                         'Qiita Type Plugin: BAM',
                         validate, generate_html_summary,
                         artifact_types)
