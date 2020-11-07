from tkinter import *
from tkinter.ttk import *
from tkinter import simpledialog
from tkinter import messagebox
from ttkthemes import themed_tk as tk
from datetime import datetime
import pytz
import sqlite3
import styles

qn_list = []
qn_len_list = []
opt_ans_list = []
tz_SG = pytz.timezone('Asia/Singapore')
QUESTION_LENGTH_LIM = 70
MAX_OPTION = 5
MAX_QNS = 10


class ConstrainedEntry(Entry):
    def __init__(self, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)

        vcmd = (self.register(self.on_validate), "%P")
        self.configure(validate="key", validatecommand=vcmd)

    def disallow(self):
        self.bell()

    def on_validate(self, new_value):
        try:
            if new_value.strip() == "":
                return True
            value = len(new_value)
            if value > QUESTION_LENGTH_LIM:
                self.disallow()
                return False
        except ValueError:
            self.disallow()
            return False

        return True


# Slide bar and using mousewheel to scroll
def onMouseWheel(event):
    set_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def boundToMouseWheel():
    set_canvas.bind_all("<MouseWheel>", onMouseWheel)


def unboundToMouseWheel():
    set_canvas.unbind_all("<MouseWheel>")


def reset_scrollregion():
    set_canvas.configure(scrollregion=set_canvas.bbox('all'))


def update_qn_length(event):
    global qn_len_list
    global qn_list
    index = qn_list.index(event.widget)
    remain_space = QUESTION_LENGTH_LIM - len(event.widget.get())
    if 10 <= remain_space < 40:
        qn_len_list[index].configure(foreground=styles.character_limit_yellow)
    elif remain_space < 10:
        qn_len_list[index].configure(foreground=styles.character_limit_red)
    else:
        qn_len_list[index].configure(foreground=styles.character_limit_green)
    qn_len_list[index].configure(text=f'Characters: ({len(event.widget.get())}/{QUESTION_LENGTH_LIM})')


def SetQns():
    global set_root
    global set_second_frame
    global set_canvas
    global qn_list
    global qn_len_list
    global opt_ans_list
    global choice_grid_index_list
    global add_btn_count
    global all_add_opt_btn_list
    global conn
    global c
    global qn_length_limit
    global qn

    conn = sqlite3.connect('questions.db')
    c = conn.cursor()

    qn_list = []
    opt_ans_list = []
    all_add_opt_btn_list = []
    choice_grid_index_list = []

    set_root = tk.ThemedTk()
    set_root.get_themes()
    set_root.set_theme(styles.MAIN_THEME)
    set_root.iconbitmap('main_qn.ico')

    app_width2 = 840
    app_height2 = 700

    screen_width2 = set_root.winfo_screenwidth()
    screen_height2 = set_root.winfo_screenheight()

    x2 = (screen_width2 / 2) - (app_width2 / 2)
    y2 = (screen_height2 / 2) - (app_height2 / 2)
    set_root.geometry(f"{app_width2}x{app_height2}+{int(x2)}+{int(y2)}")

    title = simpledialog.askstring("Title", "Title of question: ", parent=set_root)
    if not title:
        set_root.destroy()
        return
    set_root.title(title)
    set_root.after(1, lambda: set_root.focus_force())

    set_root.rowconfigure(0, weight=0)
    set_root.rowconfigure(1, weight=1)
    set_root.columnconfigure(0, weight=1)
    set_root.resizable(False, False)

    # Call Style Function
    styles.style_widget(set_root)

    head = Label(set_root, text='Type in your questions and set your answers for each question')
    head.grid(row=0, column=0, sticky='nsew')

    '''Creating a scrollbar'''
    # Create a main frame
    set_main_frame = Frame(set_root)
    set_main_frame.grid(row=1, column=0, sticky='nsew')

    # Create a canvas
    set_canvas = Canvas(set_main_frame)
    set_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    # Add a Scrollbar to the Canvas
    set_scrollbar = Scrollbar(set_main_frame, orient=VERTICAL, command=set_canvas.yview)
    set_scrollbar.pack(side=RIGHT, fill=Y)

    # Configure the Canvas
    set_canvas.config(yscrollcommand=set_scrollbar.set)
    set_canvas.bind('<Configure>', lambda e: reset_scrollregion())
    set_canvas.bind('<Enter>', lambda e: boundToMouseWheel())
    set_canvas.bind('<Leave>', lambda e: unboundToMouseWheel())

    # Create another frame INSIDE the Canvas
    set_second_frame = Frame(set_canvas)

    # Add that New frame to a window in the canvas, 'Second Frame' becomes you MAIN WINDOW.
    set_canvas.create_window((0, 0), window=set_second_frame, anchor='nw')

    num_of_qns = simpledialog.askinteger("Question Numbers", "How many question do you want to set?",
                                         parent=set_root, minvalue=0, maxvalue=MAX_QNS)
    if not num_of_qns:
        set_root.destroy()
        return

    # Call Style Function
    styles.style_widget(set_second_frame)

    row = 0
    add_btn_count = 0
    for i in range(num_of_qns):
        qn_label = Label(set_second_frame, text=f'Question {i+1})')
        qn = ConstrainedEntry(set_second_frame, font=("Helvetica", 15), width=60)
        qn_length_limit = Label(set_second_frame, text=f'Characters: (0/{QUESTION_LENGTH_LIM})',
                                foreground=styles.character_limit_green, style='Char.TLabel')
        qn.bind('<Return>', lambda e: StoreQns())
        qn.bind('<KeyRelease>', update_qn_length)
        add_opt_btn = Button(set_second_frame, text='Add Choices', cursor='hand2')
        add_opt_btn.bind('<1>', AddChoices)
        add_opt_btn.bind('<Return>', AddChoices)
        qn_list.append(qn)
        qn_len_list.append(qn_length_limit)

        qn_label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
        qn.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row += 1
        qn_length_limit.grid(row=row, column=1, padx=2, sticky='e')
        row += 1
        add_opt_btn.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky='w')
        all_add_opt_btn_list.append(add_opt_btn)
        add_btn_count += 1
        choice_grid_index_list.append(row)
        row += 1

    qn_list[0].focus_set()
    submit_btn = Button(set_second_frame, text='Submit', cursor='hand2')
    submit_btn.bind('<1>', lambda e: StoreQns())
    submit_btn.bind('<Return>', lambda e: StoreQns())
    submit_btn.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky='e')

    # Dynamically updating the scrollbar when more question are added
    set_root.update()
    set_canvas.configure(scrollregion=set_canvas.bbox('all'))


