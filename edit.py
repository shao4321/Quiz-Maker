from tkinter import *
from tkinter.ttk import *
from tkinter import simpledialog
from tkinter import messagebox
from ttkthemes import themed_tk as tk
from datetime import datetime
import storeQn
import pytz
import sqlite3
import styles


set_ans_list = []
added_new_qn_opt_list = []
added_new_ans_lbl_list = []
added_new_change_ans_btn = []
set_ans_count = 0
tz_SG = pytz.timezone('Asia/Singapore')


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
            if value > storeQn.QUESTION_LENGTH_LIM:
                self.disallow()
                return False
        except ValueError:
            self.disallow()
            return False

        return True


def Edit_Qn(e, refresh_btn):
    global edit_root
    global edit_canvas
    global qn_lbl_list
    global qn_Ent_list
    global qn_len_list
    global all_opt_lbl_list
    global opt_list
    global opt_variables_list
    global opt_frame_list
    global opt_btn_frame_list
    global all_opt_list
    global add_opt_btn_list
    global edit_opt_btn_list
    global del_opt_btn_list
    global change_ans_btn_list
    global edit_second_frame
    global corr_ans_list
    global current_ans_lbl_list
    global num_of_questions
    global question_num_title
    global row
    global save_records_btn
    global conn
    global c
    global add_new_qn
    global del_qn_btn
    global unset_choice_options_list

    qn_lbl_list = []
    qn_Ent_list = []
    qn_len_list = []
    opt_list = []
    opt_variables_list = []
    opt_frame_list = []
    opt_btn_frame_list = []
    all_opt_list = []
    all_opt_lbl_list = []
    add_opt_btn_list = []
    edit_opt_btn_list = []
    del_opt_btn_list = []
    change_ans_btn_list = []
    corr_ans_list = []
    current_ans_lbl_list = []
    unset_choice_options_list = []

    # Retrieve Selected Question from database
    conn = sqlite3.connect('questions.db')
    c = conn.cursor()

    edit_root = tk.ThemedTk()
    edit_root.get_themes()
    edit_root.set_theme(styles.MAIN_THEME)
    edit_root.iconbitmap('main_qn.ico')

    edit_root.after(1, lambda: edit_root.focus_set())
    question_num_title = e.widget.item(e.widget.focus())['values']
    edit_root.title(question_num_title[0])

    app_width2 = 850
    app_height2 = 700

    screen_width2 = edit_root.winfo_screenwidth()
    screen_height2 = edit_root.winfo_screenheight()

    x2 = (screen_width2 / 2) - (app_width2 / 2)
    y2 = (screen_height2 / 2) - (app_height2 / 2)
    edit_root.geometry(f"{app_width2}x{app_height2}+{int(x2)}+{int(y2)}")

    edit_root.rowconfigure(0, weight=0)
    edit_root.rowconfigure(1, weight=1)
    edit_root.columnconfigure(0, weight=1)
    edit_root.resizable(False, False)

    # Call Style Function
    styles.style_widget(edit_root)

    head = Label(edit_root, text='Editing Mode')
    head.grid(row=0, column=0, sticky='nsew')

    '''Creating a scrollbar'''
    # Create a main frame
    edit_main_frame = Frame(edit_root)
    edit_main_frame.grid(row=1, column=0, sticky='nsew')

    # Create a canvas
    edit_canvas = Canvas(edit_main_frame)
    edit_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    # Add a Scrollbar to the Canvas
    edit_scrollbar = Scrollbar(edit_main_frame, orient=VERTICAL, command=edit_canvas.yview)
    edit_scrollbar.pack(side=RIGHT, fill=Y)

    # Configure the Canvas
    edit_canvas.config(yscrollcommand=edit_scrollbar.set)
    edit_canvas.bind('<Configure>', lambda ev: reset_scrollregion())
    edit_canvas.bind('<Enter>', lambda ev: boundToMouseWheel())
    edit_canvas.bind('<Leave>', lambda ev: unboundToMouseWheel())

    # Create another frame INSIDE the Canvas
    edit_second_frame = Frame(edit_canvas)

    # Add that New frame to a window in the canvas, 'Second Frame' becomes you MAIN WINDOW.
    edit_canvas.create_window((0, 0), window=edit_second_frame, anchor='nw')

    row = 0

    c.execute("SELECT * FROM questions WHERE question_title=(?)", (question_num_title[0],))
    selected_questions_list = c.fetchall()
    selected_questions = []
    for i in selected_questions_list:
        if i[1] not in selected_questions:
            selected_questions.append(i[1])

    num_of_questions = question_num_title[1]
    for qns in range(num_of_questions):
        qn_label = Label(edit_second_frame, text=f'Question {qns + 1}) ')
        qn_Ent = ConstrainedEntry(edit_second_frame, font=("Helvetica", 15), width=60)
        qn_Ent.bind('<KeyRelease>', update_qn_length)
        qn_Ent.insert(0, selected_questions[qns])
        remain_space = storeQn.QUESTION_LENGTH_LIM - len(qn_Ent.get())
        if 10 <= remain_space < 40:
            fg = styles.character_limit_yellow
        elif remain_space < 10:
            fg = styles.character_limit_red
        else:
            fg = styles.character_limit_green
        qn_length_limit = Label(edit_second_frame,
                                text=f'Characters: ({len(qn_Ent.get())}/{storeQn.QUESTION_LENGTH_LIM})',
                                style='Char.TLabel', foreground=fg)

        qn_label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
        qn_Ent.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        row += 1
        qn_length_limit.grid(row=row, column=1, padx=2, sticky='e')
        qn_lbl_list.append(qn_label)
        qn_Ent_list.append(qn_Ent)
        qn_len_list.append(qn_length_limit)

        row += 1
        # Frame for options
        opt_frame = Frame(edit_second_frame)
        opt_frame.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        row += 1
        opt_btn_frame = Frame(edit_second_frame)
        opt_btn_frame.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        row += 2
        c.execute("SELECT * FROM questions WHERE question_title=(?) AND question=(?)",
                  (selected_questions_list[0][0], selected_questions[qns]))
        rec = c.fetchall()
        corr_ans = rec[0][4]
        option_nums = IntVar(edit_second_frame)
        r = 0
        opt_list = []
        opt_lbl_list = []
        for i in range(len(rec)):
            # Insert radiobutton
            opt_lbl = Label(opt_frame, text=f'{i + 1})', font=('arial', 12))
            opt = Radiobutton(opt_frame, text=rec[i][3], variable=option_nums, value=i + 1, cursor='hand2')
            opt_lbl.grid(row=r, column=0, padx=5, pady=3, sticky='w')
            opt.grid(row=r, column=1, padx=5, pady=3, sticky='w')

            # Keep Track of the opt labels and buttons
            opt_lbl_list.append(opt_lbl)
            opt_list.append(opt)
            r += 1

        current_ans_lbl = Label(opt_frame, text=u'\u2713', style='CorrectAns.TLabel')
        current_ans_lbl.grid(row=corr_ans - 1, column=2, padx=5, pady=3, sticky='e')
        current_ans_lbl_list.append(current_ans_lbl)

        opt_frame_list.append(opt_frame)
        opt_btn_frame_list.append(opt_btn_frame)
        all_opt_lbl_list.append(opt_lbl_list)
        all_opt_list.append(opt_list)
        opt_variables_list.append(option_nums)

        add_option_btn = Button(opt_btn_frame, text='Add Option', cursor='hand2')
        add_option_btn.bind('<1>', add_opt)
        add_option_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        add_opt_btn_list.append(add_option_btn)

        edit_option_btn = Button(opt_btn_frame, text='Edit Option', cursor='hand2')
        edit_option_btn.bind('<1>', edit_opt)
        edit_option_btn.grid(row=0, column=1, padx=3, pady=5, sticky='w')
        edit_opt_btn_list.append(edit_option_btn)

        del_option_btn = Button(opt_btn_frame, text='Delete Option', cursor='hand2')
        del_option_btn.bind('<1>', del_opt)
        del_option_btn.grid(row=0, column=2, padx=3, pady=5, sticky='w')
        del_opt_btn_list.append(del_option_btn)

        change_ans_btn = Button(opt_btn_frame, text='Change Answer', cursor='hand2')
        change_ans_btn.bind('<1>', change_ans)
        change_ans_btn.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        change_ans_btn_list.append(change_ans_btn)
        corr_ans_list.append(corr_ans)

        unset_choice_options_list.append(False)

    add_new_qn = Button(edit_second_frame, text='Add Question', cursor='hand2', command=add_qn)
    add_new_qn.grid(row=row, column=0, padx=5, pady=5, sticky='w')
    del_qn_btn = Button(edit_second_frame, text='Delete Question', cursor='hand2', command=del_qn)
    del_qn_btn.grid(row=row, column=1, padx=5, pady=5, sticky='w')
    row += 1
    save_records_btn = Button(edit_second_frame, text='Save', cursor='hand2')
    save_records_btn.bind('<1>', lambda event: save_record(refresh_btn))
    save_records_btn.bind('<Return>', lambda event: save_record(refresh_btn))
    save_records_btn.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky='e')


