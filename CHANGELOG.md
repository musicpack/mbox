# Changelog
All notable changes to this project will be documented in this file.
## [Unreleased]
- Discovery allows you to select popular playlists or even popular songs played on the server thorugh spotify or the bot itself!
- Autoplay related songs after the music has ended.
- Smarter search through Youtube Music, selecting songs instead of music videos.
- Display lyrics sourced through close captioning or Youtube Music API.
## [0.4] - 2021-04-09
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