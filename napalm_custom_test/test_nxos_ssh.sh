RETURN_CODE=0
py.test -s -v test_napalm_cfg.py::test_compare_config --test_device nxos_ssh \
&& py.test -s -v test_napalm_cfg.py::test_compare_config_inline --test_device nxos_ssh \
&& py.test -s -v test_napalm_cfg.py::test_discard_config --test_device nxos_ssh \
&& py.test -s -v test_napalm_cfg.py::test_merge_inline_commit_config --test_device nxos_ssh \
&& py.test -s -v test_napalm_cfg.py::test_commit_config_hostname_merge --test_device nxos_ssh \
&& py.test -s -v test_napalm_cfg.py::test_replace_commit_config --test_device nxos_ssh \
&& py.test -s -v test_napalm_cfg.py::test_commit_config_hostname --test_device nxos_ssh \
&& py.test -s -v test_napalm_cfg.py::test_rollback --test_device nxos_ssh \
|| RETURN_CODE=1

exit $RETURN_CODE
