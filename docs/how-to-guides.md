# How-To Guides

## Building instructions (for the maintainer)

Run this command in the directory where `pyproject.toml` is located.
```
python3 -m build
```
Two files will be created in the `dist` directory:
```
dist/
├── dope-0.0.1-py3-none-any.whl
└── dope-0.0.1.tar.gz
```

***
## Development flow

One of the ways of testing the package during development can be using the virtual environment:

1. Create it:
`$ python3 -m venv venv`

2. Activate it:
`$ source venv/bin/activate`

3. Install dope:
`pip3 install -e .`

4. Write and test new functions ...

5. Uninstall dope:
`$ pip3 uninstall dope`

6. Deactivate it:
`$ deactivate`

7. Clean up:
`rm -r venv`

***
## Using pomodoro timers

There are 3 commands that can be used for managing timers:
* `d -ps {timout in minutes} {timer name}`, for example `d -ps 15 emails`.
* `d -pl`
* `d -pk` {part of PID}

If you want to use an exclamation mark (!) in the name of a timer, the name should use single quotes, e.g.`d -ps 20 fw!1234`.

***