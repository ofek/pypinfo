from freezegun import freeze_time
from typing import Any
from collections.abc import Iterator
import copy
import pytest
import re

from packaging.specifiers import Specifier
from packaging.version import Version

from google.cloud.bigquery.schema import SchemaField
from google.cloud.bigquery.table import RowIterator

from pypinfo import core
from pypinfo.fields import Field, File, Percent3, PythonVersion

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


def test_create_config() -> None:
    # Act
    config = core.create_config()

    # Assert
    assert not config.dry_run
    assert not config.use_legacy_sql


def test_create_config_dry_run() -> None:
    # Act
    config = core.create_config(dry_run=True)

    # Assert
    assert config.dry_run
    assert not config.use_query_cache


def test_normalize_dates_yyy_mm() -> None:
    # Arrange
    start_date = "2019-03"
    end_date = "2019-03"

    # Act
    start_date, end_date = core.normalize_dates(start_date, end_date)

    # Assert
    assert start_date == "2019-03-01"
    assert end_date == "2019-03-31"


def test_normalize_dates_yyy_mm_dd_and_negative_integer() -> None:
    # Arrange
    start_date = "2019-03-18"
    end_date = "-1"

    # Act
    start_date, end_date = core.normalize_dates(start_date, end_date)

    # Assert
    assert start_date == "2019-03-18"
    assert end_date == "-1"


def test_create_client_file_is_none() -> None:
    # Act / Assert
    with pytest.raises(SystemError):
        core.create_client(None)


def test_create_client_with_filename() -> None:
    # Arrange
    filename = "tests/data/sample-credentials.json"

    # Act
    output = core.create_client(filename)

    # Assert
    assert output.project == "pypinfo-test"


@pytest.mark.parametrize("test_input", ["-1", "2018-05-15"])
def test_validate_date_valid(test_input: str) -> None:
    # Act
    valid = core.validate_date(test_input)

    # Assert
    assert valid


@pytest.mark.parametrize("test_input", ["1", "2018-19-39", "something invalid"])
def test_validate_date_invalid(test_input: str) -> None:
    # Act / Assert
    with pytest.raises(ValueError):
        core.validate_date(test_input)


def test_format_date_negative_number() -> None:
    # Arrange
    dummy_format = "dummy format {}"

    # Act
    date = core.format_date("-1", dummy_format)

    # Assert
    assert date == 'TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)'


def test_format_date_yyy_mm_dd() -> None:
    # Act
    date = core.format_date("2018-05-15", core.START_TIMESTAMP)

    # Assert
    assert date == 'TIMESTAMP("2018-05-15 00:00:00")'


def test_month_yyyy_mm() -> None:
    # Act
    first, last = core.month_ends("2019-03")

    # Assert
    assert first == "2019-03-01"
    assert last == "2019-03-31"


def test_month_yyyy_mm_dd() -> None:
    # Act / Assert
    with pytest.raises(ValueError):
        core.month_ends("2019-03-18")


def test_month_negative_integer() -> None:
    # Act / Assert
    with pytest.raises(ValueError):
        core.month_ends("-30")


def test_build_query() -> None:
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


def test_build_query_specifier() -> None:
    # pypinfo -sd -2 -ed -1 -l 20  --test 'foo==1'
    project = "foo==1"
    all_fields: list[Field] = []
    start_date = "-2"
    end_date = "-1"
    days = None
    limit = 20
    where = None
    order = None
    pip = True
    expected = r"""
SELECT
  COUNT(*) as download_count,
FROM `bigquery-public-data.pypi.file_downloads`
WHERE timestamp BETWEEN TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -2 DAY) AND TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)
  AND file.project = "foo"
  AND REGEXP_CONTAINS(file.version, r"(?i)^(0+!)?0*1(\.0+)*$")
  AND details.installer.name = "pip"
ORDER BY
  download_count DESC
LIMIT 20
        """.strip()  # noqa: E501

    # Act
    output = core.build_query(project, all_fields, start_date, end_date, days, limit, where, order, pip)

    # Assert
    assert output == expected


def test_build_query_days() -> None:
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


def test_build_query_where() -> None:
    # Arrange
    # pypinfo -sd -2 -ed -1 --test --where 'file.filename LIKE "%manylinux%"' numpy file
    project = "numpy"
    all_fields = [File]
    start_date = "-2"
    end_date = "-1"
    days = None
    limit = 10
    where = 'file.filename LIKE "%manylinux%"'
    order = None
    pip = True
    expected = r"""
SELECT
  file.filename as file,
  COUNT(*) as download_count,
FROM `bigquery-public-data.pypi.file_downloads`
WHERE timestamp BETWEEN TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -2 DAY) AND TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)
  AND file.project = "numpy"
  AND details.installer.name = "pip"
  AND file.filename LIKE "%manylinux%"
GROUP BY
  file
ORDER BY
  download_count DESC
LIMIT 10
    """.strip()  # noqa: E501

    # Act
    output = core.build_query(project, all_fields, start_date, end_date, days, limit, where, order, pip)

    # Assert
    assert output == expected


