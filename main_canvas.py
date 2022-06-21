import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab
from mss import mss
import easyocr
import numpy as np

from select import SelectWindow

class Application(tk.Frame):

    # Default selection object options.
    SELECT_OPTS = dict(dash=(2, 2), stipple='gray25', fill='red',
                          outline='')

    def __init__(self, parent, mss, reader, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.image_canvas = None
        self.screenshot = None
        self.after_id = None
        self.sct = mss
        self.reader = reader
        btn = ttk.Button(self, text="Start", command=self.create_select)
        btn.pack()

    def create_select(self):
        root.attributes('-topmost', False)
        self.select = SelectWindow(root, self.save_bbox)
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def save_bbox(self, min_x, min_y, max_x, max_y):
        self.bbox = (min_x, min_y, max_x, max_y)
        print("selected: ", self.bbox)
        # root.geometry(f"{max_x-min_x}x{max_y-min_y}+{min_x}+{min_y}")
        root.geometry(f"{max_x-min_x}x{max_y-min_y}")
        root.attributes('-topmost', True)
        self.after_id = self.after(1, self.update_img)

    def update_img(self):
        print("update_img called")
        if self.image_canvas:
            self.image_canvas.destroy()
        sct_image = self.sct.grab(
            # self.bbox
            {"left": self.bbox[0], "top": self.bbox[1], "width": self.bbox[2], "height": self.bbox[3]}
            )
        self.screenshot = Image.frombytes('RGB', sct_image.size, sct_image.bgra, 'raw', 'BGRX')
        # self.screenshot = ImageGrab.grab(bbox=self.bbox)
        image = ImageTk.PhotoImage(self.screenshot)
        self.image_canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.image_canvas.create_image(0, 0, image=image, anchor=tk.NW)
        self.image_canvas.img = image
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        self.after_id = self.after(10, self.update_img)
        # for coords, text, confidence in reader.readtext(np.array(self.screenshot)):
        #     self.image_canvas.create_rectangle(coords[0][0], coords[0][1], coords[2][0], coords[2][1], outline='red')
        #     self.image_canvas.create_text(((coords[0][0]+coords[1][0])//2, (coords[1][1]+coords[2][1])//2), text=text,  fill="yellow")



if __name__ == '__main__':

    reader = None #easyocr.Reader(['ja','en'])

    WIDTH, HEIGHT = 400, 400
    BACKGROUND = 'grey'
    TITLE = 'tesselate'
    with mss() as sct:
        root = tk.Tk()
        root.title(TITLE)
        root.geometry('%sx%s' % (WIDTH, HEIGHT))
        root.configure(background=BACKGROUND)
        root.wm_attributes("-transparentcolor", 'yellow')
        root.attributes('-topmost', True)

        app = Application(root, sct, reader, background=BACKGROUND)
        app.pack()
        app.mainloop()