from gwtf.version import show_versions


def test_show_versions_runs():
    # Should not raise any error
    try:
        show_versions()
    except Exception as e:
        assert False, f"show_versions raised {e}"
