I searched the whole workspace and can't find any helper that builds a shell command from a user-supplied path — `client.py` just retries a `transport(path)` call with no shell/subprocess usage, and there's no other Python file matching that description.

Could you point me to the file (or paste the code)? I don't want to guess and invent a new shell-command builder from scratch, since getting that wrong (e.g., string-formatting into `shell=True`) is exactly the kind of injection risk this needs to avoid.
