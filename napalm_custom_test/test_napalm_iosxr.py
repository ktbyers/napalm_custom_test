def test_facts(napalm_connect):
    napalm_facts = napalm_connect.get_facts()
    assert isinstance(napalm_facts, type({}))
    assert napalm_facts['uptime'] > 0
    assert napalm_facts['vendor'].lower() == 'cisco'
    # assert '15.4(2)T1' in napalm_facts['os_version']
    # assert napalm_facts['serial_number'] == 'FTX1512038X'
    assert napalm_facts['hostname'] == 'pynet-iosxr1'
    assert napalm_facts['fqdn'] == 'pynet-iosxr1'
    # assert napalm_facts["model"] == "881"
    assert 'GigabitEthernet0/0/0/0' in napalm_facts["interface_list"]
