#!/bin/sh

RETURN_CODE=0
PYTEST="/home/kbyers/VENV/napalm_auto_test/bin/py.test"

# Exit on the first test failure and set RETURN_CODE = 1
echo "Starting tests...good luck:" \
&& echo "---- discard_config ----" \
&& echo "Cisco IOS" \
&& $PYTEST -s -v test_napalm_cfg.py::test_rollback --test_device ios \
&& echo "Cisco NX-OS (API)" \
&& $PYTEST -s -v test_napalm_cfg.py::test_rollback --test_device nxos \
&& echo "Cisco NX-OS (SSH)" \
&& $PYTEST -s -v test_napalm_cfg.py::test_rollback --test_device nxos_ssh \
&& echo "Arista" \
&& $PYTEST -s -v test_napalm_cfg.py::test_rollback --test_device eos \
&& echo "Juniper" \
&& $PYTEST -s -v test_napalm_cfg.py::test_rollback --test_device junos \
&& echo \
\
|| RETURN_CODE=1

exit $RETURN_CODE
