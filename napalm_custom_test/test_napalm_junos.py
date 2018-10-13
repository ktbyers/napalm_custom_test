def test_facts(napalm_connect):
    napalm_facts = napalm_connect.get_facts()
    assert isinstance(napalm_facts, type({}))
    assert napalm_facts["uptime"] > 0
    assert napalm_facts["vendor"].lower() == "juniper"
    assert "12.1X44-D35.5" in napalm_facts["os_version"]
    assert napalm_facts["serial_number"] == "BZ4614AF0938"
    assert "pynet-jnpr-srx1" in napalm_facts["hostname"]
    assert napalm_facts["fqdn"] == "pynet-jnpr-srx1"
    assert napalm_facts["model"] == "SRX100H2"
    assert "fe-0/0/7" in napalm_facts["interface_list"]
