# . bin/activate.ps1

if ($MyInvocation.InvocationName -ne ".")
{{
    Write-Host "Warning: running as a regular script will not work." -ForegroundColor DarkYellow
    Write-Host
    Write-Host "In order to activate this enviroment, 'dot-source' the file:" -ForegroundColor Green
    Write-Host
    Write-Host "  '. $($MyInvocation.MyCommand.Definition)'"
    Write-Host
    Write-Host "Please try again." -ForegroundColor Green
    Exit 1
}}

# store old JANET_PATH, if it exists
if (-not ([string]::IsNullOrEmpty($env:JANET_PATH))) {{
  $global:_OLD_JANET_PATH=$env:JANET_PATH
  Remove-Item env:JANET_PATH
}}

# store old JANET_PREFIX, if it exists
if (-not ([string]::IsNullOrEmpty($env:JANET_PREFIX))) {{
  $global:_OLD_JANET_PREFIX=$env:JANET_PREFIX
  Remove-Item env:JANET_PREFIX
}}

# store old JANET_BINPATH, if it exists
if (-not ([string]::IsNullOrEmpty($env:JANET_BINPATH))) {{
  $global:_OLD_JANET_BINPATH=$env:JANET_BINPATH
  Remove-Item env:JANET_BINPATH
}}

# store old JANET_HEADERPATH, if it exists
if (-not ([string]::IsNullOrEmpty($env:JANET_HEADERPATH))) {{
  $global:_OLD_JANET_HEADERPATH=$env:JANET_HEADERPATH
  Remove-Item env:JANET_HEADERPATH
}}

# store old JANET_LIBPATH, if it exists
if (-not ([string]::IsNullOrEmpty($env:JANET_LIBPATH))) {{
  $global:_OLD_JANET_LIBPATH=$env:JANET_LIBPATH
  Remove-Item env:JANET_LIBPATH
}}

# store old JANET_MANPATH, if it exists
if (-not ([string]::IsNullOrEmpty($env:JANET_MANPATH))) {{
  $global:_OLD_JANET_MANPATH=$env:JANET_MANPATH
  Remove-Item env:JANET_MANPATH
}}

# store old JANET_BUILD_TYPE, if it exists
if (-not ([string]::IsNullOrEmpty($env:JANET_BUILD_TYPE))) {{
  $global:_OLD_JANET_BUILD_TYPE=$env:JANET_BUILD_TYPE
  Remove-Item env:JANET_BUILD_TYPE
}}

# inside, we only set these
$env:JANET_VIRTUAL_ENV="{venv_name}"
$env:JANET_PREFIX="{venv_dir}"
$env:JANET_PATH="{venv_dir}\Library"
$env:JANET_BUILD_TYPE="{build_type}"

# store old PATH
$global:_OLD_PATH=$env:PATH
$env:PATH=$env:JANET_PREFIX + "\Library\bin;" + $env:PATH
$env:PATH=$env:JANET_PREFIX + "\bin;" + $env:PATH

$function:old_prompt = $function:prompt

function global:prompt {{
  Write-Host "({venv_name}) " -NoNewline
  & $function:old_prompt
}}

function unload_janet {{
  # restore PATH
  $env:PATH=$global:_OLD_PATH
  Remove-Variable -Name _OLD_PATH -Scope Global

  # restore old JANET_PATH, if it exists
  Remove-Item env:\JANET_PATH
  if ((Test-Path variable:global:_OLD_JANET_PATH) -and -not ([string]::IsNullOrEmpty($global:_OLD_JANET_PATH))) {{
    $env:JANET_PATH=$global:_OLD_JANET_PATH
    Remove-Variable -Name _OLD_JANET_PATH -Scope Global
  }}

  # restore old JANET_PREFIX, if it exists
  Remove-Item env:\JANET_PREFIX
  if ((Test-Path variable:global:_OLD_JANET_PREFIX) -and -not ([string]::IsNullOrEmpty($global:_OLD_JANET_PREFIX))) {{
    $env:JANET_PREFIX=$global:_OLD_JANET_PREFIX
    Remove-Variable -Name _OLD_JANET_PREFIX -Scope Global
  }}

  # restore old JANET_BINPATH, if it exists
  if ((Test-Path variable:global:_OLD_JANET_BINPATH) -and -not ([string]::IsNullOrEmpty($global:_OLD_JANET_BINPATH))) {{
    $env:JANET_BINPATH=$global:_OLD_JANET_BINPATH
    Remove-Variable -Name _OLD_JANET_BINPATH -Scope Global
  }}

  # restore old JANET_HEADERPATH, if it exists
  if ((Test-Path variable:global:_OLD_JANET_HEADERPATH) -and -not ([string]::IsNullOrEmpty($global:_OLD_JANET_HEADERPATH))) {{
    $env:JANET_HEADERPATH=$global:_OLD_JANET_HEADERPATH
    Remove-Variable -Name _OLD_JANET_HEADERPATH -Scope Global
  }}

  # restore old JANET_LIBPATH, if it exists
  if ((Test-Path variable:global:_OLD_JANET_LIBPATH) -and -not ([string]::IsNullOrEmpty($global:_OLD_JANET_LIBPATH))) {{
    $env:JANET_LIBPATH=$global:_OLD_JANET_LIBPATH
    Remove-Variable -Name _OLD_JANET_LIBPATH -Scope Global
  }}

  # restore old JANET_MANPATH, if it exists
  if ((Test-Path variable:global:_OLD_JANET_MANPATH) -and -not ([string]::IsNullOrEmpty($global:_OLD_JANET_MANPATH))) {{
    $env:JANET_MANPATH=$global:_OLD_JANET_MANPATH
    Remove-Variable -Name _OLD_JANET_MANPATH -Scope Global
  }}

  # restore old JANET_BUILD_TYPE, if it exists
  if ((Test-Path variable:global:_OLD_JANET_BUILD_TYPE) -and -not ([string]::IsNullOrEmpty($global:_OLD_JANET_BUILD_TYPE))) {{
    $env:JANET_BUILD_TYPE=$global:_OLD_JANET_BUILD_TYPE
    Remove-Variable -Name _OLD_JANET_BUILD_TYPE -Scope Global
  }}

  Remove-Item env:\JANET_VIRTUAL_ENV

  Remove-Item function:\unload_janet
  $function:prompt = $function:old_prompt
  Remove-Item function:\old_prompt
}}