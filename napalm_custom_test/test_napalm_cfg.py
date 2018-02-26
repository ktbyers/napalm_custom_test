import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import re

# Relevant methods
# load_merge_candidate()    DONE
#    Still need to merge from file      NEEDS DONE
# load_replace_candidate()  DONE
# compare_config()          DONE
# discard_config()          DONE
# commit_config()           DONE
# rollback()                DONE

# commit confirmed mechanism
# IOS needs inline and SCP mechanism tested
# IOS needs inline transfer testing

def retrieve_config(napalm_config):
    """Retrieve the running and startup-config from remote device."""
    config = napalm_config.get_config()
    running_config = config['running']
    startup_config = config['startup']
    if napalm_config._platform == 'junos':
        startup_config = running_config
    return (running_config, startup_config)


def test_compare_config(napalm_config):
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    print(filename)
    napalm_config.load_replace_candidate(filename=filename)
    output = napalm_config.compare_config()
    print(output)
    if napalm_config._platform == 'ios':
        assert '+logging buffered 5000' in output
        assert '-logging buffered 10000' in output
    elif napalm_config._platform == 'eos':
        assert '+ntp server 130.126.24.24' in output
    elif napalm_config._platform == 'nxos':
        assert 'logging history size 200' in output
    elif napalm_config._platform == 'nxos_ssh':
        assert 'logging history size 200' in output
    elif napalm_config._platform == 'junos':
        assert '-    archive size 120k files 3;' in output
        assert '+    archive size 240k files 3;' in output
    else:
        assert False


def test_merge_inline_commit_config(napalm_config):
    """Tests NAPALM merge operation incluging commit.

    Merge load comes from inline 'config'

    Verify that change is included in running-config and startup-config
    """
    # Actual change that is made on device
    merge_change = {
        'eos': 'logging buffered 7000',
        'ios': 'logging buffered 7000',
        'junos': 'set system syslog archive size 200k files 3',
        'nxos': 'logging history size 100',
        'nxos_ssh': 'logging history size 100',
    }

    # Pattern that we search for in the end-config
    merge_search = {}
    merge_search.update(merge_change)
    merge_search.update({'junos': 'archive size 200k files 3'})
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


def test_replace_commit_config(napalm_config):

    # Configuration element that is being changed to search for in end-config
    replace_pattern = {
        'eos': 'ntp server 130.126.24.24',
        'ios': 'logging buffered 5000',
        'junos': 'archive size 240k files 3',
        'nxos': 'logging history size 200',
        'nxos_ssh': 'logging history size 200',
    }

    platform = napalm_config._platform

    if platform in list(replace_pattern.keys()):
        
        config_pattern = replace_pattern[platform]

        # Stage new config for configuration replacement
        filename = 'CFGS/{}/compare_1.txt'.format(platform)
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
    filename = 'CFGS/{}/compare_1.txt'.format(platform)
    napalm_config.load_replace_candidate(filename=filename)
    napalm_config.discard_config()
    output_replace = napalm_config.compare_config()
    assert output_replace == ''

    # Discard on a merge operation
    merge_change = {
        'eos': 'logging buffered 7000',
        'ios': 'logging buffered 7000',
        'junos': 'set system syslog archive size 200k files 3',
        'nxos': 'logging history size 100',
        'nxos_ssh': 'logging history size 100',
    }

    # Stage the merge change
    config_chg = merge_change[platform]
    napalm_config.load_merge_candidate(config=config_chg)

    napalm_config.discard_config()
    output_merge = napalm_config.compare_config()
    assert output_merge == ''


def test_rollback(napalm_config):
    platform = napalm_config._platform

    config_change = {
        'eos': 'ntp server 130.126.24.24',
        'ios': 'logging buffered 5000',
        'nxos': 'logging history size 200',
        'nxos_ssh': 'logging history size 200',
        'junos': 'archive size 240k files 3',
    }

    original_cfg = {
        'eos': '',
        'ios': 'logging buffered 10000',
        'nxos': 'logging history size 400',
        'nxos_ssh': 'logging history size 400',
        'junos': 'archive size 120k files 3',
    }

    filename = 'CFGS/{}/compare_1.txt'.format(platform)
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
        if platform == 'eos':
            # For EOS that NTP server should be missing
            running = False if re.search(config_pattern, running_config) else True
        else:
            running = True if re.search(original_pattern, running_config) else False
        assert running


def test_commit_config_hostname(napalm_config):
    filename = 'CFGS/{}/hostname_change.txt'.format(napalm_config._platform)
    platform = napalm_config._platform
    if platform in ['ios']:
        napalm_config.load_replace_candidate(filename=filename)
        napalm_config.commit_config()
        running_config = napalm_config.get_config()['running']
        for line in running_config.splitlines():
            if 'hostname test-rtr1' in line:
                status = True
                break
        else:
            status = False
        assert status


def test_commit_confirm(napalm_config):
    """Commit confirm and confirm the change (replace)."""
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    platform = napalm_config._platform
    if platform in ['ios']:
        # Load new candidate config
        napalm_config.load_replace_candidate(filename=filename)

        # Commit confirm with 3 minute confirm time
        napalm_config.commit_config(confirmed=3)

        # Verify pending commit confirm
        assert napalm_config.has_pending_commit()

        # Verify revert timer is set
        # output = napalm_config.device.send_command("show archive config rollback timer") 
        # assert 'Timer value: 3 min' in output

        # Confirm the change
        napalm_config.commit_confirm()

        # Should be no pending commits
        assert not napalm_config.has_pending_commit()

        # Verify config has been committed
        napalm_config.load_replace_candidate(filename=filename)
        output = napalm_config.compare_config()
        assert output == ''


def test_commit_confirm_noconfirm(napalm_config):
    """Commit confirm with no confirm (replace)."""
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    platform = napalm_config._platform
    if platform in ['ios']:

        # Load new candidate config
        napalm_config.load_replace_candidate(filename=filename)

        # Commit confirm with 1 minute confirm time
        napalm_config.commit_config(confirmed=1)

        # Verify pending commit confirm
        assert napalm_config.has_pending_commit()

        print("Sleeping 80 seconds...")
        time.sleep(80)

        # Verify pending commit confirm
        assert not napalm_config.has_pending_commit()

        # Should have rolled back so differences should exist
        napalm_config.load_replace_candidate(filename=filename)
        output = napalm_config.compare_config()
        assert output != ''


def test_commit_confirm_revert(napalm_config):
    """Commit confirm but cancel the confirm and revert immediately (replace)."""
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    platform = napalm_config._platform
    if platform in ['ios']:

        # Load new candidate config
        napalm_config.load_replace_candidate(filename=filename)

        # Commit confirm with 3 minute confirm time
        napalm_config.commit_config(confirmed=3)

        # Verify pending commit confirm
        assert napalm_config.has_pending_commit()

        napalm_config.commit_confirm_revert()

        # Verify pending commit confirm
        assert not napalm_config.has_pending_commit()

        # Should have rolled back so differences should exist
        napalm_config.load_replace_candidate(filename=filename)
        output = napalm_config.compare_config()
        assert output != ''
