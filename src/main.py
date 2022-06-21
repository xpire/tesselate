import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab
from mss import mss
import easyocr
import translators as ts

from select import SelectWindow
from ocr_reader import AsyncOCR

IMAGE_DELAY = 200
OCR_DELAY = 1000
TRANSLATE_DELAY = 1000

class Application(tk.Frame):

    # Default selection object options.
    SELECT_OPTS = dict(dash=(2, 2), stipple='gray25', fill='red',
                          outline='')

    def __init__(self, parent, mss, reader, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.screenshot = None
        self.update_id = None
        self.ocr_id = None
        self.ocr_paused = tk.BooleanVar()
        self.ocr_results = []
        self.sct = mss
        self.reader = reader
        self.translate_stack = []
        self.translate_cache = {}
        
        start_btn = ttk.Button(self, text="Start", command=self.create_select)
        start_btn.pack()

        # pause_btn = ttk.Checkbutton(self, text="Processing", variable=self.ocr_pause, 
        #                             onvalue = True, offvalue = False, command=lambda: self.ocr_pause.set(True))
        # pause_btn.pack()

        # label to display image
        self.image_canvas = tk.Canvas(self, borderwidth=0, highlightthickness=1, highlightbackground="red")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)


    def create_select(self):
        root.attributes('-topmost', False)
        self.select = SelectWindow(root, self.save_bbox)
        if self.update_id:
            self.after_cancel(self.update_id)
            self.update_id = None
        if self.ocr_id:
            self.after_cancel(self.ocr_id)
            self.ocr_id = None

    def save_bbox(self, min_x, min_y, max_x, max_y):
        self.bbox = (min_x, min_y, max_x, max_y)
        print("selected: ", self.bbox)
        root.geometry(f"{max_x-min_x}x{max_y-min_y+10}")
        root.attributes('-topmost', True)

        self.image_canvas.config(width=max_x-min_x+100, height=max_y-min_y+100)

        self.update_id = self.after(IMAGE_DELAY, self.update_img)
        self.ocr_id = self.after(OCR_DELAY, self.start_ocr)
        self.translate_id = self.after(TRANSLATE_DELAY, self.process_translate)

    def translate(self, str):
        if str not in self.translate_cache:
            result = ts.google(str)
            self.translate_cache[str] = result
            return result
        else:
            return self.translate_cache[str]

    def process_translate(self):
        if self.translate_stack:
            raw_text, text_tk = self.translate_stack.pop()
            translated = self.translate(raw_text)
            self.image_canvas.itemconfigure(text_tk, text=translated, fill="green")
        self.translate_id = self.after(TRANSLATE_DELAY, self.process_translate)

    def update_img(self):
        print("update_img called")
        # screenshot selected region
        sct_image = self.sct.grab(self.bbox)
        self.screenshot = Image.frombytes('RGB', sct_image.size, sct_image.bgra, 'raw', 'BGRX')

        # Update screenshot thumbnail
        image = ImageTk.PhotoImage(self.screenshot)   
        self.image_canvas.create_image(0, 0, image=image, anchor=tk.NW)
        self.image_canvas.img = image

        # show OCR results if ready
        for coords, raw_text in self.ocr_results:
            rect_tk = self.image_canvas.create_rectangle(coords[0][0], coords[0][1], 
                coords[2][0], coords[2][1], outline='red', fill="white")
            cur_text = raw_text
            fill = "black"
            if raw_text in self.translate_cache:
                cur_text = self.translate_cache[raw_text]
                fill = "green"
            text_tk = self.image_canvas.create_text(((coords[0][0]+coords[1][0])//2, 
                (coords[1][1]+coords[2][1])//2), text=cur_text,  fill=fill)
            self.image_canvas.tag_lower(rect_tk,text_tk)
            self.translate_stack.append((raw_text, text_tk))

        # schedule next call
        self.update_id = self.after(IMAGE_DELAY, self.update_img)

    def start_ocr(self):
        self.ocr_thread = AsyncOCR(self.reader, self.screenshot, self.ocr_callback).start()

    def ocr_callback(self, results):
        self.ocr_results = results
        if not self.ocr_paused.get():
            self.after(OCR_DELAY, self.start_ocr)

if __name__ == '__main__':

    reader = easyocr.Reader(['ja','en'])

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