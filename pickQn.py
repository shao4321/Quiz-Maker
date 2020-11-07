from tkinter import *
from tkinter.ttk import *
from ttkthemes import themed_tk as tk
from tkinter import simpledialog
from tkinter import messagebox
from datetime import datetime
import pytz
import qns
import edit
import sqlite3
import styles

conn = sqlite3.connect('questions.db')
c = conn.cursor()

qn_to_datetime = dict()
datetime_to_qns = dict()
tz_SG = pytz.timezone('Asia/Singapore')


def on_keyrelease(event, db):
    # get text from entry
    val = event.widget.get()
    val = val.strip().lower()

    # get title from database
    if val == '':
        qns = qn_to_datetime
    else:
        qns = dict()
        for key, value in qn_to_datetime.items():
            if val in key.lower():
                qns[key] = value

    # update data in treeview
    treeview_update(qns, db)


def treeview_update(qns, db):
    # delete previous data
    for data in db.get_children():
        db.delete(data)

    # Place filtered data
    cnt = 0
    for key, value in qns.items():
        if cnt % 2 == 0:
            db.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                      values=(key, len(datetime_to_qns[value]), value), tags=('evenrow',))
        else:
            db.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                      values=(key, len(datetime_to_qns[value]), value), tags=('oddrow',))
        cnt += 1


def treeview_sort_column_by_no(tv, col, reverse):
    lst = [(tv.item(k)["text"], k) for k in tv.get_children()]
    lst.sort(key=lambda t: t[0], reverse=reverse)

    for index, (val, k) in enumerate(lst):
        tv.move(k, '', index)
        if index % 2 == 0:
            tv.item(k, tags='evenrow')
        else:
            tv.item(k, tags='oddrow')

    tv.heading(col, command=lambda: treeview_sort_column_by_no(tv, col, not reverse))


def treeview_sort_column_by_db_col(tv, col, idx, reverse):
    lst = [(tv.item(k)["values"][idx], k) for k in tv.get_children()]
    lst.sort(key=lambda t: t[0], reverse=reverse)

    for index, (val, k) in enumerate(lst):
        tv.move(k, '', index)
        if index % 2 == 0:
            tv.item(k, tags='evenrow')
        else:
            tv.item(k, tags='oddrow')

    tv.heading(col, command=lambda: treeview_sort_column_by_db_col(tv, col, idx, not reverse))


def treeview_sort_column_by_datetime(tv, col, reverse):
    global qn_to_datetime
    lst = [(datetime.strptime(tv.item(k)["values"][2], "%d/%m/%Y, %H:%M:%S"), k) for k in tv.get_children()]
    lst.sort(key=lambda t: t[0], reverse=reverse)

    for index, (val, k) in enumerate(lst):
        tv.move(k, '', index)
        if index % 2 == 0:
            tv.item(k, tags='evenrow')
        else:
            tv.item(k, tags='oddrow')

    tv.heading(col, command=lambda: treeview_sort_column_by_datetime(tv, col, not reverse))


def OpenQns(acc, main_page_lbl):
    global database
    global open_root
    global database_dict
    global row_open_root
    global select_btn
    global remove_qn_btn

    open_root = tk.ThemedTk()
    open_root.get_themes()
    open_root.set_theme(styles.MAIN_THEME)
    open_root.title('Records')
    open_root.iconbitmap('main_qn.ico')
    open_root.after(1, lambda: open_root.focus_force())
    row_open_root = 0

    app_width2 = 900
    app_height2 = 600

    screen_width2 = open_root.winfo_screenwidth()
    screen_height2 = open_root.winfo_screenheight()

    x2 = (screen_width2 / 2) - (app_width2 / 2)
    y2 = (screen_height2 / 2) - (app_height2 / 2)
    open_root.geometry(f"{app_width2}x{app_height2}+{int(x2)}+{int(y2)}")

    # Styling
    styles.style_widget(open_root)

    search_bar_lbl = Label(open_root, text='Search for question title:', style='QuestionHead.TLabel')
    search_bar = Entry(open_root, font=('Helvetica', 20))
    remove_qn_btn = Button(open_root, text='Remove Question', cursor='hand2', command=lambda: remove_qns(acc))
    select_btn = Button(open_root, text='Select', cursor='hand2')
    select_btn.bind('<1>', lambda e: qns.display_qns(database, open_root, acc))
    questions_frame = Frame(open_root)
    title = Label(questions_frame, text='All Recorded Questions', style='QuestionHead.TLabel')

    tree_frame = Frame(questions_frame)
    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)
    database = Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode='browse')
    database.bind('<Return>', lambda e: qns.display_qns(database, open_root, acc, main_page_lbl))
    database.bind('<Double-1>', lambda e: qns.display_qns(database, open_root, acc, main_page_lbl))
    database.bind('<Escape>', lambda e: refresh_tv())
    database.pack()
    tree_scroll.config(command=database.yview)

    # Create striped row tags
    database.tag_configure('evenrow', background=styles.treeview_even_row)
    database.tag_configure('oddrow', background=styles.treeview_odd_row)

    # Retrieve data from database
    c.execute("SELECT question_title, question, date_time FROM questions")
    records = c.fetchall()
    qn_to_datetime.clear()
    datetime_to_qns.clear()
    for rec in records:
        if qn_to_datetime.get(rec[0]):
            if datetime_to_qns.get(rec[2]):
                if rec[1] not in datetime_to_qns.get(rec[2]):
                    datetime_to_qns[rec[2]].append(rec[1])
        else:
            qn_to_datetime[rec[0]] = rec[2]
            datetime_to_qns[rec[2]] = [rec[1]]

    database['columns'] = ('Title Of Question', 'No. Of Questions', 'Date Modified')
    # Format Our Columns
    database.column('#0', anchor=W, width=50)
    database.column('Title Of Question', anchor=W, width=330)
    database.column('No. Of Questions', anchor=W, width=180)
    database.column('Date Modified', anchor=W, width=300)
    # Create Headings
    database.heading('#0', text='No.', anchor=W,
                     command=lambda: treeview_sort_column_by_no(database, "#0", False))
    database.heading('Title Of Question', text='Title Of Question', anchor=W,
                     command=lambda: treeview_sort_column_by_db_col(database, "Title Of Question", 0, False))
    database.heading('No. Of Questions', text='No. Of Questions', anchor=W,
                     command=lambda: treeview_sort_column_by_db_col(database, "No. Of Questions", 1, False))
    database.heading('Date Modified', text='Date Modified', anchor=W,
                     command=lambda: treeview_sort_column_by_datetime(database, "Date Modified", False))
    cnt = 0
    database_dict = dict()
    for key, value in qn_to_datetime.items():
        if cnt % 2 == 0:
            database.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                            values=(key, len(datetime_to_qns[value]), value), tags=('evenrow',))
        else:
            database.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                            values=(key, len(datetime_to_qns[value]), value), tags=('oddrow',))
        database_dict[cnt + 1] = key
        cnt += 1

    search_bar.bind('<KeyRelease>', lambda e: on_keyrelease(e, database))
    # Grid up the main widgets
    search_bar_lbl.grid(row=row_open_root, column=0, sticky='w', padx=5, pady=5)
    row_open_root += 1
    search_bar.grid(row=row_open_root, column=0, sticky='ew', padx=5, pady=5)
    row_open_root += 1
    questions_frame.grid(row=row_open_root, column=0, sticky='nsew', padx=5, pady=5)
    row_open_root += 1
    select_btn.grid(row=row_open_root, column=0, sticky='e', padx=5, pady=5)

    # Grid up the frame widgets
    title.grid(row=0, column=0, sticky='n', padx=5, pady=5)
    tree_frame.grid(row=1, column=0, sticky='n', padx=5, pady=5)

    # Set configuration to windows expansion
    open_root.rowconfigure([i for i in range(row_open_root + 1)], minsize=50, weight=1)
    open_root.columnconfigure(0, minsize=50, weight=1)
    open_root.minsize(600, 600)


