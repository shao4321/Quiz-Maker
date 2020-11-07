from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from ttkthemes import themed_tk as tk
import sqlite3
import styles
import qns


def view_score(root, main_page_lbl):
    global score_page
    global conn_s
    global c_s

    score_page = tk.ThemedTk()
    score_page.get_themes()
    score_page.set_theme(styles.MAIN_THEME)
    score_page.title('Score Tabulation')
    score_page.iconbitmap('main_qn.ico')
    score_page.after(1, score_page.focus_force())

    # Widget Styles
    styles.style_widget(score_page)

    # Treeview Column Widths
    col_width_no = 70
    col_width_userid = 150
    col_width_name = 200
    col_width_qn_title = 180
    col_width_num_attempt = 100
    col_width_score = 250
    col_width_datetime = 250
    col_width_total = sum([col_width_no, col_width_userid, col_width_name, col_width_qn_title,
                           col_width_num_attempt, col_width_score, col_width_datetime])
    tv_anchor = 'center'

    # Windows size configuration
    app_width = col_width_total + 50
    app_height = 400

    screen_width = score_page.winfo_screenwidth()
    screen_height = score_page.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)
    score_page.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

    score_page.rowconfigure(0, weight=1)
    score_page.columnconfigure(0, weight=1)

    tree_frame = Frame(score_page)
    tree_frame.grid(row=0, column=0, sticky='nsew')
    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)
    score_db = Treeview(tree_frame, yscrollcommand=tree_scroll.set)
    score_db.bind('<Double-1>', lambda e: display_past_qn(root, main_page_lbl, score_db))
    score_db.pack(fill=BOTH, expand=1)
    tree_scroll.config(command=score_db.yview)

    # Create striped row tags
    score_db.tag_configure('evenrow', background=styles.treeview_even_row)
    score_db.tag_configure('oddrow', background=styles.treeview_odd_row)

    # Retrieve all users from accounts db
    conn_a = sqlite3.connect('accounts.db')
    c_a = conn_a.cursor()
    c_a.execute("SELECT user_id FROM accounts")
    all_users_list = c_a.fetchall()
    all_users_list = [i[0] for i in all_users_list]

    # Retrieve data from scores db
    conn_s = sqlite3.connect('scores.db')
    c_s = conn_s.cursor()

    score_db['columns'] = ('User ID', 'Name', 'Qn_Title', 'No_Attempt', 'Score_P', 'Done_on')

    # Format Our Columns

    score_db.column('#0', width=col_width_no)
    score_db.column('User ID', width=col_width_userid)
    score_db.column('Name', width=col_width_name)
    score_db.column('Qn_Title', width=col_width_qn_title)
    score_db.column('No_Attempt', width=col_width_num_attempt)
    score_db.column('Score_P', width=col_width_score)
    score_db.column('Done_on', width=col_width_datetime)

    # Create Headings
    score_db.heading('#0', text='No.', anchor=tv_anchor)
    score_db.heading('User ID', text='User ID', anchor=tv_anchor)
    score_db.heading('Name', text='Name', anchor=tv_anchor)
    score_db.heading('Qn_Title', text='Question Title', anchor=tv_anchor)
    score_db.heading('No_Attempt', text='Attempt(s)', anchor=tv_anchor)
    score_db.heading('Score_P', text='Score Points', anchor=tv_anchor)
    score_db.heading('Done_on', text='Done On', anchor=tv_anchor)

    cnt = 0
    for user in all_users_list:
        c_s.execute("SELECT * FROM all_scores WHERE user_id=:userid", {'userid': user})
        user_score_lst = c_s.fetchall()
        qn_num_user_did_id_dict = {}
        for rec in range(len(user_score_lst)):
            if user_score_lst[rec]:
                current_qn = user_score_lst[rec][2]
                if current_qn in qn_num_user_did_id_dict:
                    score_db.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                                    values=(user_score_lst[rec][0], user_score_lst[rec][1], current_qn,
                                            user_score_lst[rec][3], user_score_lst[rec][4],
                                            user_score_lst[rec][5]), tags=('oddrow',))
                    with conn_s:
                        c_s.execute("UPDATE all_scores SET tv_id=:tv_id WHERE "
                                    "user_id=:userid AND qn_title=:qn_title AND num_attempt=:num_attempt",
                                    {
                                        'tv_id': cnt,
                                        'userid': user,
                                        'qn_title': current_qn,
                                        'num_attempt': user_score_lst[rec][3]
                                    })
                    for qn_id in qn_num_user_did_id_dict[current_qn]:
                        score_db.move(qn_id, cnt, 'end')
                        score_db.item(qn_id, tags=('oddrow',))
                    score_db.item(cnt, tags=('evenrow',))
                    qn_num_user_did_id_dict[current_qn].append(cnt)
                else:
                    score_db.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                                    values=(user_score_lst[rec][0], user_score_lst[rec][1], current_qn,
                                            user_score_lst[rec][3], user_score_lst[rec][4],
                                            user_score_lst[rec][5]), tags=('oddrow',))
                    with conn_s:
                        c_s.execute("UPDATE all_scores SET tv_id=:tv_id WHERE "
                                    "user_id=:userid AND qn_title=:qn_title AND num_attempt=:num_attempt",
                                    {
                                        'tv_id': cnt,
                                        'userid': user,
                                        'qn_title': current_qn,
                                        'num_attempt': user_score_lst[rec][3]
                                    })
                    qn_num_user_did_id_dict[current_qn] = [cnt]
                cnt += 1
        qn_num_user_did_id_dict.clear()

    btn_frame = Frame(score_page)
    select_btn = Button(btn_frame, text='Select', cursor='hand2',
                        command=lambda: display_past_qn(root, main_page_lbl, score_db))
    delete_btn = Button(btn_frame, text='Delete', cursor='hand2',
                        command=lambda: del_record(score_db))
    btn_frame.grid(row=1, column=0, sticky='ew')
    select_btn.grid(row=0, column=0, sticky='e', padx=3, pady=3)
    delete_btn.grid(row=0, column=1, sticky='e', padx=3, pady=3)

    btn_frame.grid_columnconfigure(0, weight=1)

    conn_a.close()
    conn_s.commit()

    score_page.protocol("WM_DELETE_WINDOW", on_closing)

    return 'break'


