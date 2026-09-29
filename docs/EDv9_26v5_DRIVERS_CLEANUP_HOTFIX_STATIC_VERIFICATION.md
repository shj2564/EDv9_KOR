EDv9 26v5 C:\Drivers Auto-Cleanup HOTFIX TEST - Static Verification

Base runtime-passed EXE SHA-256 : 40D5155F455260AC750B65BA80499B8C88673C3DCA18EAA750C26D238A886D89
Cleanup TEST EXE SHA-256        : 955E845CBB0A4B3659A35423157D15047B315A38000EA1D9EB1F05D515597713
Cleanup TEST size               : 20427288 bytes
Active token SHA-256            : C2FE0C9D5FBA4A43697A81798710C0A164E5EB1BEB62E66B494EBCB15A9F6861
Active token lines              : 24042

Port source:
  26v4 final Completion HOTFIX token bytes used verbatim
  __SONG_DRIVERS_PREEXISTED registration lines: exact copy PASS
  __SONG_FINAL_CLEANUP function lines: exact copy PASS
  Func identifier opcode: known fixed HOTFIX bytes PASS
  @ERROR canonical spelling: 2/2 PASS

Safety behavior:
  Records whether C:\Drivers existed before EDv9 launch
  If pre-existing: does not delete it
  If RunOnce UnmountDrv exists in native/WOW6432 view: does not delete it
  Otherwise removes C:\Drivers recursively at normal AutoIt exit

Regression:
  Remove the 11 injected lines -> token stream equals the runtime-passed 26v5 CLEAN candidate byte-for-byte: PASS
  XQS Korean/CLEAN resources unchanged byte-for-byte: PASS
  .text/.rdata/.data/.pdata/.reloc/.kscr/.kres unchanged: PASS
  Authenticode certificate blob preserved byte-for-byte: PASS
  Forbidden network domains remain absent: PASS

STATUS: STATIC VERIFIED / C:\Drivers CLEANUP RUNTIME TEST REQUIRED