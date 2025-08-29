
def test_policy_files_exist():
    import os
    for p in [
        'core/safety/policies/medical.yaml',
        'core/safety/policies/legal.yaml',
        'core/safety/policies/finance.yaml']:
        assert os.path.exists(p)
