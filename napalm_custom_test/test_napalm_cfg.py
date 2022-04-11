import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import re
import pytest

from napalm.base.exceptions import MergeConfigException, ReplaceConfigException

# Relevant methods
# load_merge_candidate()    DONE
# load_replace_candidate()  DONE
# compare_config()          DONE
# discard_config()          DONE
# commit_config()           DONE
# rollback()                DONE

# IOS needs inline and SCP mechanism tested
# IOS needs inline transfer testing
# Banner tests on IOS and NX-OS

# Merge compare_config for IOS, junos, eos


def retrieve_config(napalm_config):
    """Retrieve the running and startup-config from remote device."""
    config = napalm_config.get_config()
    running_config = config["running"]
    startup_config = config["startup"]
    if napalm_config._platform in ["junos", "iosxr"]:
        startup_config = running_config
    return (running_config, startup_config)


def test_compare_config(napalm_config):
    filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform)
    print(filename)
    napalm_config.load_replace_candidate(filename=filename)
    output = napalm_config.compare_config()
    print(output)
    if napalm_config._platform == "ios":
        assert "+logging buffered 5000" in output
        assert "-logging buffered 10000" in output
    elif napalm_config._platform == "eos":
        assert "+ntp server 130.126.24.24" in output
    elif napalm_config._platform in ["nxos", "nxos_ssh"]:
        assert "logging monitor 2"
    elif napalm_config._platform == "junos":
        assert "-    archive size 120k files 3;" in output
        assert "+    archive size 240k files 3;" in output
    elif napalm_config._platform == "iosxr":
        assert "#  logging buffered 4000010" in output
        assert "#  logging buffered 3000000" in output
    else:
        assert False


def test_compare_config_inline(napalm_config):
    filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform)
    with open(filename) as f:
        config = f.read()
    napalm_config.load_replace_candidate(config=config)
    output = napalm_config.compare_config()
    print(output)
    if napalm_config._platform == "ios":
        assert "+logging buffered 5000" in output
        assert "-logging buffered 10000" in output
    elif napalm_config._platform == "eos":
        assert "+ntp server 130.126.24.24" in output
    elif napalm_config._platform in ["nxos", "nxos_ssh"]:
        assert "logging monitor 1"
    elif napalm_config._platform == "junos":
        assert "-    archive size 120k files 3;" in output
        assert "+    archive size 240k files 3;" in output
    elif napalm_config._platform == "iosxr":
        assert "#  logging buffered 4000010" in output
        assert "#  logging buffered 3000000" in output
    else:
        assert False


def test_merge_compare_config(napalm_config):
    """Tests NAPALM compare config in a merge context.

    Merge load comes from inline 'config'.
    """
    # Actual change that is made on device
    merge_change = {
        "nxos": "logging monitor 1",
        "nxos_ssh": "logging monitor 1",
        "iosxr": "logging buffered 3000000",
    }

    platform = napalm_config._platform
    if platform in list(merge_change.keys()):
        # Stage the merge change
        config_chg = merge_change[platform]
        napalm_config.load_merge_candidate(config=config_chg)
        diff = napalm_config.compare_config()
        if platform in ["nxos", "nxos_ssh"]:
            assert merge_change[platform] == diff.strip()
        elif platform in ["iosxr"]:
            assert "-logging buffered 4000010" in diff
            assert "+logging buffered 3000000" in diff
        napalm_config.discard_config()