def AddChoices(e):
    global choice_grid_index_list
    global all_add_opt_btn_list
    global set_canvas
    global add_btn_count
    index = all_add_opt_btn_list.index(e.widget)
    # Prompt user for number of options
    num_of_options = simpledialog.askinteger("Options", f"How many options for question {index + 1}?",
                                             parent=set_root, minvalue=1, maxvalue=MAX_OPTION)

    if not num_of_options:
        return

    # Update remaining number of add buttons
    add_btn_count -= 1

    # Frame for options
    option_frame = Frame(set_second_frame)
    option_frame.grid(row=choice_grid_index_list[index], column=0, columnspan=2, padx=5, pady=5, sticky='w')

    # Remove the add choice button
    e.widget.grid_forget()

    # Insert radiobutton
    option_nums = IntVar(set_second_frame)
    r = 0
    opt_list = []
    for j in range(num_of_options):
        opt_lbl = Label(option_frame, text=f'{j+1})', font=('arial', 12))
        opt = Radiobutton(option_frame, variable=option_nums, value=j+1, cursor='hand2')
        opt['text'] = simpledialog.askstring("Input Answer Options", f"Option {j+1}:", parent=set_root)
        opt_list.append(opt['text'])
        opt_lbl.grid(row=r, column=0, padx=5, pady=1, sticky='w')
        opt.grid(row=r, column=1, padx=5, pady=1, sticky='w')
        r += 1

    # Set correct answer and display it
    correct_ans = simpledialog.askinteger("Answer", f"What is the Answer Option for Question "
                                                    f"{index + 1}?",
                                          parent=set_root, minvalue=1, maxvalue=num_of_options)
    ans_label = Label(option_frame, text=u'\u2713', style='CorrectAns.TLabel')
    ans_label.grid(row=correct_ans-1, column=2, padx=5, pady=1, sticky='e')

    # Store information to be inserted into the database
    opt_ans_list.append((num_of_options, opt_list, correct_ans))

    # Dynamically updating the scrollbar when more question are added
    set_root.update()
    set_canvas.configure(scrollregion=set_canvas.bbox('all'))


def StoreQns():
    if add_btn_count:
        messagebox.showerror('Error', 'Please ensure all options are set')
        set_root.after(1, lambda: set_root.focus_force())
        return
    for q in qn_list:
        if not q.get():
            messagebox.showerror('Error', 'Please fill in all empty cells')
            set_root.after(1, lambda: set_root.focus_force())
            return
    datetime_SG = datetime.now(tz_SG)
    date_time = datetime_SG.strftime("%d/%m/%Y, %H:%M:%S")
    for q in range(len(qn_list)):
        for opt in range(opt_ans_list[q][0]):
            with conn:
                c.execute("INSERT INTO questions VALUES"
                          "(:question_title, :question, :option_num, :option, :answer, :date_time)",
                          {'question_title': set_root.title(),
                           'question': qn_list[q].get(),
                           'option_num': opt+1,
                           'option': opt_ans_list[q][1][opt],
                           'answer': opt_ans_list[q][2],
                           'date_time': date_time
                           })
    conn.close()
    set_root.destroy()
    return "break"
