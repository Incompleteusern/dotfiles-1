#!/bin/sh -e

# Make sure we're in Dvorak
setxkbmap dvorak -option caps:escape
numlockx on

xmodmap -e "remove lock = Caps_Lock"

# synclient TapButton1=0           # Disable tap to click
# synclient TapButton2=0           # Disable double tap to paste
# synclient RightButtonAreaRight=1 # Remap mouse buttons