def OpenEditQns(acc, main_page_lbl):
    global database
    global row_open_root
    global select_btn

    OpenQns(acc, main_page_lbl)
    select_btn.grid_forget()

    remove_qn_btn.grid(row=row_open_root, column=0, sticky='nsew', padx=5, pady=5)
    row_open_root += 1
    select_btn.grid(row=row_open_root, column=0, sticky='e', padx=5, pady=5)

    database.config(selectmode='extended')
    database.bind('<3>', lambda e: onRight(e, acc, main_page_lbl))
    database.bind('<Return>', lambda e: edit.Edit_Qn(e, refresh_btn))
    database.bind('<Double-1>', lambda e: edit.Edit_Qn(e, refresh_btn))

    refresh_btn = Button(open_root, text='Refresh', command=lambda: refresh_open_qns(acc, main_page_lbl))
    return 'break'


def refresh_open_qns(acc, main_page_lbl):
    open_root.destroy()
    OpenEditQns(acc, main_page_lbl)
    return


def refresh_tv():
    for item in database.selection():
        database.selection_remove(item)


# Function for popup menu
def onRight(event, acc, main_page_lbl):
    # Define the popup menu
    pop_menu = Menu(open_root, tearoff=0, font=('Helvetica', 10), activebackground='grey')
    pop_menu.add_command(label='Select All', command=select_all)
    if len(database.selection()) == 1:
        pop_menu.add_command(label='Rename Title', command=lambda: rename_title(acc))
    if database.selection():
        pop_menu.add_separator()
        pop_menu.add_command(label='Remove Question', command=lambda: remove_qns(acc, main_page_lbl))

    # display the popup menu
    try:
        pop_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        # make sure to release the grab (Tk 8.0a1 only)
        pop_menu.grab_release()


def select_all():
    for data in database.get_children():
        database.focus(data)
        database.selection_add(data)


def remove_qns(acc, main_page_lbl):
    global database
    response = messagebox.askyesno('Delete', 'Are you sure you want to delete the questions?')
    if response:
        qn_titles_list = []
        for qn in database.selection():
            qn_title = database_dict[int(qn) + 1]
            qn_titles_list.append(qn_title)
            database.delete(qn)
        with conn:
            for qnt in qn_titles_list:
                c.execute("DELETE FROM questions WHERE question_title=:qn_title", {'qn_title': qnt})
    refresh_open_qns(acc, main_page_lbl)
    return 'break'


def rename_title(acc):
    cur_item = database.focus()
    selected_title = database.item(cur_item)['values'][0]
    new_title = simpledialog.askstring('Change Title', 'Enter the new title',
                                       parent=open_root, initialvalue=selected_title)
    if not new_title:
        return
    datetime_SG = datetime.now(tz_SG)
    date_time = datetime_SG.strftime("%d/%m/%Y, %H:%M:%S")
    with conn:
        c.execute("UPDATE questions SET question_title=:qn_title, date_time=:date_time WHERE question_title=:sel_title",
                  {
                      'qn_title': new_title,
                      'date_time': date_time,
                      'sel_title': selected_title
                  })
    refresh_open_qns(acc)
    return 'break'