def update_qn_length(event):
    global qn_len_list
    global qn_Ent_list
    index = qn_Ent_list.index(event.widget)
    remain_space = storeQn.QUESTION_LENGTH_LIM - len(event.widget.get())
    if 10 <= remain_space < 40:
        qn_len_list[index].configure(foreground=styles.character_limit_yellow)
    elif remain_space < 10:
        qn_len_list[index].configure(foreground=styles.character_limit_red)
    else:
        qn_len_list[index].configure(foreground=styles.character_limit_green)
    qn_len_list[index].configure(text=f'Characters: ({len(event.widget.get())}/{storeQn.QUESTION_LENGTH_LIM})')


# Slide bar and using mousewheel to scroll
def onMouseWheel(event):
    edit_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def boundToMouseWheel():
    edit_canvas.bind_all("<MouseWheel>", onMouseWheel)


def unboundToMouseWheel():
    edit_canvas.unbind_all("<MouseWheel>")


def reset_scrollregion():
    edit_canvas.configure(scrollregion=edit_canvas.bbox('all'))


def add_opt(event):
    global all_opt_list
    global all_opt_lbl_list
    global opt_frame_list
    global edit_canvas
    global current_ans_lbl_list
    global unset_choice_options_list

    qn = add_opt_btn_list.index(event.widget)
    option_nums = opt_variables_list[qn]
    num_chosen_options = len(all_opt_list[qn])
    current_ans_lbl = current_ans_lbl_list[qn]

    opt_desc = simpledialog.askstring("Add Option", "Type in your new option", parent=edit_second_frame)
    if not opt_desc:
        return 'break'

    unset_choice_options_list[qn] = False
    opt_frame = opt_frame_list[qn]
    # Insert radiobutton
    opt_lbl = Label(opt_frame, text=f'{num_chosen_options + 1})', style='Options.TLabel')
    opt = Radiobutton(opt_frame, text=opt_desc, variable=option_nums, value=num_chosen_options + 1)
    opt_lbl.grid(row=num_chosen_options, column=0, padx=5, pady=3, sticky='w')
    opt.grid(row=num_chosen_options, column=1, padx=5, pady=3, sticky='w')

    all_opt_lbl_list[qn].append(opt_lbl)
    all_opt_list[qn].append(opt)

    if not num_chosen_options:
        current_ans_lbl.grid(row=0, column=2, padx=5, pady=3, sticky='e')

    # Dynamically updating the scrollbar when more question are added
    edit_root.update()
    edit_canvas.configure(scrollregion=edit_canvas.bbox('all'))
    edit_second_frame.after(1, lambda: edit_second_frame.focus_set())
    return 'break'


