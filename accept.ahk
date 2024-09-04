#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

imagePath := "images/accept.png"
tolerance := 100 ; Adjust
CoordMode, Window

Loop
{
    ImageSearch, foundX, foundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *%tolerance% %imagePath%
    if !ErrorLevel
    {
        sleep, 500
        Click, 800, 700
        break
    }
    Sleep, 500
}
