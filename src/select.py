import tkinter as tk

class MousePositionTracker(tk.Frame):
    """ Tkinter Canvas mouse position widget. """

    def __init__(self, canvas):
        self.canvas = canvas
        self.canv_width = self.canvas.winfo_screenwidth()
        self.canv_height = self.canvas.winfo_screenheight()
        self.reset()

        # Create canvas cross-hair lines.
        xhair_opts = dict(dash=(3, 2), fill='green', state=tk.HIDDEN)
        self.lines = (self.canvas.create_line(0, 0, 0, self.canv_height, **xhair_opts),
                      self.canvas.create_line(0, 0, self.canv_width,  0, **xhair_opts))

    def cur_selection(self):
        return (self.start, self.end)

    def begin(self, event):
        self.hide()
        self.start = (event.x, event.y)  # Remember position (no drawing).

    def update(self, event):
        self.end = (event.x, event.y)
        self._update(event)
        self._command(self.start, (event.x, event.y))  # User callback.

    def _update(self, event):
        # Update cross-hair lines.
        self.canvas.coords(self.lines[0], event.x, 0, event.x, self.canv_height)
        self.canvas.coords(self.lines[1], 0, event.y, self.canv_width, event.y)
        self.show()

    def reset(self):
        self.start = self.end = None

    def hide(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.HIDDEN)
        self.canvas.itemconfigure(self.lines[1], state=tk.HIDDEN)

    def show(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.NORMAL)
        self.canvas.itemconfigure(self.lines[1], state=tk.NORMAL)

    def autodraw(self, command=lambda *args: None):
        """Setup automatic drawing; supports command option"""
        self.reset()
        self._command = command
        self.canvas.bind("<Button-1>", self.begin)
        self.canvas.bind("<B1-Motion>", self.update)
        self.canvas.bind("<ButtonRelease-1>", self.quit)

    def quit(self, event):
        self.hide()  # Hide cross-hairs.
        self.reset()

class SelectionObject:
    """ Widget to display a rectangular area on given canvas defined by two points
        representing its diagonal.
    """
    def __init__(self, canvas, select_opts):
        # Create attributes needed to display selection.
        self.canvas = canvas
        self.select_opts1 = select_opts
        self.width = self.canvas.winfo_screenwidth()
        self.height = self.canvas.winfo_screenheight()

        # Options for rectanglar selection.
        select_opts1 = self.select_opts1.copy()  # Avoid modifying passed argument.
        select_opts1.update(state=tk.HIDDEN)  # Hide initially.

        # Initial extrema of rectangle.
        imin_x, imin_y,  imax_x, imax_y = 0, 0,  1, 1

        self.rect = self.canvas.create_rectangle(imin_x, imin_y,  imax_x, imax_y, **select_opts1)

    def update(self, start, end):
        # Current extrema of rectangle.
        imin_x, imin_y,  imax_x, imax_y = self._get_coords(start, end)

        # Update coords of rectangle based on these extrema.
        self.canvas.coords(self.rect, imin_x, imin_y,  imax_x, imax_y),

        # Make sure all are now visible.
        self.canvas.itemconfigure(self.rect, state=tk.NORMAL)

        return imin_x, imin_y, imax_x, imax_y

    def _get_coords(self, start, end):
        """ Determine coords of a polygon defined by the start and
            end points one of the diagonals of a rectangular area.
        """
        return (min((start[0], end[0])), min((start[1], end[1])),
                max((start[0], end[0])), max((start[1], end[1])))

    def hide(self):
        for rect in self.rects:
            self.canvas.itemconfigure(rect, state=tk.HIDDEN)

class SelectWindow(tk.Toplevel):

    # Default selection object options.
    SELECT_OPTS = dict(dash=(2, 2), stipple='gray25', fill='red',
                          outline='')

    def __init__(self, parent, callback, *args, **kwargs):
        super().__init__(parent, takefocus=True, *args, **kwargs)
        self.callback = callback

        self.grab_set()
        self.bind("<ButtonRelease-1>", self.on_destroy)
        self.attributes('-fullscreen', True)
        self.attributes('-alpha',0.5)
        self.attributes('-topmost', True)

        self.min_x = 0
        self.min_y = 0
        self.max_x = self.winfo_screenwidth()
        self.max_y = self.winfo_screenheight()

        self.text = tk.StringVar()
        self.text.set(f"({self.min_x}px,{self.min_y}px), ({self.max_x}px,{self.max_y}px)")
        label = tk.Label(self, textvariable=self.text, font= ('Helvetica 14 bold'), foreground= "black")
        label.pack(side=tk.BOTTOM)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, background="blue")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.selection_obj = SelectionObject(self.canvas, self.SELECT_OPTS)            

        self.posn_tracker = MousePositionTracker(self.canvas)
        self.posn_tracker.autodraw(command=self.on_drag)  # Enable callbacks.
    
    def on_drag(self, start, end, **kwarg):
        self.min_x, self.min_y, self.max_x, self.max_y = self.selection_obj.update(start, end)
        self.text.set(f"({self.min_x}px,{self.min_y}px), ({self.max_x}px,{self.max_y}px)")

    def on_destroy(self, _event):
        self.destroy()
        self.callback(self.min_x, self.min_y, self.max_x, self.max_y)