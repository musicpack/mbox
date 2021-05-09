# Changelog
All notable changes to this project will be documented in this file.
## [Unreleased]
- Discovery allows you to select popular playlists or even popular songs played on the server thorugh spotify or the bot itself!
- Autoplay related songs after the music has ended.
- Display lyrics sourced through close captioning
- Have a toggle to repeat a song
- Have a command for a song timer length

## [0.5] - 2021-05-07
### Added
- Added slash commands /play, /pause, /c, /youtube, /next, /prev 
- Display lyrics sourced through close captioning or Youtube Music API.
- Smarter search through Youtube Music, selecting songs instead of music videos. Old search can be accessed through /youtube

### Changed
- Bot keeps server queue's seperate
- "PAUSED" will not remain on the footer after skipping while paused.
- Adding a song while paused will not advance to the next song.
- The bot will ignore other bot messaging in the command channel.
- The bot will leave and message the owner if it was added without the appropriate premissions.

## [0.5] - 2021-04-24
### Added
- Added slash commands /play, /pause, /c, /youtube, /next, /prev 
- Display lyrics sourced through close captioning or Youtube Music API.
- Smarter search through Youtube Music, selecting songs instead of music videos. Old search can be accessed through /youtube

### Changed
- Bot will now remove all the buttons in a message at the same time.
- Skipping non-music sections starting from the begining of the song (0:00) is faster

## [0.4] - 2021-04-16
### Added
- Non music sections will be skipped. Data sourced through the SponsorBlock API.
- Added config.ini file

### Changed
- Bot volume is now defaulted to 0.5.
- Bot volume is limited to 0 to 2.
- Footer text is not as long, due to making use of emojis.

## [0.3] - 2021-04-09
### Added
- Added a adaptive footer that displays duration, paused state, volume of the video.

### Changed
- Removing and adding buttons are now are done asynchronously. Songs will be downloaded first before buttons are added to the player.
- Added information and links about the bot in the bot channel. 