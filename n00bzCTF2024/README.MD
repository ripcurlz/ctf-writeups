# n00bzCTF2024

i was part of the team "0xB8000" in this competition.

official github containing the source code of the challenges and the official writeups:

https://github.com/n00bzUnit3d/n00bzCTF2024-Official-Writeups

## addition

category: misc

looking at the given `server.py`, the needed answer is "-1". `range(-1)` does not do anything in a loop, and at the end of the source code, the slice of `flag[:-1]` gives you the whole flag.

using pwntools, see the solution in [solution.py](addition/solution.py).

## evm

category: blockchain

[evm.txt](evm/evm.txt) contains the bytecode which can be decompiled with websites like https://ethervm.io/decompile

the compiled bytecode, to opcodes is:

```
label_0000:
    0000    5F  5F
    // Stack delta = +0
    // Block terminates

    0001    34    CALLVALUE
    0002    61    PUSH2 0x1337
    0005    02    MUL
    0006    65    PUSH6 0xfdc29ff358a3
    000D    14    EQ
    000E    60    PUSH1 0x12
    0010    57    *JUMPI
    0011    FF    *SELFDESTRUCT
    0012    00    *STOP
```

looking at the opcodes, it becomes clear, that we are searching for a number, which multiplied with `0x1337`, is equal to `0xfdc29ff358a3`. that way, we get the needed
jump to address `0x12`: [solution.py](evm/solution.py).

## file-sharing-portal

category: web

the source code shows, that the server untars any file we give it. i searched for "python tar vulnerabilities" and stumbled across this helpful blog post: https://blog.bi0s.in/2020/06/07/Web/Defenit20-TarAnalyzer/, which shows that we can exploit a vulnerability called "zip-slip" here.

the `Dockerfile` of the given source code shows that there is a cronjob present which uses `run-parts` (in `/etc/cron.custom/cleanup-cron`) to run all scripts present in the `/etc/cron.custom` folder. this can be utilized, if we overwrite the contents of this file with e.g. a bash script which is then executed by `run-parts`. we also need to overwrite this file, because otherwise, every minute the uploads folder will be cleared.

the problem is, that we do not know what the name of the flag file is. since it will probably be the only file with a file ending of `*.txt` except `requirements.txt`, i used a `find` command as can be seen in [solution.py](file-sharing-portal/solution.py). the `find` command will get the file contents of the flag file and write it to a file name known to us.

since there is a filter present on the server which files and folder can be read from, i created a dir in the payload at `/app/uploads/abcdef1234567890` beforehand with the `find` command.

after 1-2 minutes after your upload of your python-crafted tar (after the cronjob kicked in) you should be able to read the flag by browsing to the path `/read/abcdef1234567890/abcdef1234567890` in your browser or using any other tool to do a HTTP GET request.

## focus-on-yourself

category: web

looking at the given docker-compose file, you can see that we want to get the environment variable called "FLAG". the application is a flask powered web app where you can upload images, which are then displayed. the content of the pictures is base64 encoded when you look at the source of the html, e.g. in your browser.

trying LFI, i found that the path `/view?image=../../../etc/passwd` gets you the base64 encoded content of the passwd file.

since we want an env var, `/view?image=../../../proc/self/environ` gives the current state of the environment variables. after base64 decoding the result string, you get the flag.

## passwordless

category: web

`@app.route('/<uid>')` returns you the flag on a HTTP POST, if the POST parameter `username` equals `str(uuid.uuid5(uuid.UUID('13371337-1337-1337-1337-133713371337'),'admin123'))`.

possible solution:

```python
import uuid

import requests

leet = uuid.UUID('13371337-1337-1337-1337-133713371337')

uid = str(uuid.uuid5(leet,'admin123'))

# replace with the needed IP and port
host = "localhost:1337"

get = requests.get(f"http://{host}/{uid}")

print(get.text)
```

## wave

category: forensics

the given file was a corrupted wav file. inspecting it with `hexedit` showed that the first 40 bytes had to be repaired. the header of 44 bytes was not matching the WAV header (source: https://en.wikipedia.org/wiki/WAV):

```
[Master RIFF chunk]
   FileTypeBlocID  (4 bytes) : Identifier « RIFF »  (0x52, 0x49, 0x46, 0x46)
   FileSize        (4 bytes) : Overall file size minus 8 bytes
   FileFormatID    (4 bytes) : Format = « WAVE »  (0x57, 0x41, 0x56, 0x45)

[Chunk describing the data format]
   FormatBlocID    (4 bytes) : Identifier « fmt␣ »  (0x66, 0x6D, 0x74, 0x20)
   BlocSize        (4 bytes) : Chunk size minus 8 bytes, which is 16 bytes here  (0x10)
   AudioFormat     (2 bytes) : Audio format (1: PCM integer, 3: IEEE 754 float)
   NbrChannels     (2 bytes) : Number of channels
   Frequence       (4 bytes) : Sample rate (in hertz)
   BytePerSec      (4 bytes) : Number of bytes to read per second (Frequence * BytePerBloc).
   BytePerBloc     (2 bytes) : Number of bytes per block (NbrChannels * BitsPerSample / 8).
   BitsPerSample   (2 bytes) : Number of bits per sample

[Chunk containing the sampled data]
   DataBlocID      (4 bytes) : Identifier « data »  (0x64, 0x61, 0x74, 0x61)
   DataSize        (4 bytes) : SampledData size
   SampledData
```

after correction of the header bytes, the audio file could be played. it seems to be morsecode!

with e.g. this site: https://morsecode.world/international/decoder/audio-decoder-adaptive.html, one could upload the wav file which then gave the flag after converting the morsecode to readable letters.