def del_opt(event):
    global all_opt_lbl_list
    global all_opt_list
    global opt_frame_list
    global current_ans_lbl_list
    global corr_ans_list
    global edit_canvas
    global unset_choice_options_list

    qn = del_opt_btn_list.index(event.widget)
    chosen_labels = all_opt_lbl_list[qn]
    chosen_options = all_opt_list[qn]
    opt_frame = opt_frame_list[qn]
    option_nums = opt_variables_list[qn]
    chosen_qn_ans = corr_ans_list[qn]
    current_ans_lbl = current_ans_lbl_list[qn]

    if not len(chosen_options):
        messagebox.showwarning('Alert', 'No more option to be deleted.')
        edit_root.after(1, lambda: edit_root.focus_force())
        return 'break'
    opt_num = simpledialog.askinteger("Delete Option", "Which option will you like to delete?",
                                      parent=edit_second_frame, minvalue=1, maxvalue=len(chosen_options))
    if not opt_num:
        return 'break'
    if opt_num < len(chosen_options):
        for opt in range(opt_num, len(chosen_options)):
            update_lbl = chosen_labels[opt]
            update_opt = chosen_options[opt]
            update_lbl.configure(text=f'{opt})')
            update_opt['value'] = opt
    chosen_opt = chosen_options[opt_num - 1]
    chosen_options.remove(chosen_opt)
    chosen_opt.destroy()
    chosen_label = chosen_labels[opt_num - 1]
    chosen_labels.remove(chosen_label)
    chosen_label.destroy()

    # Destroy all the widgets in opt_frame
    for widget in opt_frame.winfo_children():
        widget.grid_forget()

    r = 0
    # Place updated widgets into opt_frame
    for i in range(len(chosen_options)):
        opt_lbl = Label(opt_frame, text=f'{i + 1})', font=('arial', 12))
        opt = Radiobutton(opt_frame, text=chosen_options[i]['text'], variable=option_nums, value=i + 1)
        opt_lbl.grid(row=r, column=0, padx=5, pady=3, sticky='w')
        opt.grid(row=r, column=1, padx=5, pady=3, sticky='w')
        r += 1
    if len(chosen_options) == 0:
        unset_choice_options_list[qn] = True
        current_ans_lbl.grid_forget()
    elif len(chosen_options) == 1:
        corr_ans_list[qn] = 1
        current_ans_lbl.grid(row=0, column=2, padx=5, pady=3, sticky='e')
    else:
        if opt_num < chosen_qn_ans:
            chosen_qn_ans -= 1
            corr_ans_list[qn] = chosen_qn_ans
            current_ans_lbl.grid(row=chosen_qn_ans - 1, column=2, padx=5, pady=3, sticky='e')
        elif opt_num > chosen_qn_ans:
            current_ans_lbl.grid(row=chosen_qn_ans - 1, column=2, padx=5, pady=3, sticky='e')
        else:
            while True:
                new_ans = simpledialog.askinteger('New Answer', 'Type in your new answer',
                                                  parent=edit_second_frame, minvalue=0, maxvalue=r)
                if new_ans:
                    break
            current_ans_lbl.grid(row=new_ans - 1, column=2, padx=5, pady=3, sticky='e')
            corr_ans_list[qn] = new_ans

    # Dynamically updating the scrollbar when more question are added
    edit_root.update()
    edit_canvas.configure(scrollregion=edit_canvas.bbox('all'))
    edit_second_frame.after(1, lambda: edit_second_frame.focus_set())
    return 'break'


