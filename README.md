Requisitos
Apple Music (versión Windows/Microsoft Store).
SteelSeries GG y GameSense activado. (crear un evento para el dac viene en la documentación de la página de steelseries) https://github.com/SteelSeries/gamesense-sdk/blob/master/doc/api/sending-game-events.md
Arctis Nova Pro Wireless DAC u otro SteelSeries con pantalla compatible.
Python 3.12 o superior (solo si quieres correrlo como script, el .exe ya está empaquetado).
PyInstaller (para crear tu propio .exe, opcional).


Requirements
Apple Music (Windows/Microsoft Store version).
SteelSeries GG with GameSense enabled (you need to create an event for the DAC — instructions available in the official SteelSeries documentation) https://github.com/SteelSeries/gamesense-sdk/blob/master/doc/api/sending-game-events.md
Arctis Nova Pro Wireless DAC or any other SteelSeries device with a compatible screen.
Python 3.12 or higher (only required if you want to run it as a script; the .exe is already packaged).
PyInstaller (optional, only if you want to create your own .exe).


I realized that SteelSeries only supports Tidal to display what you’re listening to on the DAC of the Arctis Nova Pro.
Since I use Apple Music, figuring out how to capture what's playing was quite tricky.

There's no public API to do this — you'd have to pay $99 for an Apple Developer account to get an API key and access their internal requests, and I wasn’t going to pay for that.

So, I thought about making a small Node.js or Python script to extract that information directly from the Apple Music window and then send it to the SteelSeries local port that lets you show custom events on the DAC.

I ended up creating a Python script that now displays the current Apple Music song on my DAC.

The first thing I did was extract the currently playing song directly from the Apple Music window.
Once I had that information, I created a GameSense event — you can see how to do that in the SteelSeries documentation:
https://github.com/SteelSeries/gamesense-sdk/blob/master/doc/api/sending-game-events.md

After creating the event, I found that SteelSeries stores a file called coreProps.json in one of its folders. This file contains the IP and port where you need to send the requests.
However, I realized that these addresses are not static — they change each time you restart the computer.
So, to handle this, I made my script dynamically read the IP and port from the coreProps.json file every time it runs so you don't have to change the IP everytime you shutdown your computer.

Finally, I converted this script into a .exe file and created a shortcut in the Windows Startup folder. Now, every time I turn on my computer, the script runs automatically, and I don't need to start it manually.
Here is the script https://github.com/dmaj9/apple-music-steelseries-dac-integration
