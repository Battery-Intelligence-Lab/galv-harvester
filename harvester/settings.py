# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import json
import os
import pathlib
import logging
import logging.handlers

VERSION = '0.1.0'

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s [%(name)s:%(lineno)d]',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_logfile() -> pathlib.Path:
    return pathlib.Path(os.getenv('LOG_FILE', "/harvester_files/harvester.log"))


def get_logger(name):
    logger = logging.getLogger(name)
    # stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setLevel(logging.INFO)
    # logger.addHandler(stream_handler)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s [%(name)s]', datefmt='%Y-%m-%d %H:%M:%S')
    os.makedirs(get_logfile().parent, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(get_logfile(), maxBytes=5_000_000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = get_logger(__file__)


def get_settings_file() -> pathlib.Path:
    return pathlib.Path(os.getenv('SETTINGS_FILE', "/harvester_files/.harvester.json"))


def get_settings():
    try:
        with open(get_settings_file(), 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding json file {f.name}", e)
                f.seek(0)
                logger.error(f.readlines())
    except FileNotFoundError:
        logger.error(f'No config file at {get_settings_file()}')
    return None


def get_setting(*args):
    settings = get_settings()
    if not settings:
        if len(args) == 1:
            return None
        return [None for _ in args]
    if len(args) == 1:
        return settings.get(args[0])
    return [settings.get(arg) for arg in args]


def get_standard_units():
    return {u['name']: u['id'] for u in get_setting('standard_units')}


def get_standard_columns():
    return {u['name']: u['id'] for u in get_setting('standard_columns')}


def update_envvars():
    envvars = get_setting('environment_variables') or {}
    for k, v in envvars.items():
        old = os.getenv(k)
        os.environ[k] = v
        if old != v:
            logger.info(f"Update envvar {k} from '{old}' to '{v}'")
    delvars = get_setting('deleted_environment_variables') or {}
    for k in delvars:
        old = os.getenv(k)
        if old is not None:
            logger.info(f"Unsetting envvar {k} (previous value: {old})")
        os.unsetenv(k)

# These definitions should be kept in sync with the definitions in the backend
HARVESTER_TASK_FILE_SIZE = 'file_size'
HARVESTER_TASK_IMPORT = 'import'
HARVESTER_STATUS_SUCCESS = 'success'
HARVESTER_STATUS_ERROR = 'error'
HARVEST_STAGE_FILE_METADATA = 'file metadata'
HARVEST_STAGE_DATA_SUMMARY = 'data summary'
HARVEST_STAGE_UPLOAD_PARQUET = 'upload parquet partitions'
HARVEST_STAGE_UPLOAD_COMPLETE = 'upload complete'
HARVEST_STAGE_COMPLETE = 'harvest complete'
HARVEST_STAGE_FAILED = 'harvest failed'