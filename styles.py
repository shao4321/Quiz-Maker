from tkinter import *
from tkinter.ttk import *

MAIN_THEME = 'radiance'
character_limit_red = "#ff0000"
character_limit_yellow = '#b3b300'
character_limit_green = '#009900'
t_ent_font = ('Helvetica', 13)
treeview_even_row = '#99ccff'
treeview_odd_row = '#ffffff'

def style_widget(root):
    style = Style(root)

    # Label Widgets
    style.configure('TLabel', font=('Times', 20, 'underline'), anchor=CENTER)
    style.configure('Username.TLabel', font=('Times', 13, 'italic'))
    style.configure('MainPage.TLabel', font=('Times', 30, 'italic'), anchor=CENTER)
    style.configure('QuestionHead.TLabel', font=('Helvetica', 20, 'underline'), anchor=W)
    style.configure('Questions.TLabel', font=('Helvetica', 15, 'underline'), anchor=W)
    style.configure('Options.TLabel', font=('arial', 12))
    style.configure('CorrectAns.TLabel', font=('Helvetica', 15, 'bold'), foreground='#33ff33')
    style.configure('WrongAns.TLabel', font=('Helvetica', 15, 'bold'), foreground='red')
    style.configure('Typical.TLabel', font=('Helvetica', 15, 'bold'))
    style.configure('Char.TLabel', font=('Helvetica', 15, 'roman'))

    # Entry Widgets
    style.configure('Search.TEntry', )

    # RadioButtons
    style.configure('TRadiobutton', font=("arial", 14))

    # Button Widgets
    style.configure('TButton', font=('Helvetica', 13, 'italic', 'bold'))
    style.map('TButton',
              foreground=[('pressed', 'blue'), ('active', 'red'), ('disabled', 'grey')])

    # Frame Widgets
    style.configure('TopButtons.TFrame', borderwidth=2, relief='raised')

    # Treeview Widgets
    style.configure('Treeview',
                    background='#99ffcc',
                    foreground='#333300',
                    font=('Helvetica', 12),
                    rowheight=25,
                    fieldbackground='#99ffcc')
    style.map('Treeview', background=[('selected', '#6600ff')])
    style.configure('Treeview.Heading', font=('Helvetica', 15), background='#80ffff')
    style.map("Treeview.Heading", relief=[('active', 'groove'), ('pressed', 'sunken')])
