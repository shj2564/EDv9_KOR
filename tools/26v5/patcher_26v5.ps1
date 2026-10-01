$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.Encoding]::UTF8
$mode=$env:EDV9_PATCH_MODE; $self=$env:EDV9_PATCH_SELF; $argTarget=$env:EDV9_PATCH_TARGET
$origExeName='EDv9_x64.exe'; $koExeName='EDv9_x64_KO_CLEAN.exe'; $datName='EDv9_v9.0.2609.20009.dat'; $iniName='EDv9_x64.ini'; $verName='Drivers\@version'
$hOrigExe='C42EBB207FA52E8420F381952AE6A1EF6D37AE7164FE32E60841B1B630D11E86'; $hKo='12170E691631F202954E6FE6E19BC22B0C9F44571BB7FC9465FA9314254F41CA'; $hOrigDat='A713503A6D7FD6F1DAB450AB8CE5DC01B06550D0E7B5DCF5D17D54BAB8F7373D'; $hOrigIni='608E193A2B03A13C4F657F89A15B43CC40437906901DF8623B21FBA18775CCF2'; $hOrigVer='3C6923B48808D1B04B1280B447B7053F5CC8987EDCF1714B0FA1C83F422B633F'
function Hash([string]$p){ (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToUpperInvariant() }
function BytesHash([byte[]]$b){ $s=[Security.Cryptography.SHA256]::Create(); try {([BitConverter]::ToString($s.ComputeHash($b))).Replace('-','').ToUpperInvariant()} finally {$s.Dispose()} }
function Cleanup-Residue {
  try { if($script:target){ foreach($n in @('EDv9_x64_KO_CLEAN.exe.tmp','EDv9_x64_KO_CLEAN.exe.new')){$p=Join-Path $script:target $n;if(Test-Path -LiteralPath $p -PathType Leaf){Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue}}}} catch {}
  try { if($env:TEMP -and (Test-Path -LiteralPath $env:TEMP)){Get-ChildItem -LiteralPath $env:TEMP -Force -ErrorAction SilentlyContinue | Where-Object {$_.Name -like 'EDv9_26v5_Patch_*'} | ForEach-Object {Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue}}} catch {}
}
function Payload {
  $txt=[IO.File]::ReadAllText($self,[Text.Encoding]::UTF8)
  $m=[regex]::Match($txt,'(?s)__PAYLOAD_KOEXE_BEGIN__\r?\n(.*?)\r?\n__PAYLOAD_KOEXE_END__')
  if(-not $m.Success){throw '내장 CLEAN EXE 데이터를 찾지 못했습니다.'}
  $gz=[Convert]::FromBase64String(($m.Groups[1].Value -replace '\s',''))
  $mi=New-Object IO.MemoryStream(,$gz); $gs=New-Object IO.Compression.GZipStream($mi,[IO.Compression.CompressionMode]::Decompress); $mo=New-Object IO.MemoryStream
  try {$gs.CopyTo($mo); return $mo.ToArray()} finally {$gs.Dispose();$mi.Dispose();$mo.Dispose()}
}
function FindTarget {
  if($argTarget -and (Test-Path -LiteralPath $argTarget -PathType Container)){$p=(Resolve-Path -LiteralPath $argTarget).Path;if(Test-Path -LiteralPath (Join-Path $p $origExeName)){return $p}}
  $here=Split-Path -Parent $self
  if(Test-Path -LiteralPath (Join-Path $here $origExeName)){return $here}
  foreach($rel in @('EDv9_26v5','EDv9_26v5_Extracted\EDv9_26v5')){$p=Join-Path $here $rel;if(Test-Path -LiteralPath (Join-Path $p $origExeName)){return $p}}
  $sh=New-Object -ComObject Shell.Application; $f=$sh.BrowseForFolder(0,'EDv9 26v5 원본 폴더를 선택하세요. (EDv9_x64.exe / DAT / Drivers가 있는 폴더)',0,0)
  if($null -eq $f){throw '폴더 선택이 취소되었습니다.'}; $p=$f.Self.Path
  if(-not (Test-Path -LiteralPath (Join-Path $p $origExeName))){throw '선택한 폴더에 EDv9_x64.exe가 없습니다.'}; return $p
}
trap {try{Cleanup-Residue}catch{};Write-Host '';Write-Host ('[오류] '+$_.Exception.Message) -ForegroundColor Red;Write-Host '[정리] 임시 파일을 제거했습니다.' -ForegroundColor DarkGray;exit 1}
$target=FindTarget; $origExe=Join-Path $target $origExeName; $koExe=Join-Path $target $koExeName; $dat=Join-Path $target $datName; $ini=Join-Path $target $iniName; $ver=Join-Path $target $verName
if((Hash $origExe) -ne $hOrigExe){throw '지원하지 않는 EDv9_x64.exe입니다. 정확한 26v5 원본(9.0.2609.20009)인지 확인하세요.'}
if(-not(Test-Path -LiteralPath $dat -PathType Leaf)){throw "$datName 파일이 없습니다."}; if((Hash $dat)-ne $hOrigDat){throw '26v5 원본 DAT가 아닙니다. 안전을 위해 중단합니다.'}
if(-not(Test-Path -LiteralPath $ini -PathType Leaf)){throw "$iniName 파일이 없습니다."}; if((Hash $ini)-ne $hOrigIni){throw '26v5 원본 INI가 아닙니다. 안전을 위해 중단합니다.'}
if(-not(Test-Path -LiteralPath (Join-Path $target 'Drivers') -PathType Container)){throw 'Drivers 폴더가 없습니다. 전체 26v5 패키지를 먼저 안전하게 압축 해제하세요.'}
if(-not(Test-Path -LiteralPath $ver -PathType Leaf)){throw 'Drivers\@version 파일이 없습니다. 전체 26v5 패키지인지 확인하세요.'}; if((Hash $ver)-ne $hOrigVer){throw '26v5 Drivers\@version이 기준과 다릅니다. 안전을 위해 중단합니다.'}
if($mode -eq 'restore'){
  if(Test-Path -LiteralPath $koExe -PathType Leaf){if((Hash $koExe)-eq $hKo){Remove-Item -LiteralPath $koExe -Force}else{throw 'EDv9_x64_KO_CLEAN.exe가 이 패처의 파일과 달라 임의 삭제하지 않았습니다.'}}
  Cleanup-Residue; Write-Host ''; Write-Host '[완료] 26v5 Korean CLEAN FINAL 실행파일을 제거했습니다.' -ForegroundColor Green; Write-Host '[보존] 원본 EXE / DAT / INI / Drivers는 변경하지 않았습니다.' -ForegroundColor Cyan; exit 0
}
if(Test-Path -LiteralPath $koExe -PathType Leaf){if((Hash $koExe)-ne $hKo){throw '기존 EDv9_x64_KO_CLEAN.exe가 다른 파일입니다. 덮어쓰지 않았습니다.'}}
$k=Payload; if((BytesHash $k)-ne $hKo){throw '내장 CLEAN EXE 무결성 검증 실패'}
$tmp=$koExe+'.tmp'; [IO.File]::WriteAllBytes($tmp,$k); if((Hash $tmp)-ne $hKo){throw '임시 CLEAN EXE SHA-256 검증 실패'}; Move-Item -LiteralPath $tmp -Destination $koExe -Force
if((Hash $koExe)-ne $hKo){throw 'CLEAN EXE 적용 후 SHA-256 검증 실패'}
if((Hash $origExe)-ne $hOrigExe -or (Hash $dat)-ne $hOrigDat -or (Hash $ini)-ne $hOrigIni -or (Hash $ver)-ne $hOrigVer){throw '적용 과정에서 원본 기준 파일이 변경되었습니다.'}
Cleanup-Residue
Write-Host ''; Write-Host '============================================================' -ForegroundColor DarkCyan; Write-Host ' EDv9 26v5 Korean CLEAN OFFLINE FINAL 적용 완료' -ForegroundColor Green; Write-Host '============================================================' -ForegroundColor DarkCyan
Write-Host ('[생성] '+$koExeName) -ForegroundColor Cyan; Write-Host '[검증] 원본 EXE / DAT / INI / Drivers\@version 해시 PASS' -ForegroundColor Cyan; Write-Host '[보존] 원본 EXE / DAT / INI / Drivers 무변경' -ForegroundColor Cyan; Write-Host '[CLEAN] 온라인 후처리 / Edge 변경 / SoftInst 경로 차단' -ForegroundColor Cyan; Write-Host '[유지] UnmountDrv 및 드라이버 핵심 경로 유지' -ForegroundColor Cyan; Write-Host '[안내] 자동 실행하지 않습니다. 생성된 CLEAN EXE를 직접 실행하세요.' -ForegroundColor Yellow; Write-Host ('SHA-256: '+$hKo) -ForegroundColor DarkGray; Write-Host ''; exit 0