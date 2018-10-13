#!/bin/sh

RETURN_CODE=0

echo "Starting Test" \
&& py.test -s -v test_napalm_nxos.py --test_device nxos \
&& py.test -s -v test_napalm_nxos.py --test_device nxos_ssh \
&& echo "Merge from direct config (not from file)" \
&& py.test -s -v test_napalm_cfg.py::test_merge_inline_commit_config --test_device nxos \
&& py.test -s -v test_napalm_cfg.py::test_merge_inline_commit_config --test_device nxos_ssh \
&& echo "Merge from direct config with errors in cfg" \
&& py.test -s -v test_napalm_cfg.py::test_merge_failure --test_device nxos \
&& py.test -s -v test_napalm_cfg.py::test_merge_failure --test_device nxos_ssh \
&& echo "Replace and Commit" \
&& py.test -s -v test_napalm_cfg.py::test_replace_commit_config --test_device nxos \
&& py.test -s -v test_napalm_cfg.py::test_replace_commit_config --test_device nxos_ssh \
&& echo "Compare Config" \
&& py.test -s -v test_napalm_cfg.py::test_compare_config --test_device nxos \
&& py.test -s -v test_napalm_cfg.py::test_compare_config --test_device nxos_ssh \
&& echo "Rollback" \
&& py.test -s -v test_napalm_cfg.py::test_rollback --test_device nxos \
&& py.test -s -v test_napalm_cfg.py::test_rollback --test_device nxos_ssh \
&& echo "Discard Config" \
&& py.test -s -v test_napalm_cfg.py::test_discard_config --test_device nxos \
&& py.test -s -v test_napalm_cfg.py::test_discard_config --test_device nxos_ssh \
&& echo \
\
|| RETURN_CODE=1
 
exit $RETURN_CODE
