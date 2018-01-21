#!/bin/sh

RETURN_CODE=0
PYTEST="/home/gituser/VENV/napalm_auto_test/bin/py.test"

# Exit on the first test failure and set RETURN_CODE = 1
echo "Starting tests...good luck:" \
&& echo \
&& echo "---- Commit Confirm Methods ----" \
&& echo "Cisco IOS" \
&& $PYTEST -s -v test_napalm_cfg.py::test_commit_confirm --test_device ios
&& $PYTEST -s -v test_napalm_cfg.py::test_commit_confirm_noconfirm --test_device ios
&& $PYTEST -s -v test_napalm_cfg.py::test_commit_confirm_revert --test_device ios
\
|| RETURN_CODE=1

exit $RETURN_CODE
