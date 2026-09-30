$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'

$FinalExe='EDv9_x64_KO_CLEAN.exe'
$Dat='EDv9_v9.0.2609.20009.dat'
$Ini='EDv9_x64.ini'
$Iso='EDv9_26v5_KO_CLEAN_FINAL.iso'
$Label='EDv9_26v5_KO'

$SHA=@{
 Final='955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713'
 Original='C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86'
 Dat='A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D'
 Ini='608E193A2B03A13C4F657F89A15B43CC40437906901DF8623B21FBA18775CCF2'
 Version='3C6923B48808D1B04B1280B447B7053F5CC8987EDCF1714B0FA1C83F422B633F'
 Oscdimg='801D8BC3FFA4C15B1740C3FAE78612243315F35ED0683E28C22570A6F5A251A9'
}
function H($p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToUpperInvariant()}
function Need($ok,$m){if(-not $ok){throw $m}}
function LinkOrCopy($s,$d){
 $p=Split-Path -Parent $d; if(!(Test-Path -LiteralPath $p)){[IO.Directory]::CreateDirectory($p)|Out-Null}
 try{New-Item -ItemType HardLink -Path $d -Target $s -Force -ErrorAction Stop|Out-Null}
 catch{Copy-Item -LiteralPath $s -Destination $d -Force}
}
function Find-Oscdimg {
 $c=@('D:\etc_Util_All\Oscdimg\oscdimg.exe',
 (Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe'),
 (Join-Path ${env:ProgramFiles(x86)} 'Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\x86\Oscdimg\oscdimg.exe'))
 foreach($p in $c){if($p -and (Test-Path -LiteralPath $p)){return $p}}
 try{return (Get-Command oscdimg.exe -ErrorAction Stop).Source}catch{}
 if(Test-Path 'D:\etc_Util_All'){return (Get-ChildItem 'D:\etc_Util_All' -Filter oscdimg.exe -File -Recurse -ErrorAction SilentlyContinue|Select-Object -First 1).FullName}
}

$src=(Get-Location).Path
if(!(Test-Path (Join-Path $src $FinalExe))){
 Add-Type -AssemblyName System.Windows.Forms
 $d=New-Object System.Windows.Forms.FolderBrowserDialog
 $d.Description='Select EDv9_26v5 folder containing FINAL EXE / DAT / INI / Drivers'
 Need ($d.ShowDialog() -eq 'OK') 'Source folder not selected'
 $src=$d.SelectedPath
}
$final=Join-Path $src $FinalExe;$dat=Join-Path $src $Dat;$ini=Join-Path $src $Ini
$drivers=Join-Path $src 'Drivers';$ver=Join-Path $drivers '@version'
Need ((H $final)-eq $SHA.Final) 'FINAL EXE hash mismatch'
Need ((H $dat)-eq $SHA.Dat) 'DAT hash mismatch'
Need ((H $ini)-eq $SHA.Ini) 'INI hash mismatch'
Need ((H $ver)-eq $SHA.Version) 'Drivers/@version hash mismatch'
$orig=Join-Path $src 'EDv9_x64.exe'
if(Test-Path $orig){Need ((H $orig)-eq $SHA.Original) 'Original EXE hash mismatch'}
Need (@(Get-ChildItem $drivers -Filter *.exe -File -Recurse).Count -eq 0) 'Unexpected EXE in Drivers'
Need (@(Get-ChildItem $drivers -Recurse -Force|?{$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count -eq 0) 'ReparsePoint in Drivers'

$parent=Split-Path -Parent $src
$stage=Join-Path $parent ('.__EDv9_26v5_ISO_STAGE_'+$PID)
$out=Join-Path $parent $Iso
$report=Join-Path $parent 'EDv9_26v5_KO_CLEAN_FINAL.ISO_BUILD_REPORT.txt'
$shafile=Join-Path $parent 'EDv9_26v5_KO_CLEAN_FINAL.sha256.txt'
try{
 [IO.Directory]::CreateDirectory($stage)|Out-Null
 LinkOrCopy $final (Join-Path $stage $FinalExe)
 LinkOrCopy $dat (Join-Path $stage $Dat)
 LinkOrCopy $ini (Join-Path $stage $Ini)
 [IO.Directory]::CreateDirectory((Join-Path $stage 'Drivers'))|Out-Null
 Get-ChildItem $drivers -Directory -Recurse -Force|%{
  $r=$_.FullName.Substring($drivers.Length).TrimStart('\')
  [IO.Directory]::CreateDirectory((Join-Path (Join-Path $stage 'Drivers') $r))|Out-Null
 }
 Get-ChildItem $drivers -File -Recurse -Force|%{
  $r=$_.FullName.Substring($drivers.Length).TrimStart('\')
  LinkOrCopy $_.FullName (Join-Path (Join-Path $stage 'Drivers') $r)
 }
 $sf=@(Get-ChildItem $stage -File -Recurse -Force);$count=$sf.Count;[Int64]$bytes=($sf|measure Length -Sum).Sum
 $ex=@(Get-ChildItem $stage -Filter *.exe -File -Recurse -Force)
 Need ($ex.Count -eq 1 -and $ex[0].Name -eq $FinalExe) 'Stage EXE policy failure'

 $osc=Find-Oscdimg;Need $osc 'oscdimg.exe not found'
 Need ((H $osc)-eq $SHA.Oscdimg) 'OSCDIMG hash mismatch'
 if(Test-Path $out){Remove-Item $out -Force}
 & $osc '-m' '-o' '-h' '-u2' '-udfver102' ('-l'+$Label) $stage $out
 Need ($LASTEXITCODE -eq 0 -and (Test-Path $out)) 'OSCDIMG build failed'

 $mounted=$false
 try{
  Mount-DiskImage -ImagePath $out -StorageType ISO -PassThru|Out-Null;$mounted=$true
  $v=$null;for($i=0;$i-lt 30;$i++){Start-Sleep -Milliseconds 500;$v=Get-DiskImage -ImagePath $out|Get-Volume -EA SilentlyContinue|? DriveLetter|select -First 1;if($v){break}}
  Need $v 'Mounted ISO volume not found';$root=$v.DriveLetter+':\'
  Need !(Test-Path (Join-Path $root 'EDv9_x64.exe')) 'Original EXE found in ISO'
  $ix=@(Get-ChildItem $root -Filter *.exe -File -Recurse -Force)
  Need ($ix.Count -eq 1 -and $ix[0].Name -eq $FinalExe) 'ISO EXE policy failure'
  Need ((H (Join-Path $root $FinalExe))-eq $SHA.Final) 'ISO FINAL EXE hash mismatch'
  $if=@(Get-ChildItem $root -File -Recurse -Force);[Int64]$ib=($if|measure Length -Sum).Sum
  Need ($if.Count -eq $count -and $ib -eq $bytes) 'ISO count/bytes mismatch'
 }finally{if($mounted){Dismount-DiskImage -ImagePath $out -EA SilentlyContinue|Out-Null}}

 $ih=H $out
 ($ih+' *'+$Iso)|Out-File $shafile -Encoding ascii
 @('EDv9 26v5 Korean CLEAN FINAL ISO','Filesystem: UDF 1.02','Volume: '+$Label,
 'FINAL EXE SHA-256: '+$SHA.Final,'ISO SHA-256: '+$ih,'ISO bytes: '+(Get-Item $out).Length,
 'File count: '+$count,'Payload bytes: '+$bytes,'Validation: PASS')|Out-File $report -Encoding utf8
 Write-Host ('ISO: '+$out);Write-Host ('SHA-256: '+$ih)
 try{Set-Clipboard $ih}catch{}
}finally{if(Test-Path $stage){Remove-Item $stage -Recurse -Force -EA SilentlyContinue}}
