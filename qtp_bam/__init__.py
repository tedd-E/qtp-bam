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
artifact_types = [
    QiitaArtifactType(
        "BAM", "BAM file", False, False, True,
        [("bam", True), ("directory", False)]
    )
]

# Initialize the plugin
plugin = QiitaTypePlugin(
    "BAM type",
    "0.0.1",
    "Qiita Type Plugin: BAM",
    validate,
    generate_html_summary,
    artifact_types,
)
