from decimal import BasicContext
from unittest.mock import patch, MagicMock
from io import StringIO
from pathlib import Path

import pytest

from munger import Munger, Hook, SchemaType

BASIC_CSV = "Field,OtherField\n" "1,a\n" "2,b\n" "3,c\n" "4,d\n"

BASIC_VALIDATION_SCHEMA = {
    "Field": {"type": "string"},
    "OtherField": {"type": "string", "maxlength": 1},
}


@patch("munger.open")
@patch("writer.open")
def test_munger_can_initialize(mock_writer_open, mock_open):
    mock_open.return_value = StringIO(BASIC_CSV)

    m = Munger()

    # give source file
    m.set_source_data("fish.csv")

    # assign just a validator schema
    m.set_schema(SchemaType.VALIDATE, BASIC_VALIDATION_SCHEMA)

    # register a valid writer
    mock_writer_open.return_value = StringIO()
    m.register_writer(Hook.END, filename="output.csv")


def test_munger_raises_exception_if_registering_a_schema_with_string():
    m = Munger()

    with pytest.raises(TypeError):
        m.set_schema("validation", BASIC_VALIDATION_SCHEMA)


# multiple patches must be given as args in opposite order
@patch("munger.open")
@patch("writer.open")
def test_munger_can_munge_a_simple_doc(mock_writer_open, mock_open):
    mock_open.return_value = StringIO(BASIC_CSV)

    m = Munger()

    m.set_source_data("fish.csv")
    m.set_schema(SchemaType.VALIDATE, BASIC_VALIDATION_SCHEMA)

    # register a valid writer
    output = StringIO()
    mock_writer_open.return_value = output
    m.register_writer(Hook.END, filename="output.csv")

    # munge the doc
    m.munge_all()

    # CSV Writer always outputs \r\n
    result = output.getvalue().replace("\r", "")
    # assert writer.write.call_count == 4
    assert result == BASIC_CSV


def test_munger_will_not_register_a_writer_without_a_source_file():
    m = Munger()

    # should raise an exception
    with pytest.raises(RuntimeError):
        m.register_writer(Hook.END, filename="fish.csv")


@patch("munger.open")
def test_munger_raises_exception_if_filename_and_suffix_are_both_passed_for_writer(
    mock_open,
):
    mock_open.return_value = StringIO()
    m = Munger()

    m.set_source_data("fish.csv")

    # should raise an exception
    with pytest.raises(TypeError):
        m.register_writer(Hook.END, filename="bird.csv", suffix="bird")


@patch("munger.open")
@patch("writer.open")
def test_munger_will_split_writes_according_to_a_condition(mock_writer_open, mock_open):
    m = Munger()

    mock_open.return_value = StringIO(BASIC_CSV)
    m.set_source_data("fish.csv")
    m.set_schema(SchemaType.VALIDATE, BASIC_VALIDATION_SCHEMA)

    def is_even(processor):
        return int(processor.document["Field"]) % 2 == 0

    condition_sio = StringIO()
    mock_writer_open.return_value = condition_sio
    m.register_writer(Hook.END, filename="condition.csv", condition=is_even)

    valid_sio = StringIO()
    mock_writer_open.return_value = valid_sio
    m.register_writer(Hook.END, filename="valid.csv")

    m.munge_all()

    # condition.csv should have half the rows
    valid_result = valid_sio.getvalue().replace("\r", "")
    condition_result = condition_sio.getvalue().replace("\r", "")

    valid_expected = "Field,OtherField\n1,a\n3,c\n"
    condition_expected = "Field,OtherField\n2,b\n4,d\n"

    assert valid_result == valid_expected
    assert condition_result == condition_expected


@patch("munger.open")
@patch("writer.open")
def test_munger_will_include_errors(mock_writer_open, mock_open):
    m = Munger()

    modified_csv = BASIC_CSV.replace("4,d", "4,dog")
    mock_open.return_value = StringIO(modified_csv)
    m.set_source_data("fish.csv")

    m.set_schema(SchemaType.VALIDATE, BASIC_VALIDATION_SCHEMA)

    valid_sio = StringIO()
    mock_writer_open.return_value = valid_sio
    m.register_writer(Hook.END, filename="bear.csv")

    invalid_sio = StringIO()
    mock_writer_open.return_value = invalid_sio
    m.register_writer(
        Hook.FAILED_VALIDATION, filename="invalid.csv", include_errors=True
    )

    m.munge_all()

    # invalid.csv should contain a column ValidationErrors with the document errors included
    result = invalid_sio.getvalue().replace("\r", "")
    expected = (
        "Field,OtherField,ValidationErrors\n4,dog,{'OtherField': ['max length is 1']}\n"
    )

    assert result == expected


@patch("munger.open")
@patch("writer.open")
def test_munger_raises_an_exception_if_trying_to_munge_with_no_processors(
    mock_writer_open, mock_open
):
    m = Munger()

    mock_open.return_value = StringIO(BASIC_CSV)
    m.set_source_data("fish.csv")

    mock_writer_open.return_value = StringIO()
    m.register_writer(Hook.END, filename="output.csv")

    with pytest.raises(RuntimeError):
        m.munge_all()


@patch("munger.open")
@patch("writer.open")
def test_munger_can_filter_data(mock_writer_open, mock_open):
    m = Munger()

    mock_open.return_value = StringIO(BASIC_CSV)
    m.set_source_data("fish.csv")

    def is_even(field, value, error):
        if int(value) % 2 != 0:
            error(field, "Not even number")

    filter_schema = {"Field": {"check_with": is_even}}
    m.set_schema(SchemaType.FILTER, filter_schema, allow_unknown=True)

    output = StringIO()
    mock_writer_open.return_value = output
    m.register_writer(Hook.END, filename="output.csv")

    filtered = StringIO()
    mock_writer_open.return_value = filtered
    m.register_writer(Hook.FAILED_FILTER, filename="filtered.csv")

    m.munge_all()

    result = output.getvalue().replace("\r", "")
    expected = "Field,OtherField\n2,b\n4,d\n"

    assert result == expected

    result = filtered.getvalue().replace("\r", "")
    expected = "Field,OtherField\n1,a\n3,c\n"

    assert result == expected


@patch("munger.open")
@patch("writer.open")
def test_munger_inserts_writer_suffixes_into_source_filename(
    mock_writer_open, mock_open
):
    m = Munger()

    mock_open.return_value = StringIO(BASIC_CSV)
    m.set_source_data("../indexes/fish.csv")

    output = StringIO()
    mock_writer_open.return_value = output
    m.register_writer(Hook.END, suffix="cleaned")

    # why 0 to access args? i dunno
    mock_writer_open.assert_called()
    res_path, _ = mock_writer_open.call_args[0]
    exp_path = Path("../indexes/fish-cleaned.csv")
    # converting to string normalizes Windows/Linux paths
    assert str(res_path) == str(exp_path)
