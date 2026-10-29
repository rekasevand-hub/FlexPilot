<#
.SYNOPSIS
  以 UTF-8（无 BOM）编码写入文件。

.DESCRIPTION
  避免 PowerShell 管道（@'...'@ | python -）把中文按 GBK 传给 Python 导致中文变成 ?。
  本脚本在 PowerShell 进程内直接用 .NET 写入 UTF-8 无 BOM 文件，中文不会丢失。

.EXAMPLE
  $content = @'
  class Test { // 中文注释
      def hello() { return "你好"; }
  }
  '@
  & .codex/skills/flexpilot/scripts\write_utf8.ps1 -Path src/xxx/Test.groovy -Content $content
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Path,
    [Parameter(Mandatory = $true)]
    [AllowEmptyString()]
    [string]$Content
)

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$fullPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
$dir = Split-Path -Parent $fullPath
if ($dir -and -not (Test-Path -LiteralPath $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}
[System.IO.File]::WriteAllText($fullPath, $Content, $utf8NoBom)
Write-Host "written (UTF-8 no BOM): $fullPath"