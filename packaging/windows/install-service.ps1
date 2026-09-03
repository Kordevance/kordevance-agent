$ErrorActionPreference = "Stop"

$ServiceName = "KordevanceGateway"
$InstallDir = "$env:ProgramFiles\Kordevance"
$ExePath = "$InstallDir\kordevance-gateway.exe"
$LogDir = "$env:ProgramData\Kordevance\logs"
$NssmPath = "$PSScriptRoot\nssm.exe"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

& $NssmPath install $ServiceName $ExePath
& $NssmPath set $ServiceName AppDirectory $InstallDir
& $NssmPath set $ServiceName Start SERVICE_AUTO_START
& $NssmPath set $ServiceName AppStdout "$LogDir\kordevance-gateway.log"
& $NssmPath set $ServiceName AppStderr "$LogDir\kordevance-gateway.err.log"
& $NssmPath set $ServiceName AppRotateFiles 1

Start-Service $ServiceName
