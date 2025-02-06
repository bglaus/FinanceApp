
# Streamlit Desktop App using Electron

This is an experiment to create a desktop app using [Streamlit](https://streamlit.io/) and [Electron](https://www.electronjs.org/) using [stlite](https://github.com/whitphx/stlite).

![](https://github.com/bglaus/FinanceApp/blob/main/demo.gif)

Users can add bank statements as csv-files and configure rules on how to categorize them. 

## Commands
- `npm install` to install dependencies
- `npm run dump` creates ./build directory
- `npm run serve` to run a preview
- `npm run app:dist` for packaging

## Limitations
- it's only possible to install pure python packages, no C-extensions are supported. This means that some packages like `transformers` or `pickle` are not supported.
When running `npm run dump` you'll get an error like `ValueError: Can't find a pure Python 3 wheel for: 'safetensors>=0.4.1', 'tokenizers<0.22,>=0.21'`.
- currently it only supports german ui language.
