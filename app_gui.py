# Structure
# Grid, main frame, lower frame (fixed height)
#    Main frame, grid of frames, containing packed labels (like gridTest) *
#    Lower frame, Grid of Labels
#
# * Each grid box associated to an object in a List
#       lbl_name, lbl_votes, refcode, frm_self

import tkinter as tk

class app_gui:
    cols=2             # default columns
    maingridframes=[]  # List for storage of datagrid objects
    def __init__(self):
        window=tk.Tk()
        window.rowconfigure(0, weight=1, minsize=50)
        window.columnconfigure(0, weight=1, minsize=75)
        self.frm_main = tk.Frame(master=window, background="#aaa")
        self.frm_main.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        #tk.Label(master=self.frm_main, text="main frame").pack() # dummy content
        window.rowconfigure(1, weight=0, minsize=30)
        self.frm_lower = tk.Frame(master=window, relief=tk.SUNKEN, borderwidth=1)
        #tk.Label(master=self.frm_lower, text="lower frame").pack() # dummy content
        self.showLwr()
        self.window=window
    def showLwr(self):
        self.frm_lower.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
    def Show(self):
        self.window.mainloop()
        
class datagrid:
    source=""       #Key of dictionary from which the data is obtained
    def __init__(self,parent,name="Cell {i}, {j}",status="\N{BULLET}\N{WHITE BULLET}"):
        self.frame = tk.Frame(
            master=parent,
            borderwidth=1
        )

        self.lbl_status = tk.Label(master=self.frame, text=status, anchor="e", font=("Sans Serif",25))
        self.lbl_status.pack(side=tk.RIGHT, padx=(0,5))

        self.lbl_name = tk.Label(master=self.frame, text=name, anchor="w")
        self.lbl_name.pack(side=tk.LEFT, padx=(5,0))
    def grid(self,i,j):
        if ((i % 2) == 1):
            bg="#eee"
        else:
            bg="#ccc"
        self.frame["background"]=bg
        self.lbl_name["background"]=bg
        self.lbl_status["background"]=bg
        self.frame.grid(row=i, column=j, padx=1, sticky="nsew")
        # remember to configure rows/columns elsewhere


if __name__ == '__main__':
    test=app_gui()
    for i in range(3):
        test.frm_main.columnconfigure(i, weight=1, minsize=75)
        test.frm_main.rowconfigure(i, weight=1, minsize=30)
        for j in range(0, 3):
            datagrid(test.frm_main, f"Cell {i}, {j}").grid(i,j)
    test.Show()