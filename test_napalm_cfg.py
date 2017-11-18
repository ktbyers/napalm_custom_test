def test_compare_config(napalm_config):
    filename = 'CFGS/{}/compare_1.txt'.format(napalm_config._platform)
    print(filename)
    napalm_config.load_replace_candidate(filename=filename)
    output = napalm_config.compare_config()
    print(output)
    if napalm_config._platform == 'ios':
        assert '+logging buffered 5000' in output
        assert '-logging buffered 10000' in output
    else:
        assert True
