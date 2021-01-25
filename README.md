# Persimmon Banking

### Development Setup

- Create a new virtualenv for this project: `mkvirtualenv --python=$(which python3) persimmon`
- Install the python dependencies: `pip install -r requirements.txt`

To reactivate this virtualenv whenver you want to run python in your shell: run `workon persimmon`.
You can configure PyCharm to use this virtualenv with the "project interpreter" option: navigate it to something like `~/.virtualenvs/persimmon/bin/python`
You can also configure PyCharm to have django-specific autocompletions - this is highly reccommended. Go to Settings -> Languages and Frameworks -> Django and select the `persimmon` folder as the django project root. You may also need to specify the path to the settings.py file - this is `persimmon/persimmon/settings.py`.
