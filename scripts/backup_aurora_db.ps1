<#
.SYNOPSIS
    HealthKicks Ecosystem - Portable Aurora PostgreSQL Backup Script (Windows)

.DESCRIPTION
    Runs on demand from Windows to securely dump the remote Aurora PostgreSQL database.
    Does NOT require a Windows scheduled task or local PostgreSQL installation when using SSH streaming mode.

.EXAMPLE
    .\scripts\backup_aurora_db.ps1
    .\scripts\backup_aurora_db.ps1 -SshKeyPath "C:\path\to\your-key.pem"
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$Ec2Host = "api.healthkicks.eu",

    [Parameter(Mandatory = $false)]
    [string]$SshUser = "ubuntu",

    [Parameter(Mandatory = $false)]
    [string]$SshKeyPath = "",

    [Parameter(Mandatory = $false)]
    [string]$BackupDir = "backups",

    [Parameter(Mandatory = $false)]
    [string]$DbName = "healthkicks",

    [Parameter(Mandatory = $false)]
    [string]$DbUser = "healthkicks"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..")
$TargetDir = Join-Path $ProjectRoot $BackupDir

if (-not (Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    Write-Host "[+] Created backup directory: $TargetDir" -ForegroundColor Cyan
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutputFile = Join-Path $TargetDir "healthkicks_${DbName}_${Timestamp}.dump"

Write-Host "============================================================" -ForegroundColor Green
Write-Host " HealthKicks Aurora Database Backup (On Demand)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Target Host : $Ec2Host" -ForegroundColor Gray
Write-Host "  SSH User    : $SshUser" -ForegroundColor Gray
Write-Host "  Database    : $DbName" -ForegroundColor Gray
Write-Host "  Output File : $OutputFile" -ForegroundColor Gray
Write-Host "------------------------------------------------------------" -ForegroundColor Gray

# Build SSH arguments
$SshArgs = @()
if ($SshKeyPath -and (Test-Path $SshKeyPath)) {
    $SshArgs += "-i"
    $SshArgs += $SshKeyPath
}
$SshArgs += "-o"
$SshArgs += "StrictHostKeyChecking=accept-new"
$SshArgs += "${SshUser}@${Ec2Host}"

# Check if local pg_dump is available; otherwise stream pg_dump from EC2 / Docker
$LocalPgDump = Get-Command "pg_dump" -ErrorAction SilentlyContinue

if ($LocalPgDump) {
    Write-Host "[*] Found local pg_dump at $($LocalPgDump.Source). Checking connection..." -ForegroundColor Yellow
    # Local pg_dump flow (requires either direct network access or active port forwarding)
    Write-Host "[*] Running pg_dump locally..." -ForegroundColor Cyan
    & pg_dump -h $Ec2Host -U $DbUser -d $DbName -Fc -f $OutputFile
} else {
    Write-Host "[*] Streaming pg_dump via SSH from EC2 (zero local PostgreSQL installation required)..." -ForegroundColor Cyan

    # Remote command finds docker container or host pg_dump and exports custom format (-Fc)
    $RemoteCmd = "bash -c 'if [ -f /home/ubuntu/.env ]; then export \$(grep -v \"^#\" /home/ubuntu/.env | xargs); fi; pg_dump -U $DbUser -Fc $DbName'"

    $AllArgs = $SshArgs + @($RemoteCmd)

    $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    $ProcessInfo.FileName = "ssh.exe"
    $ProcessInfo.Arguments = ($AllArgs -join " ")
    $ProcessInfo.RedirectStandardOutput = $true
    $ProcessInfo.RedirectStandardError = $true
    $ProcessInfo.UseShellExecute = $false

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $ProcessInfo

    $FileStream = [System.IO.File]::Create($OutputFile)
    $ErrorOutput = New-Object System.Text.StringBuilder

    try {
        $Process.Start() | Out-Null

        $StdErrTask = [System.Threading.Tasks.Task]::Run([Action]{
            while (-not $Process.StandardError.EndOfStream) {
                $line = $Process.StandardError.ReadLine()
                if ($line) { [void]$ErrorOutput.AppendLine($line) }
            }
        })

        $Process.StandardOutput.BaseStream.CopyTo($FileStream)
        $Process.WaitForExit()
        $StdErrTask.Wait()

        $FileStream.Close()

        if ($Process.ExitCode -ne 0) {
            $ErrMsg = $ErrorOutput.ToString()
            # If host pg_dump failed, try through the backend docker container
            Write-Host "[!] Host command returned code $($Process.ExitCode). Trying via Docker container..." -ForegroundColor Yellow

            $DockerRemoteCmd = "docker exec -i healthkicks-backend bash -c 'pg_dump -U $DbUser -Fc $DbName'"
            $DockerArgs = $SshArgs + @($DockerRemoteCmd)

            $ProcessInfo2 = New-Object System.Diagnostics.ProcessStartInfo
            $ProcessInfo2.FileName = "ssh.exe"
            $ProcessInfo2.Arguments = ($DockerArgs -join " ")
            $ProcessInfo2.RedirectStandardOutput = $true
            $ProcessInfo2.RedirectStandardError = $true
            $ProcessInfo2.UseShellExecute = $false

            $Process2 = New-Object System.Diagnostics.Process
            $Process2.StartInfo = $ProcessInfo2
            $FileStream2 = [System.IO.File]::Create($OutputFile)

            $Process2.Start() | Out-Null
            $Process2.StandardOutput.BaseStream.CopyTo($FileStream2)
            $Process2.WaitForExit()
            $FileStream2.Close()

            if ($Process2.ExitCode -ne 0) {
                $DockerErr = $Process2.StandardError.ReadToEnd()
                if (Test-Path $OutputFile) { Remove-Item $OutputFile -Force }
                throw "Backup failed via both host and Docker.`nHost Error: $ErrMsg`nDocker Error: $DockerErr"
            }
        }
    } finally {
        if ($FileStream) { $FileStream.Dispose() }
    }
}

if ((Test-Path $OutputFile) -and ((Get-Item $OutputFile).Length -gt 0)) {
    $SizeMb = [math]::Round((Get-Item $OutputFile).Length / 1MB, 2)
    Write-Host "[SUCCESS] Backup completed successfully!" -ForegroundColor Green
    Write-Host "  File size: $SizeMb MB" -ForegroundColor Green
    Write-Host "  Location : $OutputFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "To restore this dump into PostgreSQL:" -ForegroundColor Gray
    Write-Host "  pg_restore -h <host> -U <user> -d <db> -c $OutputFile" -ForegroundColor Gray
} else {
    if (Test-Path $OutputFile) { Remove-Item $OutputFile -Force }
    throw "Backup output file was empty or not created."
}
