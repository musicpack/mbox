# Music Box
Music Box is a discord streaming bot designed to be easy to use.

Uses SponsorBlock data licensed used under CC BY-NC-SA 4.0. More details: https://sponsor.ajay.app/

**Features:**

- Playing music from Youtube.
- Search Youtube & Youtube Music from the bot.
- Skipping non-music sections of the bot based on [crowdsourced data](https://sponsor.ajay.app/).
- [Discord slash commands](https://blog.discord.com/slash-commands-are-here-8db0a385d9e6)  eg. /play, /pause

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
4. Install FFMPEG [(instructions)](https://github.com/borisliao/mbox/wiki/Installing-FFMPEG-for-mbox)
5. Make a discord application and copy the token [(instructions)](https://github.com/borisliao/mbox/wiki/Creating-a-new-Discord-Application-for-mbox)
6. Navigate to sample_config.ini and change variable TOKEN to the copied value.
7. Rename sample_config.ini to config.ini

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