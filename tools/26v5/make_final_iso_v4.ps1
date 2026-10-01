# Canonical Windows ISO builder v4
# Successfully used for the 2026-10-01 SettingsSave FINAL ISO.
# PowerShell variable names are case-insensitive, so all *Name and *Path variables are distinct.

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$SourceDir = 'D:\SoNG-HoME_Admin\SoNG_Admin\Downloads\EDv9_26v5_KO_CLEAN_FINAL'
$OutputDir = 'D:\SoNG-HoME_Admin\SoNG_Admin\Downloads'
$FinalExeName = 'EDv9_x64_KO_CLEAN.exe'
$DatName = 'EDv9_v9.0.2609.20009.dat'
$IniName = 'EDv9_x64.ini'
$DriversName = 'Drivers'
$IsoName = 'EDv9_26v5_KO_CLEAN_FINAL.iso'
$VolumeLabel = 'EDv9_26v5_KO'

$ExpectedSha = @{
 FinalExe = '12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA'
 Dat = 'A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D'
 Ini = '608E193A2B03A13C4F657F89A15B43CC40437906901DF8623B21FBA18775CCF2'
 Version = '3C6923B48808D1B04B1280B447B7053F5CC8987EDCF1714B0FA1C83F422B633F'
 Oscdimg = '801D8BC3FFA4C15B1740C3FAE78612243315F35ED0683E28C22570A6F5A251A9'
}
function Get-Sha256([string]$Path){(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()}
function Assert-True($Condition,[string]$Message){if(-not $Condition){throw $Message}}
function Find-Oscdimg {
 $Candidates=@(
  'D:\etc_Util_All\Oscdimg\oscdimg.exe',
  (Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe'),
  (Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\x86\Oscdimg\oscdimg.exe')
 )
 foreach($Candidate in $Candidates){if($Candidate -and (Test-Path -LiteralPath $Candidate -PathType Leaf)){return $Candidate}}
 try{return (Get-Command oscdimg.exe -ErrorAction Stop).Source}catch{}
 if(Test-Path -LiteralPath 'D:\etc_Util_All'){
  $Found=Get-ChildItem -LiteralPath 'D:\etc_Util_All' -Filter 'oscdimg.exe' -File -Recurse -ErrorAction SilentlyContinue|Select-Object -First 1
  if($Found){return $Found.FullName}
 }
 return $null
}

Assert-True (Test-Path -LiteralPath $SourceDir -PathType Container) 'Source folder not found.'
$FinalExePath=Join-Path $SourceDir $FinalExeName
$DatPath=Join-Path $SourceDir $DatName
$IniPath=Join-Path $SourceDir $IniName
$DriversPath=Join-Path $SourceDir $DriversName
$VersionPath=Join-Path $DriversPath '@version'

Assert-True ((Get-Sha256 $FinalExePath)-eq $ExpectedSha.FinalExe) 'FINAL EXE SHA-256 mismatch.'
Assert-True ((Get-Sha256 $DatPath)-eq $ExpectedSha.Dat) 'DAT SHA-256 mismatch.'
Assert-True ((Get-Sha256 $IniPath)-eq $ExpectedSha.Ini) 'INI SHA-256 mismatch.'
Assert-True ((Get-Sha256 $VersionPath)-eq $ExpectedSha.Version) 'Drivers/@version SHA-256 mismatch.'

$AllowedTopNames=@('EDv9_x64_KO_CLEAN.exe','EDv9_v9.0.2609.20009.dat','EDv9_x64.ini','Drivers')
$UnexpectedTop=@(Get-ChildItem -LiteralPath $SourceDir -Force|Where-Object{$AllowedTopNames -notcontains $_.Name})
Assert-True ($UnexpectedTop.Count -eq 0) ('Unexpected source-root items: '+(($UnexpectedTop|% Name)-join ', '))
Assert-True (@(Get-ChildItem -LiteralPath $DriversPath -Filter '*.exe' -File -Recurse -Force).Count -eq 0) 'Unexpected EXE under Drivers.'
Assert-True (@(Get-ChildItem -LiteralPath $SourceDir -Recurse -Force|?{$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count -eq 0) 'ReparsePoint in source.'

$SourceFiles=@(Get-ChildItem -LiteralPath $SourceDir -File -Recurse -Force)
$SourceFileCount=$SourceFiles.Count
[Int64]$SourceBytes=($SourceFiles|Measure-Object Length -Sum).Sum

$OscdimgPath=Find-Oscdimg
Assert-True ($null -ne $OscdimgPath) 'oscdimg.exe not found.'
Assert-True ((Get-Sha256 $OscdimgPath)-eq $ExpectedSha.Oscdimg) 'OSCDIMG SHA-256 mismatch.'

$FinalIsoPath=Join-Path $OutputDir $IsoName
$TempIsoPath=Join-Path $OutputDir 'EDv9_26v5_KO_CLEAN_FINAL.__building__.iso'
$ShaFilePath=Join-Path $OutputDir 'EDv9_26v5_KO_CLEAN_FINAL.sha256.txt'
$ReportPath=Join-Path $OutputDir 'EDv9_26v5_KO_CLEAN_FINAL.ISO_BUILD_REPORT.txt'
if(Test-Path -LiteralPath $TempIsoPath){Remove-Item -LiteralPath $TempIsoPath -Force}

try {
 & $OscdimgPath '-m' '-o' '-h' '-u2' '-udfver102' ('-l'+$VolumeLabel) $SourceDir $TempIsoPath
 Assert-True ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $TempIsoPath -PathType Leaf)) 'ISO build failed.'
 $Mounted=$false
 try {
  Mount-DiskImage -ImagePath $TempIsoPath -StorageType ISO -PassThru|Out-Null;$Mounted=$true
  $Volume=$null
  for($i=0;$i-lt 40;$i++){Start-Sleep -Milliseconds 500;$Volume=Get-DiskImage -ImagePath $TempIsoPath|Get-Volume -EA SilentlyContinue|? DriveLetter|select -First 1;if($Volume){break}}
  Assert-True ($null -ne $Volume) 'Mounted ISO volume not found.'
  $IsoRoot=$Volume.DriveLetter+':\'
  $IsoUnexpected=@(Get-ChildItem -LiteralPath $IsoRoot -Force|?{$AllowedTopNames -notcontains $_.Name})
  Assert-True ($IsoUnexpected.Count -eq 0) 'Unexpected ISO-root item.'
  Assert-True (-not(Test-Path -LiteralPath (Join-Path $IsoRoot 'EDv9_x64.exe'))) 'Original EXE found in ISO.'
  $IsoExes=@(Get-ChildItem -LiteralPath $IsoRoot -Filter '*.exe' -File -Recurse -Force)
  Assert-True ($IsoExes.Count -eq 1 -and $IsoExes[0].Name -eq $FinalExeName) 'ISO EXE policy failed.'
  Assert-True ((Get-Sha256 (Join-Path $IsoRoot $FinalExeName))-eq $ExpectedSha.FinalExe) 'ISO FINAL EXE mismatch.'
  Assert-True ((Get-Sha256 (Join-Path $IsoRoot $DatName))-eq $ExpectedSha.Dat) 'ISO DAT mismatch.'
  Assert-True ((Get-Sha256 (Join-Path $IsoRoot $IniName))-eq $ExpectedSha.Ini) 'ISO INI mismatch.'
  Assert-True ((Get-Sha256 (Join-Path $IsoRoot 'Drivers\@version'))-eq $ExpectedSha.Version) 'ISO @version mismatch.'
  $IsoFiles=@(Get-ChildItem -LiteralPath $IsoRoot -File -Recurse -Force)
  [Int64]$IsoBytes=($IsoFiles|Measure-Object Length -Sum).Sum
  Assert-True ($IsoFiles.Count -eq $SourceFileCount -and $IsoBytes -eq $SourceBytes) 'ISO payload count/bytes mismatch.'
 } finally {if($Mounted){Dismount-DiskImage -ImagePath $TempIsoPath -EA SilentlyContinue|Out-Null}}

 if(Test-Path -LiteralPath $FinalIsoPath){$Stamp=Get-Date -Format 'yyyyMMdd_HHmmss';Move-Item -LiteralPath $FinalIsoPath -Destination (Join-Path $OutputDir ('EDv9_26v5_KO_CLEAN_FINAL_PREVIOUS_'+$Stamp+'.iso'))}
 Move-Item -LiteralPath $TempIsoPath -Destination $FinalIsoPath
 $IsoSha=Get-Sha256 $FinalIsoPath
 ($IsoSha+' *'+$IsoName)|Out-File -LiteralPath $ShaFilePath -Encoding ascii
 @(
  'EDv9 26v5 Korean CLEAN SettingsSave FINAL ISO',
  ('Build time: '+(Get-Date)),
  ('Source: '+$SourceDir),
  'Filesystem: UDF 1.02',
  ('Volume label: '+$VolumeLabel),
  ('FINAL EXE SHA-256: '+$ExpectedSha.FinalExe),
  ('ISO SHA-256: '+$IsoSha),
  ('ISO bytes: '+(Get-Item -LiteralPath $FinalIsoPath).Length),
  ('Payload file count: '+$SourceFileCount),
  ('Payload bytes: '+$SourceBytes),
  'Validation: PASS'
 )|Out-File -LiteralPath $ReportPath -Encoding utf8
 Write-Host ('ISO: '+$FinalIsoPath)
 Write-Host ('SHA-256: '+$IsoSha)
} finally {if(Test-Path -LiteralPath $TempIsoPath){Remove-Item -LiteralPath $TempIsoPath -Force -EA SilentlyContinue}}
