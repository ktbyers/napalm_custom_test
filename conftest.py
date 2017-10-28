from __future__ import print_function
from __future__ import unicode_literals

import os
import pytest
import io
import sys
import yaml
from napalm import get_network_driver

PWD = os.path.dirname(os.path.realpath(__file__))


def parse_yaml(yaml_file):
    """Read yaml file."""
    try:
        with io.open(yaml_file, encoding='utf-8') as fname:
            return yaml.load(fname)
    except IOError:
        sys.exit("Unable to open YAML file: {}".format(yaml_file))


def pytest_addoption(parser):
    """Add test_device option to py.test invocations."""
    parser.addoption("--test_device", action="store", dest="test_device", type=str,
                     help="Specify the platform type to test on")


# Fixtures
@pytest.fixture(scope="module")
def napalm_connect(request):
    def napalm_close():
        """Finalizer that will automatically close napalm conn when tests are done."""
        connection.close()
    device_under_test = request.config.getoption('test_device')
    test_devices = parse_yaml(PWD + "/test_devices.yml")
    device_def = test_devices[device_under_test]
    driver = get_network_driver(device_def.pop('device_type'))
    connection = driver(**device_def)

    request.addfinalizer(napalm_close)
    return connection
