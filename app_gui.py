# Structure
# Grid, main frame, lower frame (fixed height)
#    Main frame, grid of frames, containing packed labels (like gridTest) *
#    Lower frame, Grid of Labels
#
# * Each grid box associated to a "datagrid" object, List-ed in app_gui, 
#   and by anything that wants easy access, eg voter dict.
#       lbl_name, lbl_votes, frame. + Methods

import tkinter as tk

class app_gui:
    onGrid=[] # somewhere to note which datagrids have been grid-ed
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
    def hideLwr(self):
        self.frm_lower.grid_remove()
    def Show(self):
        self.window.mainloop()
        
class datagrid:
    def __init__(self,parent,**kwargs):
        name=kwargs.get('name',"")
        status=kwargs.get('status',"")
        self.frame = tk.Frame(
            master=parent,
            borderwidth=1
        )

        self.lbl_status = tk.Label(master=self.frame, text=status, anchor="e", font=("Sans Serif",25))
        self.lbl_status.pack(side=tk.RIGHT, padx=(0,5))
        self.status=status

        self.lbl_name = tk.Label(master=self.frame, text=name, anchor="w")
        self.lbl_name.pack(side=tk.LEFT, padx=(5,0))
        self.name=name
    def grid(self,i,j):
        bg="#eee" if  ((i % 2) == 1) else "#ccc"
        self.frame["background"]=bg
        self.lbl_name["background"]=bg
        self.lbl_status["background"]=bg
        self.frame.grid(row=i, column=j, padx=1, sticky="nsew")
        # remember to configure rows/columns elsewhere
    def let(self,**kwargs):  #since "set" is reserved in python
        # only modify if changed
        if ("status" in kwargs) and kwargs["status"]!=self.status:
            self.name=kwargs["status"]
            self.lbl_status["text"]=kwargs["status"]
        if ("name" in kwargs) and kwargs["name"]!=self.name:
            self.name=kwargs["name"]
            self.lbl_name["text"]=kwargs["name"]
            return True # Useful to propagate name change- could affect layout
        return False
    def remove(self):
        self.frame.grid_remove()

if __name__ == '__main__':
    test=app_gui()
    for i in range(3):
        test.frm_main.columnconfigure(i, weight=1, minsize=75)
        test.frm_main.rowconfigure(i, weight=1, minsize=30)
        for j in range(0, 3):
            datagrid(test.frm_main, name=f"Cell {i}, {j}", status="\N{BULLET}\N{WHITE BULLET}").grid(i,j)
    test.Show()