from collections import namedtuple

Field = namedtuple('Field', ('name', 'data'))
Downloads = Field('download_count', 'COUNT(*)')
Date = Field('download_date', 'STRFTIME_UTC_USEC(timestamp, "%Y-%m-%d")')
Version = Field('version', 'file.version')
PythonVersion = Field('python_version', 'REGEXP_EXTRACT(details.python, r"^([^\.]+\.[^\.]+)")')
Installer = Field('installer_name', 'details.installer.name')
InstallerVersion = Field('installer_version', 'details.installer.version')
System = Field('system_name', 'details.system.name')
SystemRelease = Field('system_release', 'details.system.release')
