from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from ttkthemes import themed_tk as tk
from datetime import datetime
import pytz
import storeQn
import pickQn
import sqlite3
import account
import styles
import scores

# conn = sqlite3.connect(':memory:')
conn = sqlite3.connect('questions.db')
c = conn.cursor()
conn_a = sqlite3.connect('accounts.db')
c_a = conn_a.cursor()
# c.execute("DROP TABLE questions")
# c.execute("""CREATE TABLE questions(
#             question_title TEXT,
#             question TEXT,
#             option_num INT,
#             option TEXT,
#             answer INT,
#             date_time TEXT,
# )""")
# conn.commit()
# conn.close()

answered_option_list = []
corr_ans_list = []
res_list = []
opt_frame_list = []
questions_displayed = False
tz_SG = pytz.timezone('Asia/Singapore')


# Slide bar and using mousewheel to scroll
def onMouseWheel(event, main_canvas):
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


def boundToMouseWheel(main_canvas, main_second_frame):
    main_canvas.bind("<MouseWheel>", lambda e: onMouseWheel(e, main_canvas))
    main_second_frame.bind("<MouseWheel>", lambda e: onMouseWheel(e, main_canvas))


def unboundToMouseWheel(main_canvas, main_second_frame):
    main_canvas.unbind("<MouseWheel>")
    main_second_frame.unbind("<MouseWheel>")


def onFrameConfigure(main_canvas, main_second_frame):
    main_canvas.configure(scrollregion=main_second_frame.bbox('all'))


def onCanvasConfigure(main_canvas, main_second_frame_id):
    main_canvas.itemconfigure(main_second_frame_id, width=main_canvas.winfo_width() - 5)


def reset_scrollregion(main_canvas):
    main_canvas.configure(scrollregion=main_canvas.bbox('all'))


def display_qns(database, open_root, acc, main_page_lbl):
    global opt_frame
    global row
    global answered_option_list
    global corr_ans_list
    global opt_frame_list
    global selected_questions
    global num_of_questions
    global submit_btn
    global close_btn
    global reset_choice
    global questions_displayed
    global rad_style

    if not database.selection():
        messagebox.showerror('Error', 'Please select a question.')
        open_root.after(1, lambda: open_root.focus_force())
        return
    answered_option_list.clear()
    corr_ans_list.clear()

    if questions_displayed:
        root.winfo_children()[-1].destroy()
        questions_displayed = False
    else:
        main_page_lbl.grid_forget()

    '''Creating a scrollbar'''
    # Create a main frame
    main_root_frame = Frame(root)
    main_root_frame.grid(row=2, column=0, sticky='nsew')

    # Create a canvas
    main_canvas = Canvas(main_root_frame)
    main_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    # Add a Scrollbar to the Canvas
    main_scrollbar = Scrollbar(main_root_frame, orient=VERTICAL, command=main_canvas.yview)
    main_scrollbar.pack(side=RIGHT, fill=Y)

    # Configure the Canvas
    main_canvas.config(yscrollcommand=main_scrollbar.set)
    main_canvas.bind('<Enter>', lambda e: boundToMouseWheel(main_canvas, main_second_frame))
    main_canvas.bind('<Leave>', lambda e: unboundToMouseWheel(main_canvas, main_second_frame))
    main_canvas.bind('<Configure>', lambda e: reset_scrollregion(main_canvas))
    main_canvas.bind('<Configure>', lambda e: onCanvasConfigure(main_canvas, main_second_frame_id))

    # Create another frame INSIDE the Canvas
    main_second_frame = Frame(main_canvas)
    main_second_frame.bind('<Configure>', lambda e: onFrameConfigure(main_canvas, main_second_frame))

    # Add that New frame to a window in the canvas, 'Second Frame' becomes you MAIN WINDOW.
    main_second_frame_id = main_canvas.create_window((0, 0), window=main_second_frame, anchor='nw')

    styles.style_widget(main_second_frame)
    question_title = database.item(database.focus())['values'][0]
    title_lbl = Label(main_second_frame, text=question_title,
                      style='QuestionHead.TLabel', anchor=CENTER)
    title_lbl.grid(row=0, column=0, columnspan=2, sticky='n', padx=5, pady=5)

    # Retrieve data of selected question
    c.execute("SELECT * FROM questions WHERE question_title=(?)", (question_title,))
    selected_questions_list = c.fetchall()
    selected_questions = []

    for i in selected_questions_list:
        if i[1] not in selected_questions:
            selected_questions.append(i[1])
    num_of_questions = database.item(database.focus())['values'][1]

    row = 1
    opt_frame_list.clear()
    for qns in range(num_of_questions):
        qn_lbl = Label(main_second_frame, text=f"Question {qns + 1}: {selected_questions[qns]}",
                       style='Questions.TLabel')
        qn_lbl.grid(row=row, column=0, sticky='w', padx=5, pady=5)

        # Keep Track of the previous grid-up labels
        row += 1
        # Frame for options
        opt_frame = Frame(main_second_frame)
        opt_frame.grid(row=row, column=0, columnspan=3, sticky='w', padx=5, pady=5)
        row += 2
        c.execute("SELECT * FROM questions WHERE question_title=(?) AND question=(?)",
                  (selected_questions_list[0][0], selected_questions[qns]))
        rec = c.fetchall()
        option_nums = IntVar(root)
        r = 0
        for i in range(len(rec)):
            # Insert radiobutton
            opt_lbl = Label(opt_frame, text=f'{i + 1})', style='Options.TLabel')
            opt = Radiobutton(opt_frame, text=rec[i][3], variable=option_nums, value=i + 1)
            opt_lbl.grid(row=r, column=0, padx=5, pady=1, sticky='w')
            opt.grid(row=r, column=1, padx=5, pady=1, sticky='w')
            r += 1
        corr_ans_list.append(rec[0][4])
        answered_option_list.append(option_nums)

        # Keep Track of the previous grid-up labels
        opt_frame_list.append(opt_frame)  # For Placing the Answer labels
    submit_btn = Button(main_second_frame, text='Submit', cursor='hand2',
                        command=lambda: tab_scores(acc, question_title, main_second_frame,
                                                   main_canvas, main_root_frame, main_page_lbl))
    submit_btn.grid(row=row, column=1, sticky='e', padx=5, pady=5)
    row += 1
    close_btn = Button(main_second_frame, text='Close Question Set', cursor='hand2',
                       command=lambda: close_qn(main_second_frame, main_root_frame, main_page_lbl))
    close_btn.grid(row=row, column=1, sticky='e', padx=5, pady=5)
    reset_choice = Button(main_second_frame, text='Reset', cursor='hand2', command=resetChoice)
    row += 1
    open_root.destroy()
    root.update()
    main_canvas.configure(scrollregion=main_canvas.bbox('all'))

    main_second_frame.grid_columnconfigure(0, weight=0)
    main_second_frame.grid_columnconfigure(1, weight=1)

    questions_displayed = True
    return 'break'


