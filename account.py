from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from ttkthemes import themed_tk as tk
import sqlite3
import qns
import login
import styles
import pickQn

conn_a = sqlite3.connect('accounts.db')
c_a = conn_a.cursor()
access_levels = ['Student', 'Teacher', 'Admin']


def on_quit(page):
    page.destroy()
    return 'break'


def log_out(root):
    root.destroy()
    login.main()
    return 'break'


def update_user_details(account):
    global user_id_ent
    global user_name_ent
    global user_pw_ent
    global user_lvl_ent

    with conn_a:
        c_a.execute("UPDATE accounts SET user_id=:userid, name=:name, password=:pw, access_level=:al "
                    "WHERE user_id=:old_userid",
                    {
                        'userid': user_id_ent.get(),
                        'name': user_name_ent.get(),
                        'pw': user_pw_ent.get(),
                        'al': user_lvl_ent.get(),
                        'old_userid': account[0]
                    })
    account[0] = user_id_ent.get()
    account[1] = user_name_ent.get()
    account[2] = user_pw_ent.get()
    account[3] = user_lvl_ent.get()
    user_set_page.destroy()


def update_one_user(root, account):
    update_user_details(account)
    root.destroy()
    qns.main(account)


def update_many_user(root, account):
    update_user_details(account)
    all_user_set_page.destroy()
    all_user_setting(root, account)


def user_setting(root, account=None, acc_db=None):
    global user_set_page
    global user_id_ent
    global user_name_ent
    global user_pw_ent
    global user_lvl_ent
    global update_btn
    global acc

    if acc_db:
        cur_item = acc_db.focus()
        if not cur_item:
            messagebox.showerror('Error', 'Please select a user.')
            return

    user_set_page = tk.ThemedTk()
    user_set_page.get_themes()
    user_set_page.set_theme(styles.MAIN_THEME)
    user_set_page.title('User Settings')
    user_set_page.iconbitmap('main_qn.ico')

    # Widget Styles
    styles.style_widget(user_set_page)
    ul_padding_y = 3
    ul_padding_x = 6
    ul_df_row = 0

    # Windows size configuration
    app_width = 350
    app_height = 400

    screen_width = user_set_page.winfo_screenwidth()
    screen_height = user_set_page.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)
    user_set_page.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

    user_set_page.rowconfigure(0, weight=1)
    user_set_page.columnconfigure(0, weight=1)

    user_details_frame = LabelFrame(user_set_page, text='Your account details:')
    user_id_lbl = Label(user_details_frame, text='User ID:')
    user_id_ent = Entry(user_details_frame, font=styles.t_ent_font)
    user_name_lbl = Label(user_details_frame, text='Name:')
    user_name_ent = Entry(user_details_frame, font=styles.t_ent_font)
    user_pw_lbl = Label(user_details_frame, text='Password')
    user_pw_ent = Entry(user_details_frame, font=styles.t_ent_font)
    user_lvl_lbl = Label(user_details_frame, text='Access Level')
    user_lvl_ent = Combobox(user_details_frame, font=styles.t_ent_font, width=12, value=access_levels)
    update_btn = Button(user_details_frame, text='Update', cursor='hand2',
                        command=lambda: update_one_user(root, account))
    cancel_btn = Button(user_details_frame, text='Cancel', cursor='hand2')
    cancel_btn.bind('<1>', lambda e: on_quit(user_set_page))

    if account:
        user_id_ent.insert(0, account[0])
        user_name_ent.insert(0, account[1])
        user_pw_ent.insert(0, account[2])
        user_lvl_ent.set(account[3])

        if account[3] == 'Student':
            user_lvl_ent.configure(state='disabled')

    user_details_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
    user_id_lbl.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    user_id_ent.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    user_name_lbl.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    user_name_ent.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    user_pw_lbl.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    user_pw_ent.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    user_lvl_lbl.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    user_lvl_ent.grid(row=ul_df_row, column=0, columnspan=2, sticky='nw', padx=ul_padding_x, pady=ul_padding_y)
    ul_df_row += 1
    update_btn.grid(row=ul_df_row, column=0, sticky='n', pady=ul_padding_y)
    cancel_btn.grid(row=ul_df_row, column=1, sticky='n', pady=ul_padding_y)

    if not account:
        autofill_user_setting(root, acc_db)
        account = acc

    user_details_frame.grid_rowconfigure([i for i in range(ul_df_row + 1)], weight=1)
    user_details_frame.grid_columnconfigure([i for i in range(2)], weight=1)
    user_set_page.after(1, user_set_page.focus_force())


