#NoTrayIcon
; Runs ONLY in an isolated Hyper-V Windows QA VM from its Startup folder.
; Never clicks "install", "scan", or any destructive driver action.
Opt("WinTitleMatchMode", 2)
Local $folder = "C:\EDv9_Guard_QA"
DirCreate($folder)
Local $mode = StringUpper(StringStripWS(FileRead($folder & "\mode.txt"), 3))
If $mode <> "NEGATIVE" Then $mode = "POSITIVE"
Local $log = $folder & "\runtime_" & $mode & ".log"
FileDelete($log)
Func QA_Log($txt)
    FileWrite($log, @YEAR & "-" & @MON & "-" & @MDAY & " " & @HOUR & ":" & @MIN & ":" & @SEC & " " & $txt & @CRLF)
EndFunc
QA_Log("START MODE=" & $mode & " WINDOWS=" & @OSVersion & " USER=" & @UserName)
Local $drives = DriveGetDrive("CDROM")
If Not IsArray($drives) Then
    QA_Log("FAIL NO_CDROM")
    Exit 10
EndIf
Local $exe = ""
For $i = 1 To $drives[0]
    Local $candidate = $drives[$i] & "\EDv9_x64_KO_CLEAN.exe"
    QA_Log("DRIVE " & $drives[$i] & " LABEL=" & DriveGetLabel($drives[$i]))
    If FileExists($candidate) Then
        $exe = $candidate
        ExitLoop
    EndIf
Next
If $exe = "" Then
    QA_Log("FAIL NO_SEALED_EXE")
    Exit 11
EndIf
QA_Log("EXECUTABLE " & $exe)
Local $pid = Run('"' & $exe & '"', StringLeft($exe, 3))
QA_Log("PID=" & $pid & " ERROR=" & @error)
If $pid = 0 Then
    QA_Log("FAIL CANNOT_LAUNCH")
    Exit 12
EndIf
Local $creator = False
Local $security = False
Local $guardDenied = False
Local $mainSeen = False
Local $lastProgress = -1
For $t = 0 To 330
    If WinExists("EDv9 26v5 ISO 무결성 오류") Then
        $guardDenied = True
        QA_Log("GUARD_ERROR_WINDOW")
        ExitLoop
    EndIf
    If Not $creator And WinExists("EDv9 26v5 한글패치 V1.0") Then
        $creator = True
        QA_Log("CREATOR_POPUP_SEEN")
        WinActivate("EDv9 26v5 한글패치 V1.0")
        ControlClick("EDv9 26v5 한글패치 V1.0", "", "Button1")
        Send("{ENTER}")
        Sleep(800)
    EndIf
    If $creator And Not $security And WinExists("EDv9 26v5 CLEAN OFFLINE 보안 안내") Then
        $security = True
        QA_Log("SECURITY_POPUP_SEEN")
        WinActivate("EDv9 26v5 CLEAN OFFLINE 보안 안내")
        ControlClick("EDv9 26v5 CLEAN OFFLINE 보안 안내", "", "Button1")
        Send("{ENTER}")
        Sleep(1000)
    EndIf
    If $security Then
        Local $list = WinList()
        For $j = 1 To $list[0][0]
            Local $title = String($list[$j][0])
            Local $hwnd = $list[$j][1]
            If StringInStr($title, "ITSK") Or StringInStr($title, "万能驱动") Or StringInStr($title, "EDv9") Then
                If StringInStr($title, "한글패치") Or StringInStr($title, "보안 안내") Then ContinueLoop
                Local $pos = WinGetPos($hwnd)
                If IsArray($pos) And $pos[2] > 350 And $pos[3] > 200 Then
                    $mainSeen = True
                    QA_Log("MAIN_WINDOW=" & $title & " WIDTH=" & $pos[2] & " HEIGHT=" & $pos[3])
                    ExitLoop
                EndIf
            EndIf
        Next
    EndIf
    If $mode = "NEGATIVE" And $guardDenied Then ExitLoop
    If $mode = "POSITIVE" And $creator And $security And $mainSeen Then ExitLoop
    If Mod($t, 20) = 0 Then QA_Log("WAIT_SEC=" & $t & " CREATOR=" & $creator & " SECURITY=" & $security & " DENIED=" & $guardDenied & " PIDALIVE=" & ProcessExists($pid))
    Sleep(1000)
Next
Local $passed = False
If $mode = "POSITIVE" Then
    $passed = $creator And $security And Not $guardDenied
Else
    $passed = $guardDenied And Not $creator And Not $security
EndIf
QA_Log("FINAL PASS=" & $passed & " CREATOR=" & $creator & " SECURITY=" & $security & " GUARD_DENIED=" & $guardDenied & " MAIN=" & $mainSeen)
If ProcessExists($pid) Then ProcessClose($pid)
If $passed Then Exit 0
Exit 15
