#!/bin/sh

RETURN_CODE=0
PYTEST="/home/kbyers/VENV/napalm_auto_test/bin/py.test"

# Exit on the first test failure and set RETURN_CODE = 1
echo "Starting tests...good luck:" \
&& echo \
&& echo "---- replace_commit_config ----" \
&& echo "Cisco IOS" \
&& $PYTEST -s -v test_napalm_cfg.py::test_replace_commit_config --test_device ios \
&& $PYTEST -s -v test_napalm_cfg.py::test_commit_config_hostname --test_device ios \
&& echo "Cisco NX-OS (API)" \
&& $PYTEST -s -v test_napalm_cfg.py::test_replace_commit_config --test_device nxos \
&& $PYTEST -s -v test_napalm_cfg.py::test_commit_config_hostname --test_device nxos \
&& echo "Cisco NX-OS (SSH)" \
&& $PYTEST -s -v test_napalm_cfg.py::test_replace_commit_config --test_device nxos_ssh \
&& $PYTEST -s -v test_napalm_cfg.py::test_commit_config_hostname --test_device nxos_ssh \
&& echo "Arista" \
&& $PYTEST -s -v test_napalm_cfg.py::test_replace_commit_config --test_device eos \
&& echo "Juniper" \
&& $PYTEST -s -v test_napalm_cfg.py::test_replace_commit_config --test_device junos \
&& echo \
\
|| RETURN_CODE=1

exit $RETURN_CODE