def tab_scores(acc, qn_title, main_second_frame, main_canvas, main_root_frame, main_page_lbl):
    global answered_option_list
    global opt_frame_list
    global corr_ans_list
    global row
    global retest_btn
    global close_btn
    global result
    global ans_choice_labels
    global reset_choice

    reset_choice.grid_forget()
    ans_choice_labels = []
    user_choices = []
    score = 0
    for answer in answered_option_list:
        if not answer.get():
            messagebox.showerror('Error', 'Please complete the test before you submit')
            return

    for ans in range(len(answered_option_list)):
        choice = answered_option_list[ans].get()
        correct_ans = corr_ans_list[ans]
        ans_label = Label(opt_frame_list[ans], text=u'\u2713', style='CorrectAns.TLabel')
        ans_label.grid(row=correct_ans - 1, column=2, padx=5, pady=1, sticky='e')
        ans_choice_labels.append(ans_label)
        if choice == correct_ans:
            score += 1
        else:
            choice_label = Label(opt_frame_list[ans], text=u'\u2715', style='WrongAns.TLabel')
            choice_label.grid(row=choice - 1, column=2, padx=5, pady=1, sticky='e')
            ans_choice_labels.append(choice_label)
        user_choices.append(choice)

    # Format User Choices
    user_options = ''
    for i in user_choices:
        user_options += str(i) + ','
    user_options = user_options.strip(',')

    # Format Time
    datetime_SG = datetime.now(tz_SG)
    date_time = datetime_SG.strftime("%d/%m/%Y, %H:%M:%S")

    # Open scores database
    conn_s = sqlite3.connect('scores.db')
    c_s = conn_s.cursor()

    # See if question records exist
    c_s.execute("SELECT num_attempt FROM all_scores WHERE user_id=:userid AND qn_title=:qntitle",
                {
                    'userid': acc[0],
                    'qntitle': qn_title
                })
    qn_attempt_lst = c_s.fetchall()
    # Add into records with latest attempt number
    if qn_attempt_lst:
        qn_attempt = list(qn_attempt_lst[-1])
        c_s.execute("INSERT INTO all_scores VALUES(:userid, :name, :qn_title, :no_attempt, "
                    ":score_p, :date_time, 'NULL', :user_options)",
                    {
                        'userid': acc[0],
                        'name': acc[1],
                        'qn_title': qn_title,
                        'no_attempt': qn_attempt[0] + 1,
                        'score_p': f"{round(score * 100 / len(corr_ans_list), 1)}% ({score}/{len(corr_ans_list)})",
                        'date_time': date_time,
                        'user_options': user_options
                    })
    # Add into records on 1st attempt
    else:
        c_s.execute("INSERT INTO all_scores VALUES(:userid, :name, :qn_title, :no_attempt, "
                    ":score_p, :date_time, 'NULL', :user_options)",
                    {
                        'userid': acc[0],
                        'name': acc[1],
                        'qn_title': qn_title,
                        'no_attempt': 1,
                        'score_p': f"{round(score * 100 / len(corr_ans_list), 1)}% ({score}/{len(corr_ans_list)})",
                        'date_time': date_time,
                        'user_options': user_options
                    })
    conn_s.commit()
    conn_s.close()

    result = Label(main_second_frame, text=f'You scored {score}/{len(corr_ans_list)}!', style='Typical.TLabel')
    result.grid(row=row, column=1, sticky='e', padx=5, pady=5)
    row += 1
    submit_btn.grid_forget()
    close_btn.destroy()
    retest_btn = Button(main_second_frame, text='Retest', cursor='hand2', command=Retest)
    retest_btn.grid(row=row, column=1, sticky='e', padx=5, pady=5)
    row += 1
    close_btn = Button(main_second_frame, text='Close Question Set', cursor='hand2',
                       command=lambda: close_qn(main_second_frame, main_root_frame, main_page_lbl))
    close_btn.grid(row=row, column=1, sticky='e', padx=5, pady=5)
    root.update()
    main_canvas.configure(scrollregion=main_canvas.bbox('all'))


