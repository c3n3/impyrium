from . import defaults
from .default_file import DefaultFile
import platform

ahkGetFile = DefaultFile(f"{defaults.WINDOWS_SCRIPTS_FOLDER}/{defaults.GET_FILE_AHK_SCRIPT_FILE}",
"""
#Requires AutoHotkey v1.1

#NoEnv
#SingleInstance Force

; Create a group of the windows that contain files and/or folders:
; ahk_group ExplorerDesktopGroup
GroupAdd, ExplorerDesktopGroup, ahk_class ExploreWClass
GroupAdd, ExplorerDesktopGroup, ahk_class CabinetWClass
GroupAdd, ExplorerDesktopGroup, ahk_class Progman
GroupAdd, ExplorerDesktopGroup, ahk_class WorkerW

; Write currently selected file to a file passed to the script by argument
FileAppend, % Explorer_GetSelection(), %1%
return

Explorer_GetSelection() {
    ; https://www.autohotkey.com/boards/viewtopic.php?style=17&t=60403#p255169
    WinGetClass, winClass, % "ahk_id" . hWnd := WinExist("A")
    if !(winClass ~= "^(Progman|WorkerW|(Cabinet|Explore)WClass)$")
        Return
    shellWindows := ComObjCreate("Shell.Application").Windows
    if (winClass ~= "Progman|WorkerW")
        shellFolderView := shellWindows.Item( ComObject(VT_UI4 := 0x13, SWC_DESKTOP := 0x8) ).Document
    else {
        for window in shellWindows
        if (hWnd = window.HWND) && (shellFolderView := window.Document)
            break
   }
    for item in shellFolderView.SelectedItems
        result .= (result = "" ? "" : "`n") . item.Path
    Return result
}
""",
isExample = False,
shouldWriteFun = lambda: platform.system() == "Windows"
)
