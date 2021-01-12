# Twitch Plays Nintendo Switch

Implementation by [@it_door](https://twitch.tv/it_door)

## Prerequisites

- Arduino (I used an Uno)
- Serial TTL adapter
- Some machine that runs Python 3
- A Nintendo Switch

## Setup

Client and server can live on separate machines. Make sure to set up your Twitch OAuth token in `auth.py`. All of the firmware was taken care of for me thanks to [javmarina](https://github.com/javmarina/Nintendo-Switch-Remote-Control/tree/master/firmware).

## TODO

- Clean up unused server code
- Make GUI (maybe use [Eel](https://github.com/ChrisKnott/Eel)?)
- change delay based on _type_ of input (press versus joystick)
  - joystick held for longer
- numbered/multiple inputs (split inputs by spaces to avoid spam filter?)

## Acknowledgements

- [wchill](https://github.com/wchill)
- [ItsDeidara](https://github.com/ItsDeidara)
- [javmarina](https://github.com/javmarina)
- Mecke_Dev on Twitch
- highimspectra on Twitch
