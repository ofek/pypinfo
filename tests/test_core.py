from freezegun import freeze_time
import copy
import pytest

from pypinfo import core
from pypinfo.fields import PythonVersion

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


def test_create_config():
    # Act
    config = core.create_config()

    # Assert
    assert not config.use_legacy_sql


def test_normalize_dates_yyy_mm():
    # Arrange
    start_date = "2019-03"
    end_date = "2019-03"

    # Act
    start_date, end_date = core.normalize_dates(start_date, end_date)

    # Assert
    assert start_date == "2019-03-01"
    assert end_date == "2019-03-31"


def test_normalize_dates_yyy_mm_dd_and_negative_integer():
    # Arrange
    start_date = "2019-03-18"
    end_date = -1

    # Act
    start_date, end_date = core.normalize_dates(start_date, end_date)

    # Assert
    assert start_date == "2019-03-18"
    assert end_date == -1


def test_create_client_file_is_none():
    # Act / Assert
    with pytest.raises(SystemError):
        core.create_client(None)


def test_create_client_with_filename():
    # Arrange
    filename = "tests/data/sample-credentials.json"

    # Act
    output = core.create_client(filename)

    # Assert
    assert output.project == "pypinfo-test"


@pytest.mark.parametrize("test_input", ["-1", "2018-05-15"])
def test_validate_date_valid(test_input):
    # Act
    valid = core.validate_date(test_input)

    # Assert
    assert valid


@pytest.mark.parametrize("test_input", ["1", "2018-19-39", "something invalid"])
def test_validate_date_invalid(test_input):
    # Act / Assert
    with pytest.raises(ValueError):
        core.validate_date(test_input)


def test_format_date_negative_number():
    # Arrange
    dummy_format = "dummy format {}"

    # Act
    date = core.format_date("-1", dummy_format)

    # Assert
    assert date == 'TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)'


def test_format_date_yyy_mm_dd():
    # Act
    date = core.format_date("2018-05-15", core.START_TIMESTAMP)

    # Assert
    assert date == 'TIMESTAMP("2018-05-15 00:00:00")'


def test_month_yyyy_mm():
    # Act
    first, last = core.month_ends("2019-03")

    # Assert
    assert first == "2019-03-01"
    assert last == "2019-03-31"


def test_month_yyyy_mm_dd():
    # Act / Assert
    with pytest.raises(ValueError):
        core.month_ends("2019-03-18")


def test_month_negative_integer():
    # Act / Assert
    with pytest.raises(AttributeError):
        core.month_ends(-30)


def test_build_query():
    # Arrange
    # Data from pycodestyle in 2017-10
    # pypinfo -sd 2017-10-01 -ed 2017-10-31 -pc -l 100 --json pycodestyle pyversion
    project = "pycodestyle"
    all_fields = [PythonVersion]
    start_date = "2017-10-01"
    end_date = "2017-10-31"
    days = None
    limit = 100
    where = None
    order = None
    pip = True
    expected = r"""
SELECT
  REGEXP_EXTRACT(details.python, r"^([^\.]+\.[^\.]+)") as python_version,
  COUNT(*) as download_count,
FROM `bigquery-public-data.pypi.file_downloads`
WHERE timestamp BETWEEN TIMESTAMP("2017-10-01 00:00:00") AND TIMESTAMP("2017-10-31 23:59:59")
  AND file.project = "pycodestyle"
  AND details.installer.name = "pip"
GROUP BY
  python_version
ORDER BY
  download_count DESC
LIMIT 100
    """.strip()

    # Act
    output = core.build_query(project, all_fields, start_date, end_date, days, limit, where, order, pip)

    # Assert
    assert output == expected


def test_build_query_days():
    # Arrange
    # Data from pycodestyle in 2017-10
    # pypinfo -sd 2017-10-01 -ed 2017-10-31 -pc -l 100 --json pycodestyle pyversion
    project = "pycodestyle"
    all_fields = [PythonVersion]
    start_date = None
    end_date = None
    days = 10
    limit = 100
    where = None
    order = None
    pip = True
    expected = r"""
SELECT
  REGEXP_EXTRACT(details.python, r"^([^\.]+\.[^\.]+)") as python_version,
  COUNT(*) as download_count,
FROM `bigquery-public-data.pypi.file_downloads`
WHERE timestamp BETWEEN TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -11 DAY) AND TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)
  AND file.project = "pycodestyle"
  AND details.installer.name = "pip"
GROUP BY
  python_version
ORDER BY
  download_count DESC
LIMIT 100
    """.strip()  # noqa: E501

    # Act
    output = core.build_query(project, all_fields, start_date, end_date, days, limit, where, order, pip)

    # Assert
    assert output == expected


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


def test_add_download_total():
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = copy.deepcopy(ROWS)
    expected.append(["Total", "", "662617"])

    # Act
    rows_with_total = core.add_download_total(rows)

    # Assert
    assert rows_with_total == expected


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


@freeze_time("2020-07-14 07:11:49")
def test_format_json():
    # Arrange
    # Data from pycodestyle in 2017-10
    # pypinfo -sd 2017-10-01 -ed 2017-10-31 -pc -l 100 --json pycodestyle pyversion
    rows = [
        ['python_version', 'percent', 'download_count'],
        ['2.7', '0.54', '587705'],
        ['3.6', '0.21', '227800'],
        ['3.5', '0.16', '169851'],
        ['3.4', '0.078', '84599'],
        ['3.3', '0.0091', '9953'],
        ['3.7', '0.0044', '4770'],
        ['2.6', '0.0041', '4476'],
        ['3.2', '0.0003', '326'],
        ['2.8', '3.7e-06', '4'],
        ['None', '2.8e-06', '3'],
    ]
    query_info = {
        'cached': False,
        'bytes_processed': 18087095002,
        'bytes_billed': 18087936000,
        'estimated_cost': '0.09',
    }
    indent = None
    expected = (
        '{"last_update":"2020-07-14 07:11:49",'
        '"query":'
        '{"bytes_billed":18087936000,'
        '"bytes_processed":18087095002,'
        '"cached":false,'
        '"estimated_cost":"0.09"},'
        '"rows":['
        '{"download_count":587705,"percent":"0.54","python_version":"2.7"},'
        '{"download_count":227800,"percent":"0.21","python_version":"3.6"},'
        '{"download_count":169851,"percent":"0.16","python_version":"3.5"},'
        '{"download_count":84599,"percent":"0.078","python_version":"3.4"},'
        '{"download_count":9953,"percent":"0.0091","python_version":"3.3"},'
        '{"download_count":4770,"percent":"0.0044","python_version":"3.7"},'
        '{"download_count":4476,"percent":"0.0041","python_version":"2.6"},'
        '{"download_count":326,"percent":"0.0003","python_version":"3.2"},'
        '{"download_count":4,"percent":"3.7e-06","python_version":"2.8"},'
        '{"download_count":3,"percent":"2.8e-06","python_version":"None"}]}'
    )

    # Act
    output = core.format_json(rows, query_info, indent)

    # Assert
    assert output == expected
