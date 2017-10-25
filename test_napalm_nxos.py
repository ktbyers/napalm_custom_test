import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_facts(napalm_connect):
    napalm_connect.open()
    napalm_facts = napalm_connect.get_facts()
    assert isinstance(napalm_facts, type({}))
    assert napalm_facts['uptime'] > 0
    assert napalm_facts['vendor'].lower() == 'cisco'
    assert '7.3(1)D1(1)' in napalm_facts['os_version']
    assert isinstance(napalm_facts['serial_number'], type('')) and napalm_facts['serial_number']
    assert napalm_facts['hostname'] == 'nxos1'
    assert napalm_facts['fqdn'] == 'nxos1.twb-tech.com'
    assert napalm_facts["model"] == "NX-OSv Chassis"
    assert 'Ethernet2/1' in napalm_facts["interface_list"]
