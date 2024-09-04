#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%

pickImage := "pick.png"
banImage := "ban.png"
tolerance := 98 ; Adjust

; makes the pixel postitions relative to the active window 
CoordMode, Window

; values for 1600 * 900 client size
searchBarX := 930
searchBarY := 130 
champX := 500 
champY := 200
buttonX := 800
buttonY := 750


; Prompt the user for input
InputBox, pickChoice, Pick Choice, Please enter your pick choice:
if ErrorLevel
    MsgBox, canceled
else
    OutputDebug, Pick Choice: "%pickChoice%"

InputBox, banChoice, Ban Choice, Please enter your ban choice:
if ErrorLevel
    MsgBox, canceled
else
    OutputDebug, Ban Choice: "%banChoice%"

Loop
{
    ; Make the "League of Legends" window active
    ; WinActivate, League of Legends
    
    ; Wait until the window is active
    ; WinWaitActive, League of Legends
    
    ; Look for banImage
    ImageSearch, foundX, foundY, 0, 0, A_ScreenWidth, A_ScreenHeight, %banImage%
    
    if !ErrorLevel
    {
        OutputDebug, Found the banImage
        sleep 1000
        ; search bar
        Click, %searchBarX%, %searchBarY%

        ; type champ name
        SendInput, %banChoice%

        sleep 1000
        Click, %champX%, %champY%

        sleep 1000
        Click, %buttonX%, %buttonY%
        ; exit
        ; break

        ; look for pickImage
        ImageSearch, foundX2, foundY2, 0, 0, A_ScreenWidth, A_ScreenHeight, %pickImage%
        if !ErrorLevel
        {   
            OutputDebug, Found the pickImage
            sleep 1000
            ; search bar
            Click, %searchBarX%, %searchBarY%

            ; type champ name
            SendInput, %pickChoice%

            sleep 1000
            Click, %champX%, %champY%

            sleep 1000
            Click, %buttonX%, %buttonY%

            ; exit
            break   
        }

    }
    ; loop search timer
    Sleep, 500
}
