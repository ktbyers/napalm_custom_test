from __future__ import print_function
from __future__ import unicode_literals

import os
import pytest
import io
import sys
import yaml

# from incendio import get_network_driver
from napalm import get_network_driver

PWD = os.path.dirname(os.path.realpath(__file__))


def parse_yaml(yaml_file):
    """Read yaml file."""
    try:
        with io.open(yaml_file, encoding="utf-8") as fname:
            return yaml.safe_load(fname)
    except IOError:
        sys.exit("Unable to open YAML file: {}".format(yaml_file))


def pytest_addoption(parser):
    """Add test_device option to py.test invocations."""
    parser.addoption(
        "--test_device",
        action="store",
        dest="test_device",
        type=str,
        help="Specify the platform type to test on",
    )


# Fixtures
@pytest.fixture(scope="module")
def napalm_connect(request):
    def napalm_close():
        """Finalizer that will automatically close napalm conn when tests are done."""
        connection.close()

    device_under_test = request.config.getoption("test_device")
    test_devices = parse_yaml(PWD + "/test_devices.yml")
    device_def = test_devices[device_under_test]
    driver = get_network_driver(device_def.pop("device_type"))
    connection = driver(**device_def)
    connection.open()

    request.addfinalizer(napalm_close)
    return connection


# Resets initial state on every test
@pytest.fixture
def napalm_config(request):
    def napalm_close():
        """Finalizer that will automatically close napalm conn when tests are done."""
        connection.close()

    device_under_test = request.config.getoption("test_device")
    test_devices = parse_yaml(PWD + "/test_devices.yml")
    device_def = test_devices[device_under_test]
    platform = device_def.pop("device_type")
    optional_args = device_def.get("optional_args", {})
    config_encoding = optional_args.get("config_encoding", "cli")
    driver = get_network_driver(platform)
    connection = driver(**device_def)
    connection.open()

    # Workaround to test different juniper devices
    if device_under_test == "vmx1":
        connection._platform_host = "vmx1"
    else:
        connection._platform_host = None
    connection._platform = platform

    # Stage a known initial configuration
    if config_encoding == "xml":
        filename = "CFGS/{}/initial_config.xml".format(connection._platform)
    else:
        if connection._platform_host:
            filename = "CFGS/{}/initial_config.txt".format(connection._platform_host)
        else:
            filename = "CFGS/{}/initial_config.txt".format(connection._platform)

    print("Loading initial configuration.")
    connection.load_replace_candidate(filename=filename)
    if connection.compare_config():
        connection.commit_config()

    request.addfinalizer(napalm_close)
    return connection