def edit_opt(event):
    global all_opt_list

    qn = edit_opt_btn_list.index(event.widget)
    chosen_options = all_opt_list[qn]
    opt_num = simpledialog.askinteger("Edit Option", "Which option will you like to edit?",
                                      parent=edit_second_frame, minvalue=1, maxvalue=len(chosen_options))
    if not opt_num:
        return 'break'
    rad_btn = chosen_options[opt_num-1]
    opt_details = simpledialog.askstring("Edit Option", "Edit Option Stated Below",
                                         parent=edit_second_frame, initialvalue=rad_btn['text'])
    rad_btn['text'] = opt_details

    edit_second_frame.after(1, lambda: edit_second_frame.focus_set())
    return 'break'


def add_qn():
    global edit_canvas
    global row
    global qn_lbl_list
    global qn_Ent_list
    global qn_len_list
    global all_opt_lbl_list
    global all_opt_list
    global opt_variables_list
    global opt_frame_list
    global opt_btn_frame_list
    global add_opt_btn_list
    global edit_opt_btn_list
    global del_opt_btn_list
    global change_ans_btn_list
    global current_ans_lbl_list
    global num_of_questions
    global set_ans_list
    global added_new_qn_opt_list
    global added_new_ans_lbl_list
    global added_new_change_ans_btn

    add_new_qn.grid_forget()
    del_qn_btn.grid_forget()
    qn_label = Label(edit_second_frame, text=f'Question {num_of_questions + 1}) ', style='Questions.TLabel')
    qn_Ent = ConstrainedEntry(edit_second_frame, font=("Helvetica", 15), width=60)
    qn_Ent.bind('<KeyRelease>', update_qn_length)
    qn_length_limit = Label(edit_second_frame, text=f'Characters: (0/{storeQn.QUESTION_LENGTH_LIM})',
                            style='Char.TLabel', foreground=styles.character_limit_green)

    save_records_btn.grid_forget()
    qn_label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
    qn_Ent.grid(row=row, column=1, padx=5, pady=5, sticky='w')
    row += 1
    qn_length_limit.grid(row=row, column=1, padx=2, sticky='e')

    qn_Ent_list.append(qn_Ent)
    qn_lbl_list.append(qn_label)
    qn_len_list.append(qn_length_limit)

    # Frame for options
    opt_frame = Frame(edit_second_frame)
    row += 1
    opt_frame.grid(row=row, column=0, columnspan=2, sticky='nw', padx=5, pady=5)
    row += 1
    opt_btn_frame = Frame(edit_second_frame)
    opt_btn_frame.grid(row=row, column=0, columnspan=2, sticky='nw', padx=5, pady=5)
    row += 2

    option_nums = IntVar(edit_second_frame)
    opt_list2 = []
    opt_lbl_list = []

    current_ans_lbl = Label(opt_frame, style='CorrectAns.TLabel')
    current_ans_lbl_list.append(current_ans_lbl)
    added_new_ans_lbl_list.append(current_ans_lbl)
    opt_frame_list.append(opt_frame)
    opt_btn_frame_list.append(opt_btn_frame)

    num_of_questions += 1
    all_opt_lbl_list.append(opt_lbl_list)
    all_opt_list.append(opt_list2)
    added_new_qn_opt_list.append(opt_list2)
    opt_variables_list.append(option_nums)

    add_new_qn.grid(row=row, column=0, padx=5, pady=5, sticky='w')
    del_qn_btn.grid(row=row, column=1, padx=5, pady=5, sticky='w')
    row += 1
    save_records_btn.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky='e')

    add_option_btn = Button(opt_btn_frame, text='Add Option', cursor='hand2')
    add_option_btn.bind('<1>', add_opt)
    add_option_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    add_opt_btn_list.append(add_option_btn)

    edit_option_btn = Button(opt_btn_frame, text='Edit Option', cursor='hand2')
    edit_option_btn.bind('<1>', edit_opt)
    edit_option_btn.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    edit_opt_btn_list.append(edit_option_btn)

    del_option_btn = Button(opt_btn_frame, text='Delete Option', cursor='hand2')
    del_option_btn.bind('<1>', del_opt)
    del_option_btn.grid(row=0, column=2, padx=5, pady=5, sticky='w')
    del_opt_btn_list.append(del_option_btn)

    set_ans_btn = Button(opt_btn_frame, text='Set Answer', cursor='hand2')
    set_ans_btn.bind('<1>', set_ans)
    set_ans_btn.grid(row=0, column=3, padx=5, pady=5, sticky='w')
    set_ans_list.append(set_ans_btn)

    change_ans_btn = Button(opt_btn_frame, text='Change Answer', cursor='hand2')
    change_ans_btn.bind('<1>', change_ans)
    change_ans_btn_list.append(change_ans_btn)
    added_new_change_ans_btn.append(change_ans_btn)

    # Dynamically updating the scrollbar when more question are added
    edit_root.update()
    edit_canvas.configure(scrollregion=edit_canvas.bbox('all'))
    return 'break'


