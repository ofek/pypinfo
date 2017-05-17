from collections import namedtuple

Field = namedtuple('Field', ('name', 'data'))
Downloads = Field('download_count', 'COUNT(*)')
Date = Field('download_date', 'STRFTIME_UTC_USEC(timestamp, "%Y-%m-%d")')
PythonVersion = Field('python_version', 'REGEXP_EXTRACT(details.python, r"^([^\.]+\.[^\.]+)")')
Installer = Field('installer_name', 'details.installer.name')
InstallerVersion = Field('installer_version', 'details.installer.version')
