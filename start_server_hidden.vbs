Set WshShell = CreateObject("WScript.Shell")

WshShell.CurrentDirectory = "C:\Projects\Medical-FactGuard-AI"

WshShell.Run """C:\Projects\Medical-FactGuard-AI\start_server.bat""", 0, False

Set WshShell = Nothing