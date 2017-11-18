import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