def autofill_user_setting(root, acc_db):
    global user_id_ent
    global user_name_ent
    global user_pw_ent
    global user_lvl_ent
    global update_btn
    global acc

    cur_item = acc_db.focus()
    selected_id = acc_db.item(cur_item)['values'][0]
    selected_name = acc_db.item(cur_item)['values'][1]
    selected_pw = acc_db.item(cur_item)['values'][2]
    selected_al = acc_db.item(cur_item)['values'][3]

    user_id_ent.insert(0, selected_id)
    user_name_ent.insert(0, selected_name)
    user_pw_ent.insert(0, selected_pw)
    user_lvl_ent.insert(0, selected_al)

    acc = [user_id_ent.get(), user_name_ent.get(), user_pw_ent.get(), user_lvl_ent.get()]
    update_btn.configure(command=lambda: update_many_user(root, acc))
    return


def delete_user(root, account, acc_db):
    cur_item = acc_db.focus()
    if not cur_item:
        messagebox.showerror('Error', 'Please select a user.')
        all_user_set_page.after(1, all_user_set_page.focus_force())
        return
    selected_id = acc_db.item(cur_item)['values'][0]
    ans = messagebox.askyesno('Delete User', f'Are you sure you want to delete User ID: {selected_id}?')
    if not ans:
        return
    with conn_a:
        c_a.execute("DELETE FROM accounts WHERE user_id=:userid", {'userid': selected_id})

    # Log Out if the Deleted User is the logged in user
    if selected_id == account[0]:
        all_user_set_page.destroy()
        log_out(root)
    else:
        all_user_set_page.destroy()
        all_user_setting(root, account)


def all_user_setting(root, account):
    global all_user_set_page

    all_user_set_page = tk.ThemedTk()
    all_user_set_page.get_themes()
    all_user_set_page.set_theme(styles.MAIN_THEME)
    all_user_set_page.title('All User Setting')
    all_user_set_page.iconbitmap('main_qn.ico')
    all_user_set_page.after(1, all_user_set_page.focus_force())

    # Widget Styles
    styles.style_widget(all_user_set_page)

    # Windows size configuration
    app_width = 850
    app_height = 400

    screen_width = all_user_set_page.winfo_screenwidth()
    screen_height = all_user_set_page.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)
    all_user_set_page.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

    all_user_set_page.rowconfigure(0, weight=1)
    all_user_set_page.columnconfigure(0, weight=1)

    tree_frame = Frame(all_user_set_page)
    tree_frame.grid(row=0, column=0, sticky='nsew')
    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)
    acc_db = Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode='browse')
    acc_db.bind('<Double-1>', lambda e: user_setting(root, account=None, acc_db=acc_db))
    acc_db.pack(fill=BOTH, expand=1)
    tree_scroll.config(command=acc_db.yview)

    # Create striped row tags
    acc_db.tag_configure('evenrow', background=styles.treeview_even_row)
    acc_db.tag_configure('oddrow', background=styles.treeview_odd_row)

    # Retrieve data from acc_db
    c_a.execute("SELECT * FROM accounts")
    records = c_a.fetchall()
    acc_db['columns'] = ('User ID', 'Name', 'Password', 'Access Level')

    # Format Our Columns
    acc_db.column('#0', anchor=W, width=50)
    acc_db.column('User ID', anchor=W, width=150)
    acc_db.column('Name', anchor=W, width=260)
    acc_db.column('Password', anchor=W, width=200)
    acc_db.column('Access Level', anchor=W, width=150)

    # Create Headings
    acc_db.heading('#0', text='No.', anchor=W,
                   command=lambda: pickQn.treeview_sort_column_by_no(acc_db, "#0", False))
    acc_db.heading('User ID', text='User ID', anchor=W,
                   command=lambda: pickQn.treeview_sort_column_by_db_col(acc_db, "User ID", 0, False))
    acc_db.heading('Name', text='Name', anchor=W,
                   command=lambda: pickQn.treeview_sort_column_by_db_col(acc_db, "Name", 1, False))
    acc_db.heading('Password', text='Password', anchor=W)
    acc_db.heading('Access Level', text='Access Level', anchor=W,
                   command=lambda: pickQn.treeview_sort_column_by_db_col(acc_db, "Access Level", 3, False))

    cnt = 0
    for rec in records:
        if cnt % 2 == 0:
            acc_db.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                          values=(rec[0], rec[1], rec[2], rec[3]), tags=('evenrow',))
        else:
            acc_db.insert(parent='', index='end', iid=cnt, text=str(cnt + 1),
                          values=(rec[0], rec[1], rec[2], rec[3]), tags=('oddrow',))
        cnt += 1

    btn_frame = Frame(all_user_set_page)
    delete_btn = Button(btn_frame, text='Delete', cursor='hand2',
                        command=lambda: delete_user(root, account, acc_db))
    select_btn = Button(btn_frame, text='Select', cursor='hand2',
                        command=lambda: user_setting(root, account=None, acc_db=acc_db))

    btn_frame.grid(row=1, column=0, sticky='ew')
    delete_btn.grid(row=0, column=0, sticky='e', padx=3, pady=3)
    select_btn.grid(row=0, column=1, sticky='e', padx=3, pady=3)

    btn_frame.grid_rowconfigure(0, weight=1)
    btn_frame.grid_columnconfigure(0, weight=1)
