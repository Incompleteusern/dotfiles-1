from tkinter import Tk, Button, Text, INSERT, Label
import pyperclip
import sys

# Python program to create a close button
# using destroy Class method

# Class for tkinter window


class Window():
	def __init__(self):

		# Creating the tkinter Window
		self.root = Tk()
		self.root.option_add('*Font', 'DejaVuSansMono 32')

		textarea = Label(self.root, tex="Project-Text")
		textarea.pack(pady=10)

		mainarea = Text(self.root, height=10)
		mainarea.insert(INSERT, pyperclip.paste() or '\n'.join(sys.stdin.readlines()))
		mainarea.pack(pady=10)

		# Button for closing
		exit_button = Button(self.root, text="Exit", command=self.root.destroy)
		exit_button.pack(pady=20)

		self.root.mainloop()


Window()