def del_record(s_db):
    sel_rows = s_db.selection()
    for sel_row in sel_rows:
        sel_row_children = s_db.get_children(sel_row)
        if sel_row_children:
            s_db.move(sel_row_children[-1], '', s_db.index(sel_row))
            s_db.item(sel_row_children[-1], tags=('evenrow',))
            for child in sel_row_children[:-1]:
                s_db.move(child, sel_row_children[-1], 'end')
        with conn_s:
            c_s.execute("DELETE FROM all_scores WHERE "
                        "user_id=:userid AND qn_title=:qn_title AND num_attempt=:num_attempt",
                        {
                            'userid': s_db.item(sel_row)['values'][0],
                            'qn_title': s_db.item(sel_row)['values'][2],
                            'num_attempt': s_db.item(sel_row)['values'][3]
                        })
        s_db.delete(sel_row)
    return 'break'


def display_past_qn(root, main_page_lbl, s_db):
    global main_root_frame
    global conn

    if len(s_db.selection()) > 1:
        messagebox.showerror('Error', 'Please select only 1 question record.')
        score_page.after(1, score_page.focus_force())
        return

    cur_item = s_db.focus()
    if not cur_item:
        messagebox.showerror('Error', 'Please select a question record.')
        score_page.after(1, score_page.focus_force())
        return

    main_page_lbl.grid_forget()

    with conn_s:
        c_s.execute("SELECT user_options FROM all_scores WHERE user_id=:userid AND qn_title=:qn_title "
                    "AND num_attempt=:num_attempt",
                    {
                        'userid': s_db.item(cur_item)['values'][0],
                        'qn_title': s_db.item(cur_item)['values'][2],
                        'num_attempt': s_db.item(cur_item)['values'][3]
                    })
    user_choices = c_s.fetchone()
    user_choices = user_choices[0].split(',')
    if qns.questions_displayed:
        root.winfo_children()[-1].destroy()
        qns.questions_displayed = False

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
    main_canvas.bind('<Enter>', lambda e: qns.boundToMouseWheel(main_canvas, main_second_frame))
    main_canvas.bind('<Leave>', lambda e: qns.unboundToMouseWheel(main_canvas, main_second_frame))
    main_canvas.bind('<Configure>', lambda e: qns.reset_scrollregion(main_canvas))
    main_canvas.bind('<Configure>', lambda e: qns.onCanvasConfigure(main_canvas, main_second_frame_id))

    # Create another frame INSIDE the Canvas
    main_second_frame = Frame(main_canvas)
    main_second_frame.bind('<Configure>', lambda e: qns.onFrameConfigure(main_canvas, main_second_frame))

    # Add that New frame to a window in the canvas, 'Second Frame' becomes you MAIN WINDOW.
    main_second_frame_id = main_canvas.create_window((0, 0), window=main_second_frame, anchor='nw')

    styles.style_widget(main_second_frame)

    question_title = s_db.item(cur_item)['values'][2]
    title_lbl = Label(main_second_frame, text=question_title,
                      style='QuestionHead.TLabel', anchor=CENTER)
    title_lbl.grid(row=0, column=0, columnspan=2, sticky='n', padx=5, pady=5)

    # Retrieve data of selected question
    conn = sqlite3.connect('questions.db')
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE question_title=(?)", (question_title,))
    selected_questions_list = c.fetchall()
    selected_questions = []

    for i in selected_questions_list:
        if i[1] not in selected_questions:
            selected_questions.append(i[1])
    num_of_questions = len(user_choices)

    row = 1
    for qn_num in range(num_of_questions):
        qn_lbl = Label(main_second_frame, text=f"Question {qn_num + 1}: {selected_questions[qn_num]}",
                       style='Questions.TLabel')
        qn_lbl.grid(row=row, column=0, sticky='w', padx=5, pady=5)

        # Keep Track of the previous grid-up labels
        row += 1
        # Frame for options
        opt_frame = Frame(main_second_frame)
        opt_frame.grid(row=row, column=0, columnspan=3, sticky='w', padx=5, pady=5)
        row += 2
        c.execute("SELECT * FROM questions WHERE question_title=(?) AND question=(?)",
                  (selected_questions_list[0][0], selected_questions[qn_num]))
        rec = c.fetchall()
        correct_ans = rec[0][4]
        option_nums = IntVar(root)
        r = 0
        for i in range(len(rec)):
            # Insert radiobutton
            opt_lbl = Label(opt_frame, text=f'{i + 1})', style='Options.TLabel')
            opt = Radiobutton(opt_frame, text=rec[i][3], variable=option_nums, value=i + 1)
            opt_lbl.grid(row=r, column=0, padx=5, pady=1, sticky='w')
            opt.grid(row=r, column=1, padx=5, pady=1, sticky='w')
            r += 1
        choice = int(user_choices[qn_num])
        option_nums.set(choice)
        ans_label = Label(opt_frame, text=u'\u2713', style='CorrectAns.TLabel')
        ans_label.grid(row=correct_ans - 1, column=2, padx=5, pady=1, sticky='e')
        if choice != correct_ans:
            wrong_ans_lbl = Label(opt_frame, text=u'\u2715', style='WrongAns.TLabel')
            wrong_ans_lbl.grid(row=choice - 1, column=2, padx=5, pady=1, sticky='e')

    row += 1
    close_btn = Button(main_second_frame, text='Close Question Set', cursor='hand2',
                       command=lambda: close_qn(main_page_lbl, main_second_frame))
    close_btn.grid(row=row, column=1, sticky='e', padx=5, pady=5)

    root.update()
    main_canvas.configure(scrollregion=main_canvas.bbox('all'))

    main_second_frame.grid_columnconfigure(0, weight=0)
    main_second_frame.grid_columnconfigure(1, weight=1)

    qns.questions_displayed = True

    main_root_frame.after(1, main_root_frame.focus_force())
    return 'break'


def close_qn(main_page_lbl, main_second_frame):
    main_second_frame.destroy()
    main_page_lbl.grid(row=2, column=0, sticky='nsew')
    main_root_frame.destroy()
    return 'break'


def on_closing():
    conn_s.close()
    score_page.destroy()
