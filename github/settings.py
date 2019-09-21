# -*- coding: utf-8 -*-
import os

DATA_SAMPLE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasample'))
DATA_SAMPLE_ZIP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasample.zip'))

# please change the path to your real store path
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'datasample'))

UI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ui'))

LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))

# ChromeDriver 75.0.3770.140
CHROME_DRIVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'binary', 'chromedriver'))

if not DATA_PATH:
    DATA_PATH = os.environ.get('GITHUB_DATA_PATH')

if not LOG_PATH:
    LOG_PATH = os.environ.get('LOG_PATH')

HTTP_PROXY = 'http://127.0.0.1:10080'
if not HTTP_PROXY:
    HTTP_PROXY = os.environ.get('HTTP_PROXY')

HTTPS_PROXY = 'http://127.0.0.1:10080'
if not HTTPS_PROXY:
    HTTPS_PROXY = os.environ.get('HTTPS_PROXY')
