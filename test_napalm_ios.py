def test_facts(napalm_connect):
    napalm_connect.open()
    napalm_facts = napalm_connect.get_facts()
    assert isinstance(napalm_facts, type({}))
    assert napalm_facts['uptime'] > 0
    assert napalm_facts['vendor'].lower() == 'cisco'
    assert '15.4(2)T1' in napalm_facts['os_version']
    assert napalm_facts['serial_number'] == 'FTX1512038X'
    assert napalm_facts['hostname'] == 'pynet-rtr1'
    assert napalm_facts['fqdn'] == 'pynet-rtr1.twb-tech.com'
    assert napalm_facts["model"] == "881"
    assert 'FastEthernet4' in napalm_facts["interface_list"]