def test_build_query_no_project() -> None:
    # pypinfo -sd -2 -ed -1 -l 20 --all --test ''
    project = ""
    all_fields: list[Field] = []
    start_date = "-2"
    end_date = "-1"
    days = None
    limit = 20
    where = None
    order = None
    pip = False
    expected = r"""
SELECT
  COUNT(*) as download_count,
FROM `bigquery-public-data.pypi.file_downloads`
WHERE timestamp BETWEEN TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -2 DAY) AND TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)
ORDER BY
  download_count DESC
LIMIT 20
        """.strip()  # noqa: E501

    # Act
    output = core.build_query(project, all_fields, start_date, end_date, days, limit, where, order, pip)

    # Assert
    assert output == expected


def test_build_query_only_aggregate() -> None:
    # pypinfo -sd -2 -ed -1 -l 20 numpy percent3
    project = "numpy"
    all_fields = [Percent3]
    start_date = "-2"
    end_date = "-1"
    days = None
    limit = 20
    where = None
    order = None
    pip = True
    expected = r"""
SELECT
  ROUND(100 * SUM(CASE WHEN REGEXP_EXTRACT(details.python, r"^([^\.]+)") = "3" THEN 1 ELSE 0 END) / COUNT(*), 1) as percent_3,
  COUNT(*) as download_count,
FROM `bigquery-public-data.pypi.file_downloads`
WHERE timestamp BETWEEN TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -2 DAY) AND TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL -1 DAY)
  AND file.project = "numpy"
  AND details.installer.name = "pip"
ORDER BY
  download_count DESC
LIMIT 20
        """.strip()  # noqa: E501

    # Act
    output = core.build_query(project, all_fields, start_date, end_date, days, limit, where, order, pip)

    # Assert
    assert output == expected


def test_build_query_bad_end_date() -> None:
    # Arrange
    project = "pycodestyle"
    all_fields = [PythonVersion]
    # End date is before start date
    start_date = "-1"
    end_date = "-100"

    # Act / Assert
    with pytest.raises(ValueError):
        core.build_query(project, all_fields, start_date, end_date)


def test_build_query_bad_project_extras() -> None:
    with pytest.raises(ValueError, match=".*extras.*"):
        core.build_query('foo[bar]', [])


def test_build_query_bad_project_url() -> None:
    with pytest.raises(ValueError, match=".*url.*"):
        core.build_query('foo@https://foo.bar/', [])


def test_build_query_bad_project_marker() -> None:
    with pytest.raises(ValueError, match=".*marker.*"):
        core.build_query('foo ; sys_platform == "win32"', [])


def test_add_percentages() -> None:
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


def test_add_download_total() -> None:
    # Arrange
    rows = copy.deepcopy(ROWS)
    expected = copy.deepcopy(ROWS)
    expected.append(["Total", "", "662617"])

    # Act
    rows_with_total = core.add_download_total(rows)

    # Assert
    assert rows_with_total == expected


def test_tabulate_default() -> None:
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


def test_tabulate_markdown() -> None:
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
def test_format_json() -> None:
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


def test_parse_query_result() -> None:
    data: list[tuple[Any, ...]] = [
        ("name", "other"),
        ("name1", 1),
        ("name2", 2),
    ]
    expected = [[str(cell) for cell in row] for row in data]
    schema = (
        SchemaField(data[0][0], "STRING"),
        SchemaField(data[0][1], "INTEGER"),
    )

    class MockRowIterator(RowIterator):  # type: ignore[misc]
        def __init__(self) -> None:
            super().__init__(None, None, None, schema)

        def __iter__(self) -> Iterator[tuple[Any, ...]]:
            return iter(data[1:])

    actual = core.parse_query_result(MockRowIterator())
    assert actual == expected


SPECIFIER_GOOD = {
    '==1!2.3.4': r'(?i)^0*1!0*2\.0*3\.0*4(\.0+)*$',
    '==1.0.0': r'(?i)^(0+!)?0*1(\.0+)*$',
    '==1-pre_post.dev': r'(?i)^(0+!)?0*1(\.0+)*[-_\.]?(c|rc|pre|preview)([-_\.]?0+)?(-0*0|[-_\.]?(post|rev|r)([-_\.]?0+)?)[-_\.]?dev([-_\.]?0+)?$',  # noqa: E501
    '==0a1-1.dev2': r'(?i)^(0+!)?0*0(\.0+)*[-_\.]?(a|alpha)[-_\.]?0*1(-0*1|[-_\.]?(post|rev|r)[-_\.]?0*1)[-_\.]?dev[-_\.]?0*2$',  # noqa: E501
    '==1.1.*': r'(?i)^(0+!)?(0*1\.0*1(\.0+)*|0*1\.0*1(\.[0-9]+)*)([-_\.]?(a|b|c|rc|alpha|beta|pre|preview)[-_\.]?[0-9]+?)?(-[0-9]+|([-_\.]?(post|rev|r)[-_\.]?[0-9]+?))?([-_\.]?dev[-_\.]?[0-9]+?)?$',  # noqa: E501
}


