#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

imagePath := "accept.png"
tolerance := 98 ; Adjust


; Number of pixels to move up and left
moveUp := -5
moveLeft := -5

Loop
{
    ImageSearch, foundX, foundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *%tolerance% %imagePath%
    
    ; If the image is found
    if !ErrorLevel
    {
        newX := foundX - moveLeft
        newY := foundY - moveUp
        
        MouseMove, newX, newY

        sleep, 100
        Click
        break
    }
    
    Sleep, 500
}
