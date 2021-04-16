# Music Box
Music Box is a discord streaming bot designed to use no commands.

Uses SponsorBlock data licensed used under CC BY-NC-SA 4.0. More details: https://sponsor.ajay.app/

**Features:**

Playing back from Youtube links, livestreams
Searching Youtube from the bot

![image](images/example.png)
## Installation
1. Install Python 3.7 or greater from https://www.python.org/
2. Clone this repository
```bash
git clone https://github.com/borisliao/mbox.git
```
3. Navigate to the cloned directory and install depencencies
```bash
pip install -r requirements.txt
```
4. Download a build of FFMPEG for your operating system on https://ffmpeg.org/download.html
5. Extract the zip file (preferably to the mbox directory)
6. Navigate to src/constants.py and change variable FFMPEG_PATH to the executable of where you extracted the zip file.
7. Add a new application to your discord account on https://discord.com/developers/applications
![image](images/install1.png)
The name you choose will be the bot's name. (recommended to name 'Music Box')
![image](images/install2.png)
Click on your application and then (1.) click on Bot tab and (2.) click on copy button under token
8. Navigate to src/constants.py and change variable TOKEN to the copied value.

## Usage
Run main.py on the terminal with python
```bash
python main.py
```
*Optinally run main.py in debug mode*
```bash
python main.py debug
```
![image](images/install3.png)
After running successfully, get the url to add the bot to your server by (1.) clicking OAuth2 tab on your [discord developer](https://discord.com/developers/applications/) application page (2.) checking bot and (3.) copying the url and opening it!
## Issues

* youtube-dl should update automatically during the runtime of this program
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)