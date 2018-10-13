#!/usr/bin/env python
from __future__ import unicode_literals, print_function

from email_helper import send_mail
import subprocess

RECIPIENTS = ["ktbyersx@gmail.com"]
SUBJECT = "NAPALM configuration testing"
MESSAGE = "TESTS PASSED"
SENDER = "ktbyers@twb-tech.com"

NAPALM_TESTS = {
    "compare_config": ["./test_compare_cfg.sh"],
    "merge_inline_commit_config": ["./test_merge_cfg.sh"],
    "test_replace_commit_config": ["./test_replace_cfg.sh"],
    "discard_config": ["./test_discard_cfg.sh"],
    "rollback": ["./test_rollback.sh"],
}


def main():

    message = MESSAGE
    divider = "\n"
    divider += "-" * 80
    divider += "\n"

    test_passed = True
    for test_name, napalm_test in NAPALM_TESTS.items():
        print("{}: {}".format(test_name, napalm_test))
        proc = subprocess.Popen(
            napalm_test, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        (std_out, std_err) = proc.communicate()
        return_code = proc.returncode
        if int(return_code) != 0:
            test_passed = False
            message = divider
            message += "TESTS FAILED\n"
            message += "TEST NAME: {}".format(test_name)
            message += divider
            message += divider
            message += std_out.decode()
            message += std_err.decode()
            message += divider
            break

    for recipient in RECIPIENTS:
        send_mail(recipient=recipient, subject=SUBJECT, message=message, sender=SENDER)


if __name__ == "__main__":
    main()