def test_merge_inline_commit_config(napalm_config):
    """Tests NAPALM merge operation incluging commit.

    Merge load comes from inline 'config'

    Verify that change is included in running-config and startup-config
    """
    # Actual change that is made on device
    merge_change = {
        "eos": "logging buffered 7000",
        "ios": "logging buffered 7000",
        "junos": "set system syslog archive size 200k files 3",
        "nxos": "logging monitor 1",
        "nxos_ssh": "logging monitor 1",
        "iosxr": "logging buffered 3000000",
    }

    # Pattern that we search for in the end-config
    merge_search = {}
    merge_search.update(merge_change)
    merge_search.update({"junos": "archive size 200k files 3"})
    platform = napalm_config._platform

    if platform in list(merge_change.keys()):
        config_pattern = merge_search[platform]

        # Stage the merge change
        config_chg = merge_change[platform]
        napalm_config.load_merge_candidate(config=config_chg)
        napalm_config.commit_config()

        running_config, startup_config = retrieve_config(napalm_config)
        running = True if re.search(config_pattern, running_config) else False
        startup = True if re.search(config_pattern, startup_config) else False
        assert running and startup
    else:
        assert False


def test_merge_file_commit_config(napalm_config):
    """Tests NAPALM merge operation incluging commit.

    Merge load comes from inline 'config'

    Verify that change is included in running-config and startup-config
    """
    # Config change comes from the file
    filename = "CFGS/{}/merge_1.txt".format(napalm_config._platform)
    platform = napalm_config._platform

    if platform in ("eos", "ios", "junos", "nxos", "nxos_ssh"):

        # Pattern to search for after config change
        with open(filename) as f:
            config_pattern = re.escape(f.read())
        if platform == "junos":
            config_pattern = r"archive size 200k files 3"

        # Stage the merge change
        napalm_config.load_merge_candidate(filename=filename)
        napalm_config.commit_config()

        running_config, startup_config = retrieve_config(napalm_config)
        running = True if re.search(config_pattern, running_config) else False
        startup = True if re.search(config_pattern, startup_config) else False
        assert running and startup
    else:
        assert False


def test_merge_failure(napalm_config):
    """Tests NAPALM merge operation incluging commit.

    Merge load comes from inline 'config'

    Commands will be invalid so should result in an exception and then a rollback.
    """
    # Actual change that is made on device

    merge_change = {
        "nxos": "logging monitor 1\nbogus command1",
        "nxos_ssh": "logging monitor 1\nbogus command1",
    }
    initial_cfg = {"nxos": "logging monitor 2", "nxos_ssh": "logging monitor 2"}

    platform = napalm_config._platform
    if platform in list(merge_change.keys()):

        initial_state = initial_cfg[platform]

        # Stage the merge change
        config_chg = merge_change[platform]
        napalm_config.load_merge_candidate(config=config_chg)
        with pytest.raises(MergeConfigException):
            # Should auto rollback the change
            napalm_config.commit_config()

        running_config, startup_config = retrieve_config(napalm_config)
        running = True if re.search(initial_state, running_config) else False
        startup = True if re.search(initial_state, startup_config) else False
        assert running and startup
    else:
        assert True


def test_replace_commit_config(napalm_config):

    # Configuration element that is being changed to search for in end-config
    replace_pattern = {
        "eos": "ntp server 130.126.24.24",
        "ios": "logging buffered 5000",
        "junos": "archive size 240k files 3",
        "nxos": "logging monitor 1",
        "nxos_ssh": "logging monitor 1",
        "iosxr": "logging buffered 3000000",
    }

    platform = napalm_config._platform

    if platform in list(replace_pattern.keys()):

        config_pattern = replace_pattern[platform]

        # Stage new config for configuration replacement
        filename = "CFGS/{}/compare_1.txt".format(platform)
        napalm_config.load_replace_candidate(filename=filename)

        napalm_config.commit_config()

        running_config, startup_config = retrieve_config(napalm_config)
        running = True if re.search(config_pattern, running_config) else False
        startup = True if re.search(config_pattern, startup_config) else False
        assert running and startup
    else:
        assert False


