#SingleInstance, Force
SendMode Input
SetWorkingDir, %A_ScriptDir%
CoordMode, Window ; Makes the pixel positions relative to the active window

; Set the path to images and tolerance
acceptImage  := "accept.png"
pickImage := "picksmol.png"
banImage := "ban.png"
tolerance := 100 ; Adjust as necessary


Pick := true
Ban := false
Accept := false
pickChoice := ""
banChoice := ""

; Set coordinates for 1600 * 900 client size
searchBarX := 950
searchBarY := 130 
champX := 500 
champY := 200
buttonX := 800
buttonY := 750
acceptX := 800
accepty := 750 

; Function to activate the target window
ActivateWindow(windowTitle)
{
    WinActivate, %windowTitle%
    WinWaitActive, %windowTitle%
}

; Function to prompt for user input
PromptForInput(title, message)
{
    InputBox, userInput, %title%, %message%
    if ErrorLevel
    {
        ExitApp
    }
    OutputDebug, %title%: "%userInput%"
    return userInput
}

; Function to search for an image and perform click actions
ImageSearchAndClick(imageFile, inputText)
{
    global searchBarX, searchBarY, champX, champY, buttonX, buttonY, tolerance
    msgBox %pickChoice%
    Loop {
        ImageSearch, foundX, foundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *%tolerance% %imageFile%
        if !ErrorLevel
            {
                OutputDebug, Found the image: %imageFile%
                Sleep, 1000
                
                ; Click on search bar
                Click, %searchBarX%, %searchBarY%
                
                Sleep, 1000
                ; Type the input text
                ; no worky inpuit
                SendInput, %inputText%
                
                Sleep, 1000
                Click, %champX%, %champY%
                
                Sleep, 1000
                Click, %buttonX%, %buttonY%
                
                break
            }
        Sleep, 500
    }
    return true
}

; Define the GUI function
GUI()
{
    global Pick, Ban, Accept, banChoice, pickChoice
    ; Create the GUI with checkboxes
    Gui, Add, Checkbox, vPick Checked%Pick% gTogglePick, Pick
    Gui, Add, Checkbox, vBan Checked%Ban% gToggleBan, Ban
    Gui, Add, Checkbox, vAccept Checked%Accept% Disabled, Accept
    ; Disabled
    Gui, Add, Button, gSubmit, Submit

    ; Show the GUI
    Gui, Show, , Pick/Ban/Accept Selection
    ; Wait for the user to interact with the GUI and press Submit
    Return

    ; Function to toggle the Pick variable
    TogglePick:
        Gui, Submit, NoHide
        Pick := Pick ? false : true
    Return

    ; Function to toggle the Ban variable
    ToggleBan:
        Gui, Submit, NoHide
        Ban := Ban ? false : true
    Return

    ; Handle the Submit button click
    Submit:
        Gui, Submit
        ; MsgBox, Pick: %Pick%`nBan: %Ban%`nAccept: %Accept%
        Gui, Destroy
        if pick {
            pickChoice := PromptForInput("Pick Choice", "Please enter your pick choice:")
        }
        ; Prompt the user for input
        if ban {
            banChoice := PromptForInput("Ban Choice", "Please enter your ban choice:")
        }
    Return
}

; Call the GUI function to display the GUI and wait for input
GUI()

; Look for the "Accept" image if Accept is enabled
;if Accept {
;    Loop {   
;
;        ImageSearch, foundX, foundY, 0, 0, A_ScreenWidth, A_ScreenHeight, *%tolerance% %acceptImage%
;        if !ErrorLevel
;        {
;            ; If found, click and break out of the loop
;            Sleep, 500
;            Click, %acceptX%, %acceptY%
;            break
;        }
;        Sleep, 500
;    }
;}

; Further actions like Pick and Ban could be triggered here using ImageSearchAndClick
if Pick{
    MsgBox %pickChoice%
    ImageSearchAndClick(pickImage, pickChoice)
}

;if Ban
;{
;    ImageSearchAndClick(banImage, banChoice)
;}