def Retest():
    global retest_btn
    global close_btn
    global result
    global row
    global ans_choice_labels

    for i in ans_choice_labels:
        i.destroy()
    retest_btn.destroy()
    close_btn.destroy()
    result.destroy()
    row -= 1
    reset_choice.grid(row=row, column=1, sticky='e', padx=5, pady=5)
    row += 1
    submit_btn.grid(row=row, column=1, sticky='e', padx=5, pady=5)


def resetChoice():
    global answered_option_list
    global reset_choice

    for ans in answered_option_list:
        ans.set(None)
    reset_choice.grid_forget()


def close_qn(main_second_frame, main_root_frame, main_page_lbl):
    global opt_frame_list

    opt_frame_list.clear()
    main_second_frame.destroy()
    main_page_lbl.grid(row=2, column=0, sticky='nsew')
    main_root_frame.destroy()


def on_closing():
    conn.close()
    conn_a.close()
    root.destroy()


def main(acc):
    global root

    acc = list(acc)

    # Main Page
    root = tk.ThemedTk()
    root.get_themes()
    root.set_theme(styles.MAIN_THEME)
    root.title('Questions')
    root.iconbitmap('main_qn.ico')
    root.after(1, root.focus_force())

    app_width = 800
    app_height = 700

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)
    root.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

    root.rowconfigure([0, 1], weight=0)
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    root.minsize(app_width, app_height)

    # Widget Styling
    styles.style_widget(root)

    # Button Widgets
    qns_btn_frame = Frame(root, style='TopButtons.TFrame')
    qns_btn_frame.grid(row=0, column=0, sticky='new')
    set_qns = Button(qns_btn_frame, text='Set New Questions', cursor='hand2', command=storeQn.SetQns)
    open_qns = Button(qns_btn_frame, text='Retrieve/Open Questions', cursor='hand2',
                      command=lambda: pickQn.OpenQns(acc, main_page_lbl))
    edit_qns = Button(qns_btn_frame, text='Edit Questions', cursor='hand2',
                      command=lambda: pickQn.OpenEditQns(acc, main_page_lbl))
    view_score_btn = Button(qns_btn_frame, text='View Scores', cursor='hand2',
                            command=lambda: scores.view_score(root, main_page_lbl))

    # User Name
    user_frame = Frame(root, style='TopButtons.TFrame')
    user_name = Label(user_frame, text=f'Welcome, {acc[1]}!', style='Username.TLabel')
    log_out_btn = Button(user_frame, text='Log Out', cursor='hand2', command=lambda: account.log_out(root))
    user_frame.grid(row=1, column=0, sticky='ew')
    user_name.grid(row=0, column=0, sticky='w', pady=3, padx=5)
    log_out_btn.grid(row=0, column=1, sticky='e', pady=3, padx=5)

    user_frame.grid_columnconfigure(1, weight=1)

    # Create Menu Bar
    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    maintain_menu = Menu(menu_bar, tearoff=0, font=('Times', 10))

    # Grid up the widgets
    if acc[3] == 'Teacher' or acc[3] == 'Admin':
        open_qns.grid(row=0, column=0, sticky='nw', padx=5, pady=5)
        set_qns.grid(row=0, column=1, sticky='nw', padx=5, pady=5)
        edit_qns.grid(row=0, column=2, sticky='nw', padx=5, pady=5)
        view_score_btn.grid(row=0, column=3, sticky='nw', padx=5, pady=5)
        maintain_menu.add_command(label="All User Account Setting",
                                  command=lambda: account.all_user_setting(root, acc))

    else:
        open_qns.grid(row=0, column=0, sticky='nw', padx=5, pady=5)
        view_score_btn.grid(row=0, column=1, sticky='nw', padx=5, pady=5)

    maintain_menu.add_command(label="User Account Setting",
                              command=lambda: account.user_setting(root, account=acc))

    maintain_menu.add_command(label="Log Out", command=lambda: account.log_out(root))
    menu_bar.add_cascade(label="Account", menu=maintain_menu)

    main_page_lbl = Label(root, text='No Question On Display', style='MainPage.TLabel')
    main_page_lbl.grid(row=2, column=0, sticky='nsew')

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