def test_discard_config(napalm_config):

    platform = napalm_config._platform

    # Discard on a replace operation
    filename = "CFGS/{}/compare_1.txt".format(platform)
    napalm_config.load_replace_candidate(filename=filename)
    napalm_config.discard_config()
    output_replace = napalm_config.compare_config()
    assert output_replace == ""

    # Discard on a merge operation
    merge_change = {
        "eos": "logging buffered 7000",
        "ios": "logging buffered 7000",
        "junos": "set system syslog archive size 200k files 3",
        "nxos": "logging monitor 1",
        "nxos_ssh": "logging monitor 1",
        "iosxr": "logging buffered 3000000",
    }

    # Stage the merge change
    config_chg = merge_change[platform]
    napalm_config.load_merge_candidate(config=config_chg)

    napalm_config.discard_config()
    output_merge = napalm_config.compare_config()
    assert output_merge == ""


def test_rollback(napalm_config):
    platform = napalm_config._platform

    config_change = {
        "eos": "ntp server 130.126.24.24",
        "ios": "logging buffered 5000",
        "nxos": "logging monitor 1",
        "nxos_ssh": "logging monitor 1",
        "junos": "archive size 240k files 3",
        "iosxr": "logging buffered 3000000",
    }

    original_cfg = {
        "eos": "",
        "ios": "logging buffered 10000",
        "nxos": "logging monitor 2",
        "nxos_ssh": "logging monitor 2",
        "junos": "archive size 120k files 3",
        "iosxr": "logging buffered 4000010",
    }

    filename = "CFGS/{}/compare_1.txt".format(platform)
    if platform in config_change.keys():

        config_pattern = config_change[platform]

        napalm_config.load_replace_candidate(filename=filename)
        napalm_config.commit_config()

        running_config, startup_config = retrieve_config(napalm_config)
        running = True if re.search(config_pattern, running_config) else False
        assert running

        # Now rollback to original state
        napalm_config.rollback()
        original_pattern = original_cfg[platform]
        running_config, startup_config = retrieve_config(napalm_config)
        if platform == "eos":
            # For EOS that NTP server should be missing
            running = False if re.search(config_pattern, running_config) else True
        else:
            running = True if re.search(original_pattern, running_config) else False
        assert running


def test_commit_config_hostname(napalm_config):
    filename = "CFGS/{}/hostname_change.txt".format(napalm_config._platform)
    platform = napalm_config._platform
    if platform in ["ios"]:
        napalm_config.load_replace_candidate(filename=filename)
        napalm_config.commit_config()
        running_config = napalm_config.get_config()["running"]
        for line in running_config.splitlines():
            if "hostname test-rtr1" in line:
                status = True
                break
        else:
            status = False
        assert status
    elif platform in ["nxos", "nxos_ssh"]:
        napalm_config.load_replace_candidate(filename=filename)
        napalm_config.commit_config()
        running_config = napalm_config.get_config()["running"]
        for line in running_config.splitlines():
            if "hostname test-newprompt1" in line:
                status = True
                break
        else:
            status = False
        assert status


def test_commit_config_hostname_merge(napalm_config):
    filename = "CFGS/{}/hostname_change_merge.txt".format(napalm_config._platform)
    platform = napalm_config._platform
    if platform in ["ios"]:
        napalm_config.load_merge_candidate(filename=filename)
        napalm_config.commit_config()
        running_config = napalm_config.get_config()["running"]
        for line in running_config.splitlines():
            if "hostname test-rtr1" in line:
                status = True
                break
        else:
            status = False
        assert status

        # Now try to rollback the hostname change
        napalm_config.rollback()
        running_config = napalm_config.get_config()["running"]
        for line in running_config.splitlines():
            if "hostname cisco1" in line:
                status = True
                break
        else:
            status = False
        assert status

    elif platform in ["nxos", "nxos_ssh"]:
        napalm_config.load_merge_candidate(filename=filename)
        napalm_config.commit_config()
        running_config = napalm_config.get_config()["running"]
        for line in running_config.splitlines():
            if "hostname test-newprompt1" in line:
                status = True
                break
        else:
            status = False
        assert status

        # Now try to rollback the hostname change
        napalm_config.rollback()
        running_config = napalm_config.get_config()["running"]
        for line in running_config.splitlines():
            if "hostname nxos1" in line:
                status = True
                break
        else:
            status = False
        assert status


