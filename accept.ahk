#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

imagePath := "accept.png"
tolerance := 100 ; Adjust
CoordMode, Window

ratioX := 0.5
ratioY := 0.78

Loop
{
    ImageSearch, foundX, foundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *%tolerance% %imagePath%
    if !ErrorLevel
    {   
        WinActivate, League of Legends  
        WinGetPos, winX, winY, winWidth, winHeight, League of Legends
        ; Calculate click position relative to the window size
        clickX := winWidth * ratioX
        clickY := winHeight * ratioY
        ; Sleep for a bit before clicking
        Sleep, 500

        ; Perform the click
        Click, %clickX%, %clickY%
        break
    }
    Sleep, 500
}
