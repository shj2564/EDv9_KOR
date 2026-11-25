#NoTrayIcon
; EDv9 26v5 native ISO seal - builds into the original AutoIt SCRIPT.
; Not a standalone launcher; strict UDF ISO-only policy.
; SEALED ISO hash normalization: overwrite ONLY 64 ASCII hex hash bytes with zero
; before SHA-256. The 64-byte slot remains at the same raw ISO offset.
; Guard data is embedded in the final EXE's dedicated PE section by the builder.
; The resulting ISO must be sealed and verified in the builder before distribution.

Func __SONG_ISO_Stop($reason)
    ProgressOff()
    MsgBox(16, "EDv9 26v5 ISO 무결성 오류", _
        "ISO 무결성 검증에 실패하여 실행을 중단합니다." & @CRLF & @CRLF & _
        $reason & @CRLF & @CRLF & _
        "제작자: SoNG / 무단변조 금지" & @CRLF & _
        "정상 배포 ISO를 Windows에서 마운트한 후 실행해 주세요.")
    Exit 91
EndFunc

Func __SONG_ISO_ReadSeal()
    Local $f = FileOpen(@ScriptFullPath, 16)
    If $f = -1 Then Return SetError(1, 0, 0)
    Local $data = FileRead($f)
    FileClose($f)
    If @error Or BinaryLen($data) < 1024 Then Return SetError(2, 0, 0)
    Local $s = BinaryToString($data, 1)
    $data = 0
    Local $needle = "EDV9_ISO_SEAL_V1|O="
    Local $at = StringInStr($s, $needle, 1)
    If $at = 0 Then Return SetError(3, 0, 0)
    Local $tail = StringMid($s, $at, 140)
    $s = ""
    Local $matches = StringRegExp($tail, "^EDV9_ISO_SEAL_V1\|O=([0-9A-F]{16})\|S=([0-9A-F]{16})\|H=([0-9A-F]{64})\|END", 1)
    If Not IsArray($matches) Or UBound($matches) <> 3 Then Return SetError(4, 0, 0)
    If $matches[2] = StringRepeat("0", 64) Then Return SetError(5, 0, 0)
    Local $out[3]
    $out[0] = Dec($matches[0])
    $out[1] = Dec($matches[1])
    $out[2] = StringUpper($matches[2])
    If $out[0] <= 0 Or $out[1] < 1000000 Then Return SetError(6, 0, 0)
    If $out[0] + 64 > $out[1] Then Return SetError(7, 0, 0)
    Return $out
EndFunc

Func __SONG_ISO_BCryptStart()
    Local $hAlg = DllCall("bcrypt.dll", "long", "BCryptOpenAlgorithmProvider", _
        "ptr*", 0, "wstr", "SHA256", "ptr", 0, "ulong", 0)
    If @error Or Not IsArray($hAlg) Or $hAlg[0] <> 0 Or $hAlg[1] = 0 Then Return SetError(1, 0, 0)
    Local $hHash = DllCall("bcrypt.dll", "long", "BCryptCreateHash", _
        "ptr", $hAlg[1], "ptr*", 0, "ptr", 0, "ulong", 0, "ptr", 0, "ulong", 0, "ulong", 0)
    If @error Or Not IsArray($hHash) Or $hHash[0] <> 0 Or $hHash[2] = 0 Then
        DllCall("bcrypt.dll", "long", "BCryptCloseAlgorithmProvider", "ptr", $hAlg[1], "ulong", 0)
        Return SetError(2, 0, 0)
    EndIf
    Local $out[2] = [$hAlg[1], $hHash[2]]
    Return $out
EndFunc

Func __SONG_ISO_BCryptEnd($ctx)
    If Not IsArray($ctx) Then Return
    If $ctx[1] Then DllCall("bcrypt.dll", "long", "BCryptDestroyHash", "ptr", $ctx[1])
    If $ctx[0] Then DllCall("bcrypt.dll", "long", "BCryptCloseAlgorithmProvider", "ptr", $ctx[0], "ulong", 0)
EndFunc

