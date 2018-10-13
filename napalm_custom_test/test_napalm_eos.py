import six


def test_facts(napalm_connect):
    napalm_facts = napalm_connect.get_facts()
    assert isinstance(napalm_facts, type({}))
    assert napalm_facts["uptime"] > 0
    assert napalm_facts["vendor"].lower() == "arista"
    assert "4.15.4F" in napalm_facts["os_version"]
    assert isinstance(napalm_facts["serial_number"], six.string_types)
    assert "pynet-sw8" in napalm_facts["hostname"]
    assert napalm_facts["fqdn"] == "pynet-sw8"
    assert "vEOS" in napalm_facts["model"]
    assert "Ethernet1" in napalm_facts["interface_list"]