@pytest.mark.parametrize('specifier', SPECIFIER_GOOD.keys())
def test_specifier_good(specifier: str) -> None:
    actual = core.version_specifier_condition(Specifier(specifier)).strip()
    regex = SPECIFIER_GOOD[specifier]
    expected = f'REGEXP_CONTAINS(file.version, r"{regex}")'
    assert actual == expected


@pytest.mark.parametrize(
    'specifier, version',
    (
        ('==1!2.3.4', '1!2.3.4'),
        ('==1!2.3.4', '1!2.3.4.0'),
        ('==1!2.3.4', '01!02.03.04.00'),
        ('==1.0.0', '1.0.0'),
        ('==1.0.0', '1'),
        ('==1.0.0', '0!1.0'),
        ('==1.0.0', '00!01.00'),
        ('==1-pre_post.dev', '1-pre_post.dev'),
        ('==1-pre_post.dev', '1.0.0Rc0.poSt.0.dEv-0'),
        ('==1-pre_post.dev', '1.0.0_C00-Rev00_dEv.00'),
        ('==1-pre_post.dev', '1.0.0prevIew0-0-dEv00'),
        ('==1-pre_post.dev', '1.0.0prevIewR0dEv'),
        ('==1-pre_post.dev', '1.0.0rcRdEv'),
        ('==0a1-1.dev2', '0a1-1.dev2'),
        ('==0a1-1.dev2', '0.0.alpha.1.post.1.dev.2'),
        ('==0a1-1.dev2', '00!00.00.alpha.01.post.01.dev.02'),
        ('==1.1.*', '1.1'),
        ('==1.1.*', '1.1a1'),
        ('==1.1.*', '01.01.00.01.post01'),
        ('==1.1.*', '1.1.1.1.0.dev1'),
    ),
)
def test_specifier_regex_match(specifier: str, version: str) -> None:
    specifier_ = Specifier(specifier)
    version_ = Version(version)
    assert specifier_.contains(version_, prereleases=True)
    assert re.match(SPECIFIER_GOOD[specifier], str(version_))
    assert re.match(SPECIFIER_GOOD[specifier], version)


@pytest.mark.parametrize(
    'specifier, version',
    (
        ('==1!2.3.4', '1!2.3'),
        ('==1!2.3.4', '2.3.4'),
        ('==1!2.3.4', '1!2.3.4.post1'),
        ('==1!2.3.4', '1!2.3.4rc1'),
        ('==1!2.3.4', '1!2.3.4dev'),
        ('==1.0.0', '1.1'),
        ('==1.0.0', '1!1'),
        ('==1.0.0', '2'),
        ('==1.0.0', '1rc1'),
        ('==1-pre_post.dev', '1-pre1_post.dev'),
        ('==1-pre_post.dev', '1.0.0Rc0.poSt.1.dEv-0'),
        ('==1-pre_post.dev', '1.0.0_C00-Rev00_dEv.10'),
        ('==1-pre_post.dev', '1.0.0prevIew0-1-dEv00'),
        ('==1-pre_post.dev', '1.0.1prevIewR0dEv'),
        ('==1-pre_post.dev', '1!1.0.0rcRdEv'),
        ('==0a1-1.dev2', '0a1-1.dev3'),
        ('==0a1-1.dev2', '0.1.alpha.1.post.1.dev.2'),
        ('==0a1-1.dev2', '0!1.00.alpha.01.post.01.dev.02'),
        ('==1.1.*', '1.2'),
        ('==1.1.*', '1.0'),
        ('==1.1.*', '1!1.1'),
        ('==1.1.*', '2'),
    ),
)
def test_specifier_regex_no_match(specifier: str, version: str) -> None:
    specifier_ = Specifier(specifier)
    version_ = Version(version)
    assert not specifier_.contains(version_, prereleases=True)
    assert re.match(SPECIFIER_GOOD[specifier], str(Version(version))) is None
    assert re.match(SPECIFIER_GOOD[specifier], version) is None


@pytest.mark.parametrize('specifier', ['~=1.0', '!=1', '<=1', '>=1', '<1', '>1', '===1'])
def test_specifier_unsupported(specifier: str) -> None:
    with pytest.raises(ValueError, match=r'.*operator not supported:.*'):
        core.version_specifier_condition(Specifier(specifier))