Func __SONG_ISO_Verify()
    Local $seal = __SONG_ISO_ReadSeal()
    If Not IsArray($seal) Then Return SetError(1, 0, False)

    If StringMid(@ScriptFullPath, 2, 1) <> ":" Then Return SetError(2, 0, False)
    Local $drive = StringLeft(@ScriptFullPath, 2)
    Local $dtype = DllCall("kernel32.dll", "uint", "GetDriveTypeW", "wstr", $drive & "\")
    If @error Or Not IsArray($dtype) Or $dtype[0] <> 5 Then Return SetError(3, 0, False)

    ; The mounted ISO is accessed as raw CD-ROM media, not via a cached
    ; manifest of its ordinary files. Metadata and added/removed files count.
    Local $dev = "\\.\" & $drive
    Local $fd = DllCall("kernel32.dll", "handle", "CreateFileW", "wstr", $dev, _
        "dword", 0x80000000, "dword", 3, "ptr", 0, "dword", 3, _
        "dword", 0x08000000, "ptr", 0)
    If @error Or Not IsArray($fd) Or $fd[0] = Ptr(-1) Or $fd[0] = 0 Then Return SetError(4, 0, False)
    Local $handle = $fd[0]

    Local $ctx = __SONG_ISO_BCryptStart()
    If Not IsArray($ctx) Then
        DllCall("kernel32.dll", "bool", "CloseHandle", "handle", $handle)
        Return SetError(5, 0, False)
    EndIf

    Local Const $CHUNK = 4194304
    Local $buf = DllStructCreate("byte[" & $CHUNK & "]")
    Local $got = DllStructCreate("dword")
    Local $pos = 0
    Local $errorCode = 0
    Local $lastPercent = -1

    ProgressOn("EDv9 ISO 전체 무결성 검사", "승인된 배포 ISO인지 검증 중입니다.", "0%", -1, -1, 16)
    While $pos < $seal[1]
        Local $take = $CHUNK
        If $seal[1] - $pos < $CHUNK Then $take = $seal[1] - $pos
        DllStructSetData($got, 1, 0)
        Local $r = DllCall("kernel32.dll", "bool", "ReadFile", _
            "handle", $handle, "ptr", DllStructGetPtr($buf), _
            "dword", $take, "ptr", DllStructGetPtr($got), "ptr", 0)
        Local $n = DllStructGetData($got, 1)
        If @error Or Not IsArray($r) Or Not $r[0] Or $n <> $take Then
            $errorCode = 6
            ExitLoop
        EndIf

        ; Normalization of the self-referential hash slot only.
        Local $lo = $seal[0]
        If $lo < $pos Then $lo = $pos
        Local $hi = $seal[0] + 64
        If $hi > $pos + $n Then $hi = $pos + $n
        If $lo < $hi Then
            For $j = $lo To $hi - 1
                DllStructSetData($buf, 1, Asc("0"), ($j - $pos) + 1)
            Next
        EndIf

        Local $s = DllCall("bcrypt.dll", "long", "BCryptHashData", _
            "ptr", $ctx[1], "ptr", DllStructGetPtr($buf), "ulong", $n, "ulong", 0)
        If @error Or Not IsArray($s) Or $s[0] <> 0 Then
            $errorCode = 7
            ExitLoop
        EndIf
        $pos += $n
        Local $pct = Int($pos * 100 / $seal[1])
        If $pct <> $lastPercent Then
            $lastPercent = $pct
            ProgressSet($pct, "ISO 전체 SHA-256 검사 중 (" & $pct & "%)")
        EndIf
    WEnd

    ; Detect an image that was extended beyond the approved byte count.
    If $errorCode = 0 Then
        Local $extra = DllStructCreate("byte[2048]")
        DllStructSetData($got, 1, 0)
        Local $tail = DllCall("kernel32.dll", "bool", "ReadFile", _
            "handle", $handle, "ptr", DllStructGetPtr($extra), _
            "dword", 2048, "ptr", DllStructGetPtr($got), "ptr", 0)
        If Not @error And IsArray($tail) And $tail[0] Then
            If DllStructGetData($got, 1) <> 0 Then $errorCode = 8
        EndIf
    EndIf

    Local $hash = ""
    If $errorCode = 0 Then
        Local $result = DllStructCreate("byte[32]")
        Local $done = DllCall("bcrypt.dll", "long", "BCryptFinishHash", _
            "ptr", $ctx[1], "ptr", DllStructGetPtr($result), "ulong", 32, "ulong", 0)
        If @error Or Not IsArray($done) Or $done[0] <> 0 Then
            $errorCode = 9
        Else
            $hash = StringUpper(Hex(DllStructGetData($result, 1)))
        EndIf
    EndIf

    __SONG_ISO_BCryptEnd($ctx)
    DllCall("kernel32.dll", "bool", "CloseHandle", "handle", $handle)
    ProgressOff()
    If $errorCode Then Return SetError($errorCode, 0, False)
    If StringLen($hash) <> 64 Or $hash <> $seal[2] Then Return SetError(10, 0, False)
    Return True
EndFunc

Func __SONG_ISO_VerifyOrExit()
    Local $verified = __SONG_ISO_Verify()
    If $verified Then Return
    Local $reason = "오류 코드: " & @error
    __SONG_ISO_Stop($reason)
EndFunc