def del_qn():
    global num_of_questions
    global qn_lbl_list
    global qn_Ent_list
    global qn_len_list
    global all_opt_lbl_list
    global opt_variables_list
    global opt_frame_list
    global opt_btn_frame_list
    global all_opt_list
    global add_opt_btn_list
    global edit_opt_btn_list
    global del_opt_btn_list
    global change_ans_btn_list
    global current_ans_lbl_list
    global edit_canvas

    if not num_of_questions:
        messagebox.showwarning('Alert', 'No more question to be deleted.')
        edit_root.after(1, lambda: edit_root.focus_force())
        return 'break'
    qn_num = simpledialog.askinteger("Delete Question", "Which question would you like to delete?",
                                     parent=edit_second_frame, minvalue=1, maxvalue=num_of_questions)
    if not qn_num:
        edit_root.after(1, lambda: edit_root.focus_force())
        return 'break'
    if qn_num < num_of_questions:
        for qn in range(qn_num, num_of_questions):
            update_qn_num = qn_lbl_list[qn]
            update_qn_num.configure(text=f'Question {qn})')

    # Retrieve all widgets pertaining to selected question
    chosen_qn_lbl = qn_lbl_list[qn_num - 1]
    chosen_qn_ent = qn_Ent_list[qn_num - 1]
    chosen_qn_len = qn_len_list[qn_num - 1]
    chosen_qn_opt_frame = opt_frame_list[qn_num - 1]
    chosen_qn_opt_btn_frame = opt_btn_frame_list[qn_num - 1]

    # Remove from the system lists
    qn_lbl_list.remove(chosen_qn_lbl)
    qn_Ent_list.remove(chosen_qn_ent)
    qn_len_list.remove(chosen_qn_len)
    opt_frame_list.remove(chosen_qn_opt_frame)
    opt_btn_frame_list.remove(chosen_qn_opt_btn_frame)

    # Widgets will be removed by removing its frame
    all_opt_lbl_list.pop(qn_num - 1)
    all_opt_list.pop(qn_num - 1)
    opt_variables_list.pop(qn_num - 1)
    add_opt_btn_list.pop(qn_num - 1)
    edit_opt_btn_list.pop(qn_num - 1)
    del_opt_btn_list.pop(qn_num - 1)
    change_ans_btn_list.pop(qn_num - 1)
    current_ans_lbl_list.pop(qn_num - 1)

    # Remove these widgets
    chosen_qn_lbl.destroy()
    chosen_qn_ent.destroy()
    chosen_qn_len.destroy()
    chosen_qn_opt_frame.destroy()
    chosen_qn_opt_btn_frame.destroy()

    num_of_questions -= 1

    # Dynamically updating the scrollbar when more question are added
    edit_root.update()
    edit_canvas.configure(scrollregion=edit_canvas.bbox('all'))
    edit_second_frame.after(1, lambda: edit_second_frame.focus_set())
    return 'break'


