import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
# import subprocess
import threading
from delete_when_unzip import main_unzip as single_unzip
from delete_when_unzip_multi import main_unzip as multi_unzip
from delete_when_unzip_rar import main_unzip as single_unzip_rar
from delete_when_unzip_rar_multi import main_unzip as multi_unzip_zc
from delete_when_unzip_cli import main_unzip as multi_unzip_rar
from robust_split import robust_basename_split
import time
import os
import re

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
def thread_it(func, *args):
    '''Wrap a function to run in a thread'''
    # create
    t = threading.Thread(target=func, args=args) 
    t.setDaemon(True) 
    # start
    t.start()

class ProcessManager:
    '''
    Process control class: runs the main extraction process and the
    progress-bar process in the background. Pass the file name and
    other parameters to this object before extraction, then call
    run() to start.
    '''
    def __init__(self,mode:str,file_path:str,chunksize:int,password_str:str):
        self.modemap = {
            'Single file, zip/tar.gz':0, 
            'Single file, RAR':1, 
            'Multi-volume, zip':2,
            'Multi-volume, rar':3,
            'Single file, alternate':4,
            'Multi-volume, alternate':5
        }
        self.mode = self.modemap[mode]
        self.file_path = file_path
        self.chunksize = chunksize
        self.password_str = password_str
        self.fsize = 0

    def run(self):
        '''Start extraction: launch the process (non-blocking) and return'''
        self.progress_bar = ttk.Progressbar(window, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.pack(pady=10)
        thread_it(self.pack_process)
        thread_it(self.process_inquiry)

    def pack_process(self):
        '''
        Main extraction process
        '''
        try:
            # If self.mode is 0, 1, or 4 and file_path contains .part, .PART, .r01, .z01,
            # .R01, or .Z01, pop up a warning to confirm this is correct, since selecting
            # single-file mode on a segmented file otherwise causes an empty-result error.
            if self.mode in [0, 1, 4]:
                if re.search(r'\.(part\d{1,}|r\d{1,}|z\d{1,}|\d{3,})\.?(rar|zip)?$', self.file_path, re.I):
                    confirm = messagebox.askyesno(
                        "Filename Warning",
                        "Detected split file marker in filename, but single file mode is selected. Continue?"
                    )
                    if not confirm:
                        self.end_process()
                        return
            if self.mode == 0:
                unzip_func = single_unzip
                self.fsize = os.path.getsize(self.file_path)*1.0
            if self.mode == 1:
                unzip_func = single_unzip_rar
                self.fsize = os.path.getsize(self.file_path)*1.0

            if self.mode == 2:
                unzip_func = multi_unzip
                self.fsize = self.get_multi_filecounts()*1.0
            if self.mode == 3:
                unzip_func = multi_unzip_rar
                self.fsize = self.get_multi_filecounts()*1.0

            if self.mode == 4:
                unzip_func = single_unzip_rar
                self.fsize = os.path.getsize(self.file_path)*1.0
            if self.mode == 5:
                unzip_func = multi_unzip_zc
                self.fsize = self.get_multi_filecounts()*1.0
            # print(self.password_str)    # debug
            unzip_func(self.file_path,self.chunksize,self.password_str)
        except Exception as e:
            err_message = repr(e)
            print('Error:'+err_message)
            if '7z' in err_message or 'UnsupportedCompressionTypeError(14)' in err_message:
                err_message = 'Unsupported compression algorithm'
            if 'Rar!' in err_message:
                err_message = 'Please choose RAR mode'
            if 'Decryption is unsupported' in err_message or\
                'Unsupported block header size' in err_message:
                err_message = 'libarchive cannot decompress encrypted single RAR'
            if '\'str\' object cannot be interpreted as an integer' in err_message:
                err_message = 'Please use other mode for single or volumes'
            messagebox.showerror("Error", err_message)
            self.end_process()

    def process_inquiry(self):
        '''
        Manages the progress bar's value, updating it every 0.1s using
        a smoothed progress estimation method. Once progress reaches
        100, the interface is unlocked.
        '''
        if self.fsize == 0: # only runs once the file size has been retrieved
            return
        self.progress_bar['value'] = 1.0
        velocity_bar = 0.1 # 0.1% per step -> 1% per sec
        bar_top = 1.0
        last_val = 0.0
        new_val = 0.0
        delta_n = 1
        first_checkpoint_limit = 20
        # steadily advance the progress bar
        while True:
            if self.mode in (0,1,4):
                try:
                    new_val = 100.0 * (self.fsize-os.path.getsize(self.file_path))/self.fsize
                except:
                    new_val = 100.0 # the file no longer exists after the last chunk is processed, so jump straight to 100%
            else:
                new_val = 100.0 * (self.fsize-self.get_multi_filecounts()) / self.fsize
            if new_val==100:
                break
            # Before the first update we don't know the bar's real speed, so the initial
            # estimate of 0.1 may be too high. If the bar exceeds a threshold with no new
            # progress update received, stop advancing it further.
            if bar_top>=first_checkpoint_limit: 
                velocity_bar = 0.0
            bar_top = bar_top + velocity_bar
            if new_val != last_val: # got a new progress value: update speed/bar params, lift the cap
                velocity_bar = abs(new_val-last_val)/delta_n
                bar_top = new_val
                last_val = new_val
                first_checkpoint_limit = 100
                delta_n = 0
            # update the progress bar
            self.progress_bar['value'] = bar_top
            self.progress_bar.update()
            time.sleep(0.01)
            delta_n+=1
        messagebox.showinfo("Successfully Unzipped!","Successfully Unzipped!")
        self.end_process()

    def get_multi_filecounts(self):
        '''
        Query the number of remaining volume files
        '''
        file_list = []
        file_path,file_basename_zip = os.path.split(self.file_path)
        if file_path == '':
            file_path = './'

        file_basename = robust_basename_split(file_basename_zip)

        # old logic
        # file_basename,_ = os.path.splitext(file_basename_zip)   # only splits off the last suffix (xxx.part1 |.zip )
        # if file_basename.endswith('.zip') or file_basename.endswith('.ZIP'):    # for .zip.00x multi-segment files
        #     file_basename,_ = os.path.splitext(file_basename)
        # if file_basename.endswith('.part1'):    # for .part1.rar multi-segment files
        #     file_basename,_ = os.path.splitext(file_basename)
        files = os.listdir(file_path)
        # filter for file_basename.zip, file_basename.z01, file_basename.z02 ...
        pattern1 = re.compile(rf"{re.escape(file_basename)}\.z\d+",re.I)
        pattern2 = re.compile(rf"{re.escape(file_basename)}\.zip",re.I)
        pattern3 = re.compile(rf"{re.escape(file_basename)}\.zip\.\d+",re.I)
        pattern4 = re.compile(rf"{re.escape(file_basename)}\.r\d+",re.I)
        pattern5 = re.compile(rf"{re.escape(file_basename)}\.rar",re.I)
        pattern6 = re.compile(rf"{re.escape(file_basename)}\.rar\.\d+",re.I)
        pattern7 = re.compile(rf"{re.escape(file_basename)}\.part\d+\.rar",re.I)

        for file in files:
            if pattern1.match(file) or pattern2.match(file) or pattern3.match(file) or\
                pattern4.match(file) or pattern5.match(file) or pattern6.match(file) or pattern7.match(file):
            # if file.startswith(file_basename) and os.path.isfile(os.path.join(file_path, file)):
                file_list.append(os.path.join(file_path, file)) # sorted in z01,z02,...zip order
        return len(file_list)

    def end_process(self):
        self.progress_bar['value'] = 100.0
        run_state.set(" Run")      # global var
        run_button['state'] = 'normal'
        self.progress_bar.pack_forget()

def run_program():

    file_path = file_entry.get()
    number = number_entry.get()
    number = eval(number)*1024*1024
    # number = str(number)
    mode = var_mode.get()

    if checkbox_var.get() == 1:
        password_str = password_entry.get()
    else:
        password_str = None
    if mode=='' or file_path=='':
        messagebox.showerror('Empty file path or mode!','Empty file path or mode!') 
        return
    
    # prep before running
    run_button['state'] = 'disable' # global var
    run_state.set("Running...")      # global var
    process_unzip = ProcessManager(mode,file_path,number,password_str) # runs the task and progress bar on separate threads, non-blocking
    process_unzip.run() 
    # try:
    #     # run the command-line program
    #     if mode == 'mode1':
    #         single_unzip(file_path,number,password_str)

    #     elif mode == 'mode2':
    #         multi_unzip(file_path,number,password_str)

    #     messagebox.showinfo("Successfully Unzipped!","Successfully Unzipped!")
    # except Exception as e:
    #     messagebox.showerror("Error", str(e))
    # run_state.set(" Run ")      # global var
    # run_button['state'] = 'normal'

def browse_file():
    # file_path = filedialog.askopenfilename(filetypes=[('ZIP Files','.zip'),
    #                                                   ('ZIP Seg Files','.zip.001'),
    #                                                   ('RAR Files','.rar .part1.rar .part01.rar'),
    #                                                   ('All Files','*')])
    file_path = filedialog.askopenfilename(filetypes=[('ZIP/RAR Files','.zip .zip.001 .rar .part1.rar .part01.rar .part001.rar'),
                                                      ('All Files','*')])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

# create the main window
window = tk.Tk()
window.title("Delete when unzip(For BIIIIG zip/rar file)")
try:
    _icon_img = tk.PhotoImage(file=os.path.join(_SCRIPT_DIR, 'app_icon.png'))
    window.iconphoto(True, _icon_img)
except Exception:
    try:
        window.iconbitmap(os.path.join(_SCRIPT_DIR, 'app_icon.ico'))  # fallback for Windows
    except Exception:
        pass 
# create the file path input box and browse button
file_label = tk.Label(window, text="File Path:")
file_label.pack()
file_entry = tk.Entry(window, width=50)
file_entry.pack()
browse_button = tk.Button(window, text="Choose File", command=browse_file)
browse_button.pack()

# create the chunk size spinbox
number_label = tk.Label(window, text="Chunk Size (MB):")
number_label.pack()
# number_entry = tk.Entry(window)
# number_entry.insert(0, "512")
default_chunksize = tk.StringVar()
default_chunksize.set(512)
number_entry = tk.Spinbox(window,from_=0,to=1e12,textvariable=default_chunksize)
number_entry.pack()

# create the password input box
def toggle_entry_state():
    if checkbox_var.get() == 1:
        password_entry.config(state=tk.NORMAL)
    else:
        password_entry.config(state=tk.DISABLED)
checkbox_var = tk.IntVar()
checkbox = tk.Checkbutton(window, text="Use Password:", variable=checkbox_var, command=toggle_entry_state)
checkbox.pack()

password_entry = tk.Entry(window, state=tk.DISABLED)
password_entry.pack()

# create the mode selection area
label_mode = tk.Label(window, text="Select Mode:")
label_mode.pack()
var_mode = tk.StringVar()
cbox = ttk.Combobox(window,textvariable=var_mode)
cbox['value'] = ('Single file, zip/tar.gz', 'Single file, RAR', 
                 'Multi-volume, zip', 'Multi-volume, rar',
                 'Single file, alternate','Multi-volume, alternate')
cbox.pack()

notice = tk.Label(window, text="(Note: files are permanently deleted after extraction, use with care.\nIn multi-volume mode, only select the first volume: .zip, .zip.001, or part1\nBefore extracting volumes, make sure all volumes are present)")
notice.pack()

# create the run button
run_state = tk.StringVar()
run_state.set(" Run")
run_button = tk.Button(window, textvariable=run_state, command=run_program)
run_button.pack()

# run the main loop
window.mainloop()