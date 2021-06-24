from tkinter import *
from tkinter.ttk import *
from ttkthemes import themed_tk as tk
from tkinter import messagebox
import sqlite3
import qns
import styles

conn = sqlite3.connect('accounts.db')
c = conn.cursor()

new_acc_al = 'Admin'

# Functions
def on_login():
    with conn:
        c.execute('SELECT * FROM accounts WHERE user_id=:userid AND password=:pw',
                  {
                      'userid': id_ent.get(),
                      'pw': pw_ent.get()
                  })
    account = c.fetchone()
    if not account:
        messagebox.showerror('Invalid Input', 'You have entered an incorrect username/password')
        return
    login_page.destroy()
    qns.main(account)
    return 'break'


def register():
    global reg_page
    global reg_id_ent
    global reg_name_ent
    global reg_pw_ent
    global reg_cfm_pw_ent

    reg_page = tk.ThemedTk()
    reg_page.get_themes()
    reg_page.set_theme(styles.MAIN_THEME)

    reg_page.title('Register')
    reg_page.iconbitmap('main_qn.ico')

    # Widget Styles
    styles.style_widget(reg_page)
    reg_padding_y = 3
    reg_padding_x = 6
    reg_df_row = 0
    ent_box_width = 30

    reg_page.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")
    reg_page.rowconfigure(0, weight=1)
    reg_page.columnconfigure(0, weight=1)

    reg_details_frame = Frame(reg_page)

    reg_id_lbl = Label(reg_details_frame, text='Enter your Login ID')
    reg_id_ent = Entry(reg_details_frame, font=styles.t_ent_font, width=ent_box_width)
    reg_id_ent.bind('<Return>', lambda e: on_register())

    reg_name_lbl = Label(reg_details_frame, text='Enter your Name')
    reg_name_ent = Entry(reg_details_frame, font=styles.t_ent_font, width=ent_box_width)
    reg_name_ent.bind('<Return>', lambda e: on_register())
    
    reg_pw_lbl = Label(reg_details_frame, text='Enter your new Password')
    reg_pw_ent = Entry(reg_details_frame, font=styles.t_ent_font, width=ent_box_width)
    reg_pw_ent.bind('<Return>', lambda e: on_register())

    reg_cfm_pw_lbl = Label(reg_details_frame, text='Enter your Password again')
    reg_cfm_pw_ent = Entry(reg_details_frame, font=styles.t_ent_font, width=ent_box_width)
    reg_cfm_pw_ent.bind('<Return>', lambda e: on_register())

    reg_btn = Button(reg_details_frame, text='Register', cursor='hand2', command=on_register)

    cancel_btn = Button(reg_details_frame, text='Cancel', cursor='hand2')
    cancel_btn.bind('<1>', lambda e: on_quit(reg_page))

    reg_id_ent.focus_set()

    reg_details_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')

    reg_id_lbl.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1
    reg_id_ent.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1

    reg_name_lbl.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1
    reg_name_ent.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1

    reg_pw_lbl.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1
    reg_pw_ent.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1

    reg_cfm_pw_lbl.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1
    reg_cfm_pw_ent.grid(row=reg_df_row, column=0, columnspan=2, sticky='nw', padx=reg_padding_x, pady=reg_padding_y)
    reg_df_row += 1

    reg_btn.grid(row=reg_df_row, column=0, sticky='n', pady=reg_padding_y)
    cancel_btn.grid(row=reg_df_row, column=1, sticky='n', pady=reg_padding_y)

    reg_details_frame.grid_rowconfigure([i for i in range(reg_df_row + 1)], weight=1)
    reg_details_frame.grid_columnconfigure([i for i in range(2)], weight=1)


