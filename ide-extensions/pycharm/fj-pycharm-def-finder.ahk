; Double-click the script (with AutoHotKey v1 installed) to run now. Copy e script to "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup" to still take effect after reboot.

; The script makes a Ctrl+Shift+Click Pycharm shortcut for flip-jump files (Find macro declaration), that resembles the Ctrl+Click shortcut for python (Find function declaration).

; Script summery: Replace Ctrl+Shift+Click with  [ Click  ->  Copy the pointed word  ->  Ctrl+Shift+F (search in project)  ->  (search) "def " + copied word ].


^+Lbutton::
{
	; Click
	Send {Lbutton}
	
	; Mark the pointed word
	Send ^{Left}
	Send ^+{Right}
	
	; Copy the pointed word
	Send ^c
	
	; Unmark word
	Send {Right}
	
	; Open the "Find in files" window (shortcut in Pycharm)
	Send ^+f
	Sleep 100

	; Search for "def COPIED_WORD"
	Send {Home}
	Send +{End}
	Send def{Space}
	Send ^v
	Send {Space}
	
	return
}