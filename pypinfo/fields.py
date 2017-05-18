from collections import namedtuple

Field = namedtuple('Field', ('name', 'data'))
Downloads = Field('download_count', 'COUNT(*)')
Date = Field('download_date', 'STRFTIME_UTC_USEC(timestamp, "%Y-%m-%d")')
Month = Field('download_month', 'STRFTIME_UTC_USEC(timestamp, "%Y-%m")')
Year = Field('download_year', 'STRFTIME_UTC_USEC(timestamp, "%Y")')
Country = Field('country', 'country_code')
Project = Field('project', 'file.project')
Version = Field('version', 'file.version')
PythonVersion = Field('python_version', 'REGEXP_EXTRACT(details.python, r"^([^\.]+\.[^\.]+)")')
Percent3 = Field(
    'percent_3',
    'ROUND(100 * SUM(CASE WHEN REGEXP_EXTRACT(details.python, r"^([^\.]+)") = "3" THEN 1 ELSE 0 END) / COUNT(*), 1)'
)
Percent2 = Field(
    'percent_2',
    'ROUND(100 * SUM(CASE WHEN REGEXP_EXTRACT(details.python, r"^([^\.]+)") = "2" THEN 1 ELSE 0 END) / COUNT(*), 1)'
)
Implementation = Field('implementation', 'details.implementation.name')
ImplementationVersion = Field('impl_version', 'REGEXP_EXTRACT(details.implementation.version, r"^([^\.]+\.[^\.]+)")')
OpenSSLVersion = Field('openssl_version', 'REGEXP_EXTRACT(details.openssl_version, r"^OpenSSL ([^ ]+) ")')
Installer = Field('installer_name', 'details.installer.name')
InstallerVersion = Field('installer_version', 'details.installer.version')
SetuptoolsVersion = Field('setuptools_version', 'details.setuptools_version')
System = Field('system_name', 'details.system.name')
SystemRelease = Field('system_release', 'details.system.release')
Distro = Field('distro_name', 'details.distro.name')
DistroVersion = Field('distro_version', 'details.distro.version')
CPU = Field('cpu', 'details.cpu')

AGGREGATES = {Percent3, Percent2}
