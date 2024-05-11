# Copyright 2022 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This software is provided as-is,
# without warranty or representation for any use or purpose.
# Your use of it is subject to your agreement with Google.

from airflow import models
from airflow.providers.google.cloud.operators.dataflow import (
    DataflowStartFlexTemplateOperator,)
from airflow.utils.dates import days_ago

GCS_TEMPLATE_PATH = models.Variable.get("GCS_TEMPLATE_PATH")
INPUT_DATA_PATH = models.Variable.get("INPUT_DATA_PATH")
PROJECT_ID = models.Variable.get("PROJECT_ID")
DATASET_ID = models.Variable.get("DATASET_ID")
SDK_DOCKER_IMAGE = models.Variable.get("SDK_DOCKER_IMAGE")
DF_WORKER_SA = models.Variable.get("DF_WORKER_SA")
TEMP_LOCATION = models.Variable.get("TEMP_LOCATION")
STAGING_LOCATION = models.Variable.get("STAGING_LOCATION")
NETWORK = models.Variable.get("NETWORK")
SUBNET = models.Variable.get("SUBNET")
JOB_LOCATION = models.Variable.get("JOB_LOCATION")
JOB_NAME = "bq-to-xml-sample-job"
PIPELINE_NAME = "bq_to_xml_sample_dag"

PAYLOAD = {
    "launchParameter": {
        "containerSpecGcsPath": GCS_TEMPLATE_PATH,
        "jobName": JOB_NAME,
        "parameters": {
            "input": INPUT_DATA_PATH,
            "output": f"{PROJECT_ID}:{DATASET_ID}",
            "sdk_container_image": SDK_DOCKER_IMAGE,
            "sdk_location": "container",
        },
        "environment": {
            "serviceAccountEmail":
                DF_WORKER_SA,
            "tempLocation":
                TEMP_LOCATION,
            "stagingLocation":
                STAGING_LOCATION,
            "network":
                NETWORK,
            "subnetwork":
                SUBNET,
            "ipConfiguration":
                "WORKER_IP_PRIVATE",
            "workerRegion":
                JOB_LOCATION,
            "additionalExperiments": [
                "use_runner_v2",
                "use_network_tags_for_flex_templates=dataflow-worker",
                "use_network_tags=dataflow-worker",
            ],
        },
    }
}

## DAG_CONFIG
default_args = {"start_date": days_ago(1), "retries": 1}

with models.DAG(
        PIPELINE_NAME,
        default_args=default_args,
        schedule_interval="@once",
) as dag:

    start_flex_template = DataflowStartFlexTemplateOperator(
        task_id="bq_to_xml_sample_df_job",
        project_id=PROJECT_ID,
        location=JOB_LOCATION,
        body=PAYLOAD,
    )

    start_flex_template
