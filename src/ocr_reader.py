from threading import Thread
import io

class AsyncOCR(Thread):
    def __init__(self, reader, screenshot, callback):
        super().__init__()
        self.reader = reader
        self.screenshot = screenshot
        self.callback = callback
        self.result = None

    def run(self):
        img_byte_arr = io.BytesIO()
        self.screenshot.save(img_byte_arr, format="PNG")
        self.result = self.reader.readtext(img_byte_arr.getvalue(), paragraph=True)
        print(f"async ocr finished with {self.result}")
        self.callback(self.result)