from unittest.mock import MagicMock

from munger.validations import has_datamapper_date_format, has_datamapper_time_format


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
