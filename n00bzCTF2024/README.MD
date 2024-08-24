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