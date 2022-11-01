from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox
from secret_messages import secretMsgCore

MY_FONT = 'Times New Roman'
MY_BACKGROUND = '#505050'

root = Tk()
root.title('Secret Image Communication')
root.resizable(False, False)
root.config(background=MY_BACKGROUND)

#  Global vars
mode = StringVar()
password = StringVar()
img_path = StringVar()


def change_mode(event):
    ''' Toggle between Encode and Decode '''
    current = mode.get()
    if current == 'Encode':
        message_box.config(background='white', state='normal')
    elif current == 'Decode':
        message_box.config(background='#999999', state='normal')

def search_image():
    ''' The users navigate between their files to find the image '''
    img_path.set(filedialog.askopenfilename(
        initialdir='.',
        title='Select a image',
        filetypes=(
            ('Image', ('*.jpg', '*.png')),
        )
    ))

    image_name.config(text=img_path.get())

def do_action():
    ''' Execute the encode or decode function '''
    if mode.get() == 'Encode':
        message = message_box.get('1.0', END).strip()
        if len(message) == 0:
            showMessage(False, '', 'Message empty')
        else:
            encode(img_path.get(), message_box.get('1.0', END), password.get())
    elif mode.get() == 'Decode':
        decode(img_path.get(), password.get())

def showMessage(success, title, message):
    '''' Shows a message to the user '''
    message = f'Message: {message}'
    if success:
        messagebox.showinfo(title=title, message=message)
    else:
        messagebox.showerror(title='An error has ocurred', message=message)

def encode(path, message, password):
    ''' Encode the image '''
    result = secretMsgCore.encode_image(path, message, password)
    showMessage(result['ok'], 'Image encoded', result['message'])

def decode(path, password):
    ''' Decode the image '''
    result = secretMsgCore.decode_image(path, password)
    showMessage(result['ok'], 'Message decoded', result['message'])

# Defining the widgets
title = Label(root, text='Secret Image Communication', font=(MY_FONT,20), bg=MY_BACKGROUND, fg='white')
browse_button = Button(root, text='Search image', font=(MY_FONT, 10), bg='#404040', fg='white', command=search_image)
image_name = Label(root, font=(MY_FONT,10), bg=MY_BACKGROUND, fg='white')
mode_label = Label(root, text='Select mode', font=(MY_FONT,14), bg=MY_BACKGROUND, fg='white')

mode_selector = Combobox(
    root,
    values=['Encode', 'Decode'],
    textvariable=mode,
    state='readonly',
    background=MY_BACKGROUND
)
mode_selector.current(0)

mode_selector.bind('<<ComboboxSelected>>', change_mode)

message_label = LabelFrame(root, text='Message', bg=MY_BACKGROUND, font=(MY_FONT,14), fg='white', padx=5, pady=5)
message_box = Text(message_label, font=(MY_FONT,12), height=5, width=45, padx=1)

password_label = Label(root, text='Password', bg=MY_BACKGROUND, font=(MY_FONT,14), fg='white')
password_entry = Entry(root, textvariable=password, show='*', font=(MY_FONT,14))

submit = Button(root, text='Go!', font=(MY_FONT, 10), bg='#404040', fg='white', command=do_action)


# Locating widgets
title.grid(column=0, row=0, columnspan=4, sticky='ew', padx=20, pady=(5, 35))
browse_button.grid(column=1, row=1, columnspan=2, sticky='ew', pady=(10,3), padx=25)
image_name.grid(column=0, row=2, columnspan=4, sticky='ew', pady=(0, 10), padx=25)
mode_label.grid(column=1, row=3, columnspan=2, sticky='ew', pady=(15,0))
mode_selector.grid(column=1, row=4, columnspan=2, sticky='ew', pady=(0,10))
message_label.grid(column=0, row=5, columnspan=4, sticky='ew', pady=(10,0), padx=15)
message_box.grid(column=0, row=6, columnspan=4, sticky='ew', padx=15, pady=(0,15))
password_label.grid(column=0, row=7, columnspan=4, sticky='ew', pady=(15,0))
password_entry.grid(column=0, row=8, columnspan=4, sticky='ew', padx=100)
submit.grid(column=1, row=9, columnspan=2, sticky='ew', pady=20, padx=35)


root.mainloop()