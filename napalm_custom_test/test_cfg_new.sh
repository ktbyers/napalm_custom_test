#!/bin/sh

RETURN_CODE=0

# Exit on the first test failure and set RETURN_CODE = 1
echo "Starting tests...good luck:" \
&& ./test_compare_cfg.sh \
&& ./test_merge_cfg.sh \
&& ./test_replace_cfg.sh \
&& ./test_discard_cfg.sh \
\
|| RETURN_CODE=1

exit $RETURN_CODE
