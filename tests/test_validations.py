from unittest.mock import MagicMock

from munger.validations import (
    has_only_ascii,
    is_upper,
    uds_style_path,
    is_numeric,
    has_datamapper_date_format,
    has_datamapper_time_format,
    does_not_have_char,
)


def test_has_only_ascii():
    valid = "fish"
    invalid = "fish\ufeff"

    mock_error = MagicMock()
    has_only_ascii("test", valid, mock_error)

    assert not mock_error.called

    mock_error = MagicMock()
    has_only_ascii("test", invalid, mock_error)

    assert mock_error.called


def test_is_upper():
    valid = "FISH"
    invalid = "Fish"

    mock_error = MagicMock()
    is_upper("test", valid, mock_error)

    assert not mock_error.called

    mock_error = MagicMock()
    is_upper("test", invalid, mock_error)

    assert mock_error.called


def test_uds_style_path():
    valid = "\\fish\\bird\\"
    invalid = "fish\\bird\\"

    mock_error = MagicMock()
    uds_style_path("test", valid, mock_error)

    assert not mock_error.called

    mock_error = MagicMock()
    uds_style_path("test", invalid, mock_error)

    assert mock_error.called


def test_is_numeric():
    valid = "12345"
    invalid = "63CBLG101010"

    mock_error = MagicMock()
    is_numeric("test", valid, mock_error)

    assert not mock_error.called

    mock_error = MagicMock()
    is_numeric("test", invalid, mock_error)

    assert mock_error.called


def test_has_datamapper_date_format():
    valid = (
        "20210504",
        "05/04/2021",
        "05/04/21",
        "04 January 2021",
        "04 January 21",
        "04 Jan 21",
        "5/4/2021",
        "5/4/21",
    )
    invalid = ("2021-May-04", "05-04-2021", "May 4th 2021")

    for value in valid:
        mock_error = MagicMock()
        has_datamapper_date_format("date", value, mock_error)
        assert not mock_error.called

    for value in invalid:
        mock_error = MagicMock()
        has_datamapper_date_format("date", value, mock_error)
        assert mock_error.called


def test_has_datamapper_time_format():
    valid = (
        "12:30 PM",
        "12:30:25 PM",
        "12:30",
        "12:30:25",
        "123025",
    )
    invalid = ("Quarter past 12", "5/4/2021", "12:30:25T-5:00")

    for value in valid:
        mock_error = MagicMock()
        has_datamapper_time_format("date", value, mock_error)
        assert not mock_error.called

    for value in invalid:
        mock_error = MagicMock()
        has_datamapper_time_format("date", value, mock_error)
        assert mock_error.called


def test_does_not_have_char():
    no_dot_valid = "pdf"
    no_dot_invalid = ".pdf"

    no_e_valid = "missing vowl"
    no_e_invalid = "not missing vowel"

    mock_error = MagicMock()
    does_not_have_char(".")("test", no_dot_valid, mock_error)
    assert not mock_error.called

    mock_error = MagicMock()
    does_not_have_char(".")("test", no_dot_invalid, mock_error)
    assert mock_error.called

    mock_error = MagicMock()
    does_not_have_char("e")("test", no_e_valid, mock_error)
    assert not mock_error.called

    mock_error = MagicMock()
    does_not_have_char("e")("test", no_e_invalid, mock_error)
    assert mock_error.called
