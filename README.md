
![Newman Api Test](https://github.com/Tal-Leibman/messages-app-flask/workflows/Newman%20Api%20Test/badge.svg?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### Prerequisites
* python 3.8
* pipenv (recommended for better dependencies management) , just pip also works
### Usage examples 
* `python main.py --help` for all cli args
* example for running local flask debug `python main.py --db-url=postgres://{user}:{password}@{hostname}:{port}/{database-name} --port=5000 --debug=yes`
* `python main.py` to run waitress WSGI server with port and db-url from environment variables (suitable for heroku setup) 
### Formatter
* Black for consistent code style  https://pypi.org/project/black/
### Tests
* Use postman_collection.json and postman_environment.json in postman test runner