def test_cfg_exceptions(napalm_config):

    # filename or config not specified
    with pytest.raises(ReplaceConfigException):
        napalm_config.load_replace_candidate()
    with pytest.raises(MergeConfigException):
        napalm_config.load_merge_candidate()

    # Invalid filename
    with pytest.raises(ReplaceConfigException):
        napalm_config.load_replace_candidate(filename="invalid_file_x")

    platform = napalm_config._platform
    if platform in ("nxos", "nxos_ssh"):
        # Commit Config with a message
        with pytest.raises(NotImplementedError):
            napalm_config.commit_config(message="should raise not implemented")

        # No change staged
        napalm_config.discard_config()
        with pytest.raises(ReplaceConfigException):
            napalm_config.commit_config()

        # No exception if the sot_file doesn't exist
        napalm_config._delete_file(filename="sot_file")
        napalm_config._create_sot_file()
        assert True


def test_commit_confirm(napalm_config):
    """Commit confirm and confirm the change (replace)."""

    if napalm_config._platform_host:
        filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform_host)
    else:
        filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform)
    platform = napalm_config._platform

    if platform in ["eos", "junos"]:
        # Load new candidate config
        napalm_config.load_replace_candidate(filename=filename)

        # Commit confirm with 300 second confirm time
        napalm_config.commit_config(revert_in=300)

        # Verify pending commit confirm
        assert napalm_config.has_pending_commit()

        # Verify revert timer is set
        pending_commit = napalm_config._get_pending_commits()
        for config_session, confirm_by_time in pending_commit.items():
            assert confirm_by_time > 240
            assert confirm_by_time <= 300

        # Confirm the change
        napalm_config.confirm_commit()

        # There should be no active commit-confirms at this point
        assert not napalm_config.has_pending_commit()

        # Verify config has been committed
        napalm_config.load_replace_candidate(filename=filename)
        output = napalm_config.compare_config()
        assert output == ""

    else:

        with pytest.raises(NotImplementedError):
            napalm_config.commit_config(revert_in=600)


def test_commit_confirm_noconfirm(napalm_config):
    """Commit confirm with no confirm (replace)."""

    if napalm_config._platform_host:
        filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform_host)
    else:
        filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform)
    platform = napalm_config._platform

    if platform in ["eos", "junos"]:

        # Load new candidate config
        napalm_config.load_replace_candidate(filename=filename)

        # Commit confirm with 1 minute confirm time
        napalm_config.commit_config(revert_in=60)

        # Verify pending commit confirm
        assert napalm_config.has_pending_commit()

        # Juniper is slow to rollback.
        print("Sleeping 150 seconds...")
        time.sleep(150)

        # Verify pending commit confirm
        assert not napalm_config.has_pending_commit()

        # Should have rolled back so differences should exist
        napalm_config.load_replace_candidate(filename=filename)
        output = napalm_config.compare_config()
        assert output != ""


def test_commit_confirm_revert(napalm_config):
    """Commit confirm but cancel the confirm and revert immediately (replace)."""

    if napalm_config._platform_host:
        filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform_host)
    else:
        filename = "CFGS/{}/compare_1.txt".format(napalm_config._platform)
    platform = napalm_config._platform

    if platform in ["eos", "junos"]:

        # Load new candidate config
        napalm_config.load_replace_candidate(filename=filename)

        # Commit confirm with 3 minute confirm time
        napalm_config.commit_config(revert_in=300)

        # Verify pending commit confirm
        assert napalm_config.has_pending_commit()

        napalm_config.rollback()

        # Verify pending commit confirm
        assert not napalm_config.has_pending_commit()

        # Should have rolled back so differences should exist
        napalm_config.load_replace_candidate(filename=filename)
        output = napalm_config.compare_config()
        assert output != ""

        napalm_config.discard_config()
