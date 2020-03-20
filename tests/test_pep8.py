import pycodestyle


def test_conformance():
    """Test that we conform to PEP-8."""
    # E731 ignores lamda, W291 trailing whitespace
    # W391 blank line at end of file
    # W292 no newline at end of file
    # E722 bare except
    # W293 blank line white space
    style = pycodestyle.StyleGuide(quiet=False,
                                   ignore=['E501', 'E731', 'W291',
                                           'W391', 'W292', 'E722',
                                           'W293'])
    # style.input_dir('../../pya')
    style.input_dir('./src/')
    # style.input_dir('tests')
    result = style.check_files()
    assert result.total_errors == 0