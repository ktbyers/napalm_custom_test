import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time

# Relevant methods
# load_merge_candidate()
# load_replace_candidate()
# compare_config()
# discard_config()
# commit_config()
# rollback()

# commit confirmed mechanism
# IOS needs inline and SCP mechanism tested

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

def test_commit_config(napalm_config):
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