def on_register():
    global reg_page

    # Check database for user id conflict
    with conn:
        c.execute("SELECT user_id FROM accounts")
    db_user_ids = c.fetchall()
    db_user_ids = [list(i)[0] for i in db_user_ids]
    if reg_id_ent.get() in db_user_ids:
        messagebox.showwarning('ID in use', 'User ID taken. Please use another User ID.')
        reg_page.after(1, lambda: reg_page.focus_force())
        return
    if not reg_id_ent.get() or not reg_name_ent.get() or not reg_pw_ent.get() or not reg_cfm_pw_ent.get():
        messagebox.showwarning('Incomplete', 'Please complete fill in all the blank cells.')
        reg_page.after(1, lambda: reg_page.focus_force())
        return
    if reg_pw_ent.get() != reg_cfm_pw_ent.get():
        messagebox.showwarning('Password', 'Password Mismatch. Please confirm again.')
        reg_page.after(1, lambda: reg_page.focus_force())
        return

    with conn:
        c.execute("INSERT INTO accounts VALUES(:userid, :name, :pw, :al)",
                  {
                      'userid': reg_id_ent.get(),
                      'name': reg_name_ent.get(),
                      'pw': reg_pw_ent.get(),
                      'al': new_acc_al
                  })
    reg_page.destroy()
    messagebox.showinfo('Success', 'You have successfully registered.')
    return 'break'


def on_quit(page):
    page.destroy()
    return 'break'


def main():
    global login_page
    global id_ent
    global pw_ent
    global app_width
    global app_height
    global t_ent_font
    global x
    global y

    login_page = tk.ThemedTk()
    login_page.get_themes()
    login_page.set_theme(styles.MAIN_THEME)
    login_page.title('Login')
    login_page.iconbitmap('main_qn.ico')
    login_page.after(1, login_page.focus_force())

    # Widget Styles
    styles.style_widget(login_page)

    # Windows size configuration
    app_width = 350
    app_height = 400

    screen_width = login_page.winfo_screenwidth()
    screen_height = login_page.winfo_screenheight()

    x = (screen_width / 2) - (app_width / 2)
    y = (screen_height / 2) - (app_height / 2)
    login_page.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

    login_page.rowconfigure(0, weight=1)
    login_page.columnconfigure(0, weight=1)
    login_page.resizable(False, False)

    details_frame = Frame(login_page)
    id_lbl = Label(details_frame, text='Login ID')
    id_ent = Entry(details_frame, font=styles.t_ent_font)
    id_ent.focus_set()

    pw_lbl = Label(details_frame, text='Password')
    pw_ent = Entry(details_frame, font=styles.t_ent_font, show='*')

    login_btn = Button(details_frame, text='Login', cursor='hand2')
    quit_btn = Button(details_frame, text='Quit', cursor='hand2')
    register_btn = Button(details_frame, text='Register', command=register, cursor='hand2')

    # Key Bindings
    login_btn.bind('<1>', lambda e: on_login())
    quit_btn.bind('<1>', lambda e: on_quit(login_page))
    id_ent.bind('<Return>', lambda e: on_login())
    id_ent.bind('<Escape>', lambda e: on_quit(login_page))
    pw_ent.bind('<Return>', lambda e: on_login())
    pw_ent.bind('<Escape>', lambda e: on_quit(login_page))

    padding_y = 3
    df_row = 0
    details_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')

    id_lbl.grid(row=df_row, column=0, columnspan=2, sticky='n', pady=padding_y)
    df_row += 1

    id_ent.grid(row=df_row, column=0, columnspan=2, sticky='n', pady=padding_y)
    df_row += 1

    pw_lbl.grid(row=df_row, column=0, columnspan=2, sticky='n', pady=padding_y)
    df_row += 1

    pw_ent.grid(row=df_row, column=0, columnspan=2, sticky='n', pady=padding_y)
    df_row += 1

    login_btn.grid(row=df_row, column=0, sticky='n', pady=padding_y)
    quit_btn.grid(row=df_row, column=1, sticky='n', pady=padding_y)
    df_row += 1
    register_btn.grid(row=df_row, column=0, columnspan=2, sticky='n', pady=padding_y)

    details_frame.grid_rowconfigure([i for i in range(df_row + 1)], weight=1)
    details_frame.grid_columnconfigure([i for i in range(2)], weight=1)

    login_page.mainloop()


if __name__ == "__main__":
    main()
