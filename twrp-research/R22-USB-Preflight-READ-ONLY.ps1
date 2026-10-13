#Requires -Version 5.1
<#
.SYNOPSIS
    Read-only preflight for Xoom TWRP R22 testing.
.DESCRIPTION
    Checks the local candidate image and USB ADB recovery connection.
    Does NOT flash, reboot, remount, edit settings, or transmit credentials.
#>
[CmdletBinding()]
param(
    [string]$Serial,
    [string]$CandidateImage
)
$ErrorActionPreference = 'Stop'
$expectedR22 = 'c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622'
$expectedR21 = 'ef587efbaf41440c270efb2ba0950eb79f868f93d83d3c82b42c762e7017298d'
function Call-Adb([string[]]$Arguments) {
    $out = & adb @Arguments 2>&1
    $code = $LASTEXITCODE
    if ($code -ne 0) { throw "adb failed (exit $code): $($Arguments -join ' '); $out" }
    return $out
}
$adb = Get-Command adb -ErrorAction Stop
Write-Host "ADB executable: $($adb.Source)"
& adb version | Select-Object -First 2
if ($CandidateImage) {
    $resolved = (Resolve-Path -LiteralPath $CandidateImage).Path
    $item = Get-Item -LiteralPath $resolved
    if ($item.Length -ne 11376640) { throw "Unexpected R22 image size: $($item.Length)" }
    $actualHash = (Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $expectedR22) { throw "R22 IMAGE HASH MISMATCH: $actualHash" }
    Write-Host "R22 image VERIFIED: $resolved ($($item.Length) bytes)" -ForegroundColor Green
} else {
    Write-Host 'No local candidate path supplied. Image verification skipped.'
}
$devices = @(& adb devices -l)
if ($LASTEXITCODE -ne 0) { throw 'adb devices failed' }
Write-Host 'USB ADB device list:'
$devices | ForEach-Object { Write-Host $_ }
$connected = @($devices | Where-Object { $_ -match '^([^\s]+)\s+(device|recovery)\b' } |
    ForEach-Object { [regex]::Match($_, '^([^\s]+)').Groups[1].Value })
if (-not $Serial) {
    if ($connected.Count -ne 1) {
        Write-Host 'Specify -Serial if more than one device is connected, or wake/reconnect the Xoom.'
        return
    }
    $Serial = $connected[0]
}
if ($connected -notcontains $Serial) {
    Write-Host "Requested device '$Serial' is not ADB-ready. No changes made."
    return
}
Write-Host "Inspecting device $Serial (READ ONLY)"
$state = (Call-Adb -Arguments @('-s',$Serial,'get-state') | Select-Object -First 1).ToString().Trim()
Write-Host "ADB state: $state"
if ($state -notin @('recovery','device')) {
    Write-Host 'Not a normal running ADB state; stop here.'
    return
}
foreach ($prop in @('ro.product.device','ro.product.model','ro.bootmode','ro.twrp.version')) {
    $value = Call-Adb -Arguments @('-s',$Serial,'shell',"getprop $prop")
    Write-Host "$prop : $($value -join ' ')"
}
$recoveryLink = Call-Adb -Arguments @('-s',$Serial,'shell',
    '/sbin/busybox ls -l /dev/block/platform/sdhci-tegra.3/by-name/recovery')
Write-Host 'Recovery partition link (inspect before any flash):'
$recoveryLink | ForEach-Object { Write-Host $_ }
Write-Host "Expected installed R21 IMAGE SHA256: $expectedR21"
Write-Host "Expected candidate R22 IMAGE SHA256: $expectedR22"
Write-Host 'PREFLIGHT COMPLETE (READ ONLY). No flash/reboot performed.' -ForegroundColor Green
