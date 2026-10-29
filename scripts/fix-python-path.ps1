# Fix python command: move conda paths to the front of User PATH (before the WindowsApps Store stub)
$backup = [Environment]::GetEnvironmentVariable('Path', 'User')
Set-Content -Path "$PSScriptRoot\.path-backup.txt" -Value $backup -Encoding UTF8
Write-Host "Backup saved to scripts\.path-backup.txt"

$new = @(
    'D:\LLM_condas',
    'D:\LLM_condas\Scripts',
    'D:\LLM_condas\Library\bin',
    'C:\Users\lzq\.kimi-code\bin',
    'C:\Users\lzq\AppData\Local\Microsoft\WindowsApps',
    'D:\Development\IntelliJ IDEA 2025.1.1.1\bin',
    'D:\Development\Microsoft VS Code\bin',
    'C:\Users\lzq\AppData\Local\Programs\Ollama',
    'C:\Users\lzq\AppData\Roaming\npm'
) -join ';'
[Environment]::SetEnvironmentVariable('Path', $new, 'User')
Write-Host "User PATH updated."

# Broadcast environment change so new processes pick it up
$sig = '[DllImport("user32.dll", SetLastError=true)] public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);'
Add-Type -Namespace Win32 -Name NativeMethods -MemberDefinition $sig
$r = [UIntPtr]::Zero
[Win32.NativeMethods]::SendMessageTimeout([IntPtr]0xffff, 0x1A, [UIntPtr]::Zero, 'Environment', 2, 5000, [ref]$r) | Out-Null
Write-Host "Environment change broadcasted."

# Verify using the fresh Machine+User PATH from registry (simulates a new process)
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
Write-Host ""
Write-Host "Verification:"
python --version
where.exe python
