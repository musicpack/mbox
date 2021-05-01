# Music Box
Music Box is a discord streaming bot designed to be easy to use.

Uses SponsorBlock data licensed used under CC BY-NC-SA 4.0. More details: https://sponsor.ajay.app/

**Features:**

- Play music from Youtube.
- Search Youtube & Youtube Music from the bot.
- Skip non-music sections of the bot based on [crowdsourced data](https://sponsor.ajay.app/).
- [Discord slash commands](https://blog.discord.com/slash-commands-are-here-8db0a385d9e6)  eg. /play, /pause

![image](images/example.png)

## Setup/Installation
1. Install Python 3.7 or greater from https://www.python.org/
    - Mac/Linux users, you might already have python 3 installed on your computer. Open your terminal and type `python`. If your command prompt says `Python 3.7` or higher you do not need to install from the website.
    - Mac/Linux users, your `python` command might use Python 2, which is not supported. If this is the case use the command `python3` instead of `python` for the rest of this setup. 
        

2. Clone this repository and navigate to project directory
    - Windows users, you might need to install git from [git-scm.com](https://git-scm.com/download/win)
    ```bash
    git clone https://github.com/borisliao/mbox.git
    cd mbox/
    ```

3. Install python project dependencies 
    - It is *recomended to create a virtual environment* instead of installing libraries globally to avoid conflicts with any other python projects. 
    - Virtual environments can usually live in the project root directory. If you like, you can start a new virtual environment by:
        ```bash
        cd <your project root directory>

        (On linux shell)
        python -m venv <venv name>/
        source <venv name>/bin/activate 
        
        (On cmd or powershell)
        python -m venv <venv name>
        <venv name>\Scripts\activate 
        ```
    - Install python project dependencies using pip
        ```bash
        pip install -r requirements.txt
        ```

4. Install FFmpeg on your computer [(wiki)](https://github.com/borisliao/mbox/wiki/FFmpeg-Installation)
    - Since this step is platform dependent, please view the tutorial on the [wiki](https://github.com/borisliao/mbox/wiki/FFmpeg-Installation)
    
5. **Mac/Linux Users only:** Install Opus
    - For MacOS users, the easiest way is to [install homebrew](https://brew.sh/) then type ``brew install opus``
    - For Linux/Unix users, type ``sudo apt-get install libopus``

6. Set up a Bot account on the Discord Developer Portal and copy the token to sample_config.ini [(wiki)](https://github.com/borisliao/mbox/wiki/Setting-up-a-Bot-Account-on-the-Discord-Developer-Portal)
    - Go to [Discord Developer Portal](https://discord.com/developers/applications) 
    - Add new application to Discord account. [(image)](https://raw.githubusercontent.com/borisliao/mbox/master/images/install1.png)

    - Enter Bot's name. *Recommended name: Music Box*
    - Click on Bot tab.

    - Scroll down to Privileged Gateway Intents and turn on both PRESENCE INTENT and SERVER MEMBERS INTENT. [(image)](https://raw.githubusercontent.com/borisliao/mbox/master/images/install4.png)
    
    - Scroll back up to Build-A-Bot and copy token. [(image)](https://raw.githubusercontent.com/borisliao/mbox/master/images/install2.png)

    - Navigate to sample_config.ini and change variable TOKEN to the copied value.
    - Rename sample_config.ini to config.ini

7. Invite the bot to a server [(wiki)](https://github.com/borisliao/mbox/wiki/Invite-the-Bot-to-a-Server)
    - Click on OAuth2 tab.
    - Under Scopes, check off ``bot`` checkbox.
    - Copy bot invitation link. [(image)](images/install3.png)

    - Paste URL into browser and invite bot to a server.

## Usage
*To run application*.
```bash
python main.py
```
### For Developers: 

If you are using VSCode, you can run the program in *[Run and Debug](https://code.visualstudio.com/docs/editor/debugging)*, with the included profiles: *Normal Mode*, *Debug Mode*

*To run application in debug mode*.
```bash
python main.py debug
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
