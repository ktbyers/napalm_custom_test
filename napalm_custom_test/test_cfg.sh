#!/bin/sh

RETURN_CODE=0

# Exit on the first test failure and set RETURN_CODE = 1
echo "Starting tests...good luck:" \
&& echo "Cisco IOS" \
&& py.test -s -v test_napalm_cfg.py --test_device ios \
&& echo "Cisco NX-OS (API)" \
&& py.test -s -v test_napalm_cfg.py --test_device nxos \
&& echo "Cisco NX-OS (SSH)" \
&& py.test -s -v test_napalm_cfg.py --test_device nxos_ssh \
&& echo "Arista" \
&& py.test -s -v test_napalm_cfg.py --test_device eos \
&& echo "Juniper" \
&& py.test -s -v test_napalm_cfg.py --test_device junos \
\
|| RETURN_CODE=1

exit $RETURN_CODE
