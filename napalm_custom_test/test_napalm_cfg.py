import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import re

# Relevant methods
# load_merge_candidate()
#    Merge done
#    Still need to merge from file
# load_replace_candidate()
# compare_config()
# discard_config()
# commit_config()
# rollback()

# commit confirmed mechanism
# IOS needs inline and SCP mechanism tested

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

def test_commit_config_hostname(napalm_config):
    filename = 'CFGS/{}/hostname_change.txt'.format(napalm_config._platform)
    if napalm_config._platform == 'ios':
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

def test_discard_config(napalm_config):
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    if napalm_config._platform == 'ios':
        napalm_config.load_replace_candidate(filename=filename)
        napalm_config.discard_config()
        output = napalm_config.compare_config()
        assert output == ''

def test_rollback(napalm_config):
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    if napalm_config._platform == 'ios':
        napalm_config.load_replace_candidate(filename=filename)
        output = napalm_config.compare_config()
        napalm_config.commit_config()
        output = napalm_config.device.send_command('show run | inc logging buffer')
        assert 'logging buffered 5000' in output
        # Now rollback to original state
        napalm_config.rollback()
        output = napalm_config.device.send_command('show run | inc logging buffer')
        assert 'logging buffered 10000' in output

def test_commit_confirm(napalm_config):
    """Commit confirm and confirm the change (replace)."""
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    # Load new candidate config
    napalm_config.load_replace_candidate(filename=filename)
    # Commit confirm with 3 minute confirm time
    napalm_config.commit_config(confirmed=3)
    # Verify revert timer is set
    output = napalm_config.device.send_command("show archive config rollback timer") 
    assert 'Timer value: 3 min' in output
    # Confirm the change
    napalm_config.commit_confirm()
    output = napalm_config.device.send_command("show archive config rollback timer") 
    assert '%No Rollback Confirmed Change pending' in output
    napalm_config.load_replace_candidate(filename=filename)
    output = napalm_config.compare_config()
    # Verify config has been committed
    assert output == ''

def test_commit_confirm_noconfirm(napalm_config):
    """Commit confirm with no confirm (replace)."""
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    # Load new candidate config
    napalm_config.load_replace_candidate(filename=filename)
    # Commit confirm with 1 minute confirm time
    napalm_config.commit_config(confirmed=1)
    # Verify revert timer is set
    output = napalm_config.device.send_command("show archive config rollback timer") 
    assert 'Timer value: 1 min' in output
    print("Sleeping 80 seconds...")
    time.sleep(80)
    output = napalm_config.device.send_command("show archive config rollback timer") 
    assert '%No Rollback Confirmed Change pending' in output
    napalm_config.load_replace_candidate(filename=filename)
    output = napalm_config.compare_config()
    # Should have rolled back so differences should exist
    if napalm_config._platform == 'ios':
        assert '+logging buffered 5000' in output
        assert '-logging buffered 10000' in output

def test_commit_confirm_abort(napalm_config):
    """Commit confirm but cancel the confirm and revert immediately (replace)."""
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    # Load new candidate config
    napalm_config.load_replace_candidate(filename=filename)
    # Commit confirm with 3 minute confirm time
    napalm_config.commit_config(confirmed=3)
    # Verify revert timer is set
    output = napalm_config.device.send_command("show archive config rollback timer") 
    assert 'Timer value: 3 min' in output
    napalm_config.commit_abort()
    output = napalm_config.device.send_command("show archive config rollback timer") 
    assert '%No Rollback Confirmed Change pending' in output
    napalm_config.load_replace_candidate(filename=filename)
    output = napalm_config.compare_config()
    # Should have rolled back so differences should exist
    if napalm_config._platform == 'ios':
        assert '+logging buffered 5000' in output
        assert '-logging buffered 10000' in output
