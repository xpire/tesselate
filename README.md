# tesselate
OCR + Translation application which emulates google instant translate for your desktop

## Features
- GUI for ease of use (drag on the screen to select area)
- GPU accerated (requires cuda installation)

## How it works
- drag to select an area on your screen to watch
- OCR is run continuously on the screenshots to identify characters, locally with [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- Characters are translated and shown, through API with [translators](https://github.com/UlionTse/translators)
