from munger.coercions import (
    strip,
    upper,
    truncate,
    datetime_to_format,
    relative_to_folder,
    get_parent_folder,
    get_filename,
    insert_base_folder,
    extract_file_ext,
    to_uds_path,
)


def test_strip():
    result = strip("    fish      ")
    expected = "fish"

    assert result == expected


def test_upper():
    result = upper("fish")
    expected = "FISH"

    assert result == expected


def test_truncate():
    func = truncate(10)
    result = func("More than 10 characters")
    expected = "More than "

    assert result == expected


def test_datetime_to_format_with_date():
    input = "January 4th, 2021"

    func = datetime_to_format("YYYYMMDD")
    result = func(input)
    expected = "20210104"

    assert result == expected


def test_datetime_to_format_with_time():
    input = "2022-05-03 11:04:17.397000"

    func = datetime_to_format("HH:mm:ss")
    result = func(input)
    expected = "11:04:17"

    assert result == expected


def test_relative_to_folder_with_windows_path():
    path = "\\Fish\\Bird\\test.pdf"

    func = relative_to_folder("\\Fish\\")
    result = func(path)
    expected = "Bird\\test.pdf"

    assert result == expected


def test_relative_to_folder_with_posix_path():
    path = "/fish/bird/test.pdf"

    func = relative_to_folder("/fish")
    result = func(path)
    expected = "bird/test.pdf"

    assert result == expected


def test_get_parent_folder_with_windows_path():
    path = "\\Fish\\Bird\\test.pdf"

    result = get_parent_folder(path)
    expected = "\\Fish\\Bird"

    assert result == expected


def test_get_parent_folder_with_posix_path():
    path = "/fish/bird/test.pdf"

    result = get_parent_folder(path)
    expected = "/fish/bird"

    assert result == expected


def test_get_filename_with_windows_path():
    path = "\\Fish\\Bird\\test.pdf"

    result = get_filename(path)
    expected = "test.pdf"

    assert result == expected


def test_get_filename_with_posix_path():
    path = "/fish/bird/test.pdf"

    result = get_filename(path)
    expected = "test.pdf"

    assert result == expected


def test_insert_base_folder_with_windows_path():
    path = "fish\\bird\\test.pdf"

    func = insert_base_folder("bear")
    result = func(path)
    expected = "bear\\fish\\bird\\test.pdf"

    assert result == expected


def test_insert_base_folder_with_posix_path():
    path = "fish/bird/test.pdf"

    func = insert_base_folder("bear")
    result = func(path)
    expected = "bear/fish/bird/test.pdf"

    assert result == expected


def test_extract_file_ext():
    """Should be the same for Windows and Posix"""
    path = "fish/bird/test.pdf"

    result = extract_file_ext(path)
    expected = "pdf"

    assert result == expected


def test_to_uds_path_with_windows_path():
    path = "fish\\bird"

    result = to_uds_path(path)
    expected = "\\fish\\bird\\"

    assert result == expected


def test_to_uds_path_with_posix_path():
    path = "fish/bird"

    result = to_uds_path(path)
    expected = "\\fish\\bird\\"

    assert result == expected
