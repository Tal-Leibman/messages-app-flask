### Prerequisites
* python 3.8
* pipenv (recommended for better dependencies management) , just pip also works
### Environment variables
* `DATABASE_URL` connection string to an sql database
* `ECHO_SQL_LOGS` set to 1 for debugging
### Local
* `python main.py debug` to run local flask debug server
* use local postgres docker image for a database
* for example  `docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres` 
### Prod
* the server will listen to requests on the port found in environment variable `PORT` 
* `python main.py prod` to run waitress WSGI server
### Formatter
* Black for consistent code style  https://pypi.org/project/black/