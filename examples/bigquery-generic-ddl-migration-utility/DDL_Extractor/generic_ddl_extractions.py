# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module to drive the generic metadata utility"""
from google.cloud import secretmanager
import json
import argparse
from netezza_metadata_extraction import NetezzaMetastoreModule
from vertica_metadata_extraction import VerticaMetastoreModule
from mssql_metadata_extraction import MssqlMetastoreModule
from oracle_metadata_extraction import OracleMetastoreModule
from snowflake_metadata_extraction import SnowflakeMetastoreModule
from utils.setup_logger import logger


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dbtype", help="database type (vertica, netezza, mysql)", required=True
    )

    parser.add_argument(
        "--secret_name", help="Secret name", required=True
    )

    parser.add_argument("--gcs_config_path", help="output bucket name", required=True)

    parser.add_argument(
        "--project_id", help="Project_Id", required=True
    )

    args = parser.parse_args()

    try:
        secret_resource_id = f"projects/{args.project_id}/secrets/{args.secret_name}/versions/latest"
        client_secret = secretmanager.SecretManagerServiceClient()
        response = client_secret.access_secret_version(name=secret_resource_id)
        secret_val = response.payload.data.decode('UTF-8')
        credentials = json.loads(secret_val)
        username = credentials['user']
        password = credentials['password']
        if args.dbtype == "vertica":
            host = credentials['host']
            port = credentials['port']
            dbname = credentials['database']
            vertica_module = VerticaMetastoreModule(
                username, password, host, port, dbname, args.gcs_config_path, args.project_id
            )
            vertica_module.vertica_metastore_discovery()
        elif args.dbtype == "netezza":
            host = credentials['host']
            port = credentials['port']
            dbname = credentials['database']            
            netezza_module = NetezzaMetastoreModule(
                username, password, host, port, dbname, args.gcs_config_path, args.project_id
            )
            netezza_module.netezza_metastore_discovery()
        elif args.dbtype == "mssql":
            host = credentials['host']
            port = credentials['port']
            dbname = credentials['database']            
            mssql_module = MssqlMetastoreModule(
                username, password, host, port, dbname, args.gcs_config_path, args.project_id
            )
            mssql_module.mssql_metastore_discovery()
        elif args.dbtype == "oracle":
            host = credentials['host']
            port = credentials['port']
            dbname = credentials['database']            
            instant_client_path = credentials['instant_client_path']
            oracle_module = OracleMetastoreModule(
                username, password, host, port, dbname, args.gcs_config_path, args.project_id, instant_client_path
            )
            oracle_module.oracle_metastore_discovery()
        elif args.dbtype == "snowflake":
            account = credentials['account']
            warehouse = credentials['warehouse']
            dbname = credentials['database']            
            schema=credentials['schema']
            snowflake_module = SnowflakeMetastoreModule(
                username, password, account, warehouse, dbname, schema, args.gcs_config_path, args.project_id
            )
            snowflake_module.snowflake_metastore_discovery()
    except Exception as error:
        logger.error(f"Error when retreiving secret credentials/Incorrect option : {error}")

