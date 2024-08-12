Alpha Remover for PNG images. If called without arguments, opens GUI dialogs for selecting a folder and a colour, images are saved to a subfolder. 

If called with -i, the path to an image is required. 
If called with -f, the path to a folder is required.

Tested on python 3.11, likely to work on later versions.

```
usage: stripalpha.py [-h] [-f FOLDER | -i IMAGE] [-c COLOR] [-ns]


options:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        Path to folder containing images, exlusive to -i
  -i IMAGE, --image IMAGE
                        Path to single image, exclusive to -f
  -c COLOR, --color COLOR
                        Hex string (eg. "#FFFFFF") or string of numbers (eg. "0, 0, 0") of replacement color, numbers
                        outside of range 0-255 are wrapped, have fun. Default ("0, 0, 0")
  -ns, --no-subfolder   Skip creating subfolder for processed images, defaults to creating a new folder
  ```

  Setup:
 
 Clone directory
  ```
  git clone https://github.com/natsukashiixo/alpha-remover-pil.git
  ```
 Change into cloned directory
  ```
  cd alpha-remover-pil
  ```
 Create Virtual environment
  ```
  python -m venv venv
  ```
 Activate venv (Windows)
  ```
  ./venv/scripts/activate.ps1
  ```

  or: Activate venv (Linux)
  ```
  source ./venv/bin/activate
  ``` 

 Install required packages
  ```
  pip install -r requirements.txt
  ```

  Usage:

  No args, opens file/colour dialogs
  ```
  python stripalpha.py
  ```

  With args, opens no dialogs
  ```
  python stripalpha.py --options --go --here
  ```