def set_ans(e):
    global set_ans_count
    global opt_frame_list
    index = set_ans_list.index(e.widget)
    if not added_new_qn_opt_list[index]:
        messagebox.showinfo('Set Options', 'Please set your options first.')
        edit_root.after(1, lambda: edit_root.focus_force())
        return 'break'
    ans = simpledialog.askinteger('Answer', 'Type in your Answer',
                                  parent=edit_second_frame, minvalue=1, maxvalue=len(added_new_qn_opt_list[index]))
    if not ans:
        return 'break'
    e.widget.grid_forget()
    corr_ans_list.append(ans)
    added_new_ans_lbl_list[index].config(text=u'\u2713')
    added_new_ans_lbl_list[index].grid(row=ans - 1, column=2, padx=5, pady=3, sticky='e')
    added_new_change_ans_btn[index].grid(row=0, column=4, padx=5, pady=3, sticky='w')
    set_ans_count += 1
    return 'break'


def change_ans(event):
    qn = change_ans_btn_list.index(event.widget)
    chosen_qn_ans = corr_ans_list[qn]
    chosen_qn_ans_lbl = current_ans_lbl_list[qn]
    chosen_options = all_opt_list[qn]
    new_ans = simpledialog.askinteger('Change Answer', 'Which option will be the answer?',
                                      parent=edit_second_frame, minvalue=1, maxvalue=len(chosen_options),
                                      initialvalue=chosen_qn_ans)
    if not new_ans:
        return 'break'
    chosen_qn_ans_lbl.grid_forget()
    chosen_qn_ans_lbl.config(text=u'\u2713')
    chosen_qn_ans_lbl.grid(row=new_ans - 1, column=2, padx=5, pady=3, sticky='e')
    corr_ans_list[qn] = new_ans
    return 'break'


def save_record(refresh_btn):
    unset_opt = [i for i in unset_choice_options_list if i]
    if len(set_ans_list) != set_ans_count or unset_opt:
        messagebox.showerror('Error', 'Please ensure all answers are set')
        edit_root.after(1, lambda: edit_root.focus_force())
        return
    for qn_ent in qn_Ent_list:
        if not qn_ent.get():
            messagebox.showerror('Error', 'Please fill in all the questions')
            edit_root.after(1, lambda: edit_root.focus_force())
            return
    with conn:
        c.execute("DELETE FROM questions WHERE question_title=:qn_title", {'qn_title': question_num_title[0]})
        datetime_SG = datetime.now(tz_SG)
        date_time = datetime_SG.strftime("%d/%m/%Y, %H:%M:%S")
        for qns in range(num_of_questions):
            options = all_opt_list[qns]
            for i in range(len(options)):
                c.execute("INSERT INTO questions VALUES(:qn_title, :new_qn, :opt_num, :opt_desc, :ans, :date_time)",
                          {
                              'opt_desc':  options[i].cget('text'),
                              'qn_title': question_num_title[0],
                              'new_qn': qn_Ent_list[qns].get(),
                              'opt_num': i + 1,
                              'ans': corr_ans_list[qns],
                              'date_time': date_time
                          })
    conn.close()
    edit_root.destroy()
    refresh_btn.invoke()
    return 'break'
