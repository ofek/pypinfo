import copy
import pytest

from pypinfo import core

ROWS = [
    ['python_version', 'percent', 'download_count'],
    ['2.7', '51.7%', '342250'],
    ['3.6', '21.1%', '139745'],
    ['3.5', '17.2%', '114254'],
    ['3.4', '7.6%', '50584'],
    ['3.3', '1.0%', '6666'],
    ['3.7', '0.7%', '4516'],
    ['2.6', '0.7%', '4451'],
    ['3.2', '0.0%', '138'],
    ['None', '0.0%', '13'],
]


def test_tabulate_default():
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = """\
| python_version | percent | download_count |
| -------------- | ------- | -------------- |
| 2.7            |   51.7% |        342,250 |
| 3.6            |   21.1% |        139,745 |
| 3.5            |   17.2% |        114,254 |
| 3.4            |    7.6% |         50,584 |
| 3.3            |    1.0% |          6,666 |
| 3.7            |    0.7% |          4,516 |
| 2.6            |    0.7% |          4,451 |
| 3.2            |    0.0% |            138 |
| None           |    0.0% |             13 |
"""

    # Act
    tabulated = core.tabulate(rows)

    # Assert
    assert tabulated == expected


def test_tabulate_markdown():
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = """\
| python_version | percent | download_count |
| -------------- | ------: | -------------: |
| 2.7            |   51.7% |        342,250 |
| 3.6            |   21.1% |        139,745 |
| 3.5            |   17.2% |        114,254 |
| 3.4            |    7.6% |         50,584 |
| 3.3            |    1.0% |          6,666 |
| 3.7            |    0.7% |          4,516 |
| 2.6            |    0.7% |          4,451 |
| 3.2            |    0.0% |            138 |
| None           |    0.0% |             13 |
"""

    # Act
    tabulated = core.tabulate(rows, markdown=True)

    # Assert
    assert tabulated == expected


def test_validate_date_negative_number():
    # Act
    valid = core.validate_date("-1")

    # Assert
    assert valid


def test_validate_date_positive_number():
    # Act / Assert
    with pytest.raises(ValueError):
        core.validate_date("1")


def test_validate_date_valid_yyyy_mm_dd():
    # Act
    valid = core.validate_date("2018-05-15")

    # Assert
    assert valid


def test_validate_date_invalid_yyyy_mm_dd():
    # Act
    with pytest.raises(ValueError):
        core.validate_date("2018-19-39")


def test_validate_date_other_string():
    # Act / Assert
    with pytest.raises(ValueError):
        core.validate_date("somthing invalid")


def test_format_date_negative_number():
    # Arrange
    dummy_format = "dummy format {}"

    # Act
    date = core.format_date("-1", dummy_format)

    # Assert
    assert date == 'DATE_ADD(CURRENT_TIMESTAMP(), -1, "day")'


def test_format_date_yyy_mm_dd():
    # Act
    date = core.format_date("2018-05-15", core.START_TIMESTAMP)

    # Assert
    assert date == 'TIMESTAMP("2018-05-15 00:00:00")'


def test_add_percentages():
    # Arrange
    rows = [
        ['python_version', 'download_count'],
        ['2.7', '480056'],
        ['3.6', '328008'],
        ['3.5', '149663'],
        ['3.4', '36837'],
        ['3.7', '1883'],
        ['2.6', '591'],
        ['3.3', '274'],
        ['3.2', '10'],
        ['None', '9'],
        ['3.8', '2'],
    ]

    expected = [
        ['python_version', 'percent', 'download_count'],
        ['2.7', '48.13%', '480056'],
        ['3.6', '32.89%', '328008'],
        ['3.5', '15.01%', '149663'],
        ['3.4', '3.69%', '36837'],
        ['3.7', '0.19%', '1883'],
        ['2.6', '0.06%', '591'],
        ['3.3', '0.03%', '274'],
        ['3.2', '0.00%', '10'],
        ['None', '0.00%', '9'],
        ['3.8', '0.00%', '2'],
    ]

    # Act
    with_percentages = core.add_percentages(rows)

    # Assert
    assert with_percentages == expected


def test_add_total():
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = copy.deepcopy(ROWS)
    expected.append(["Total", "", "662617"])

    # Act
    rows_with_total = core.add_download_total(rows)

    # Assert
    assert rows_with_total == expected
