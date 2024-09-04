#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

imagePath := "accept.png"
tolerance := 98 ; Adjust
CoordMode, Window

Loop
{
    ImageSearch, foundX, foundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *%tolerance% %imagePath%
    if !ErrorLevel
    {
        sleep, 500
        Click, 800, 750
        break
    }
    Sleep, 500
}
