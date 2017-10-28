#!/bin/sh

RETURN_CODE=0

# Exit on the first test failure and set RETURN_CODE = 1
echo "Starting tests...good luck:" \
&& echo "Cisco IOS" \
&& py.test -v test_napalm_ios.py --test_device ios \
&& echo "Cisco NX-OS (API)" \
&& py.test -v test_napalm_nxos.py --test_device nxos \
&& echo "Cisco NX-OS (SSH)" \
&& py.test -v test_napalm_nxos.py --test_device nxos_ssh \
&& echo "Arista" \
&& py.test -v test_napalm_eos.py --test_device eos \
&& echo "Juniper" \
&& py.test -v test_napalm_junos.py --test_device junos \
\
|| RETURN_CODE=1

exit $RETURN_CODE
