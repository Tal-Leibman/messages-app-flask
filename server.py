

if __name__ == '__main__':
    import os
    from main import app
    import waitress
    port = os.environ["PORT"]
    host = os.environ["HOST"]
    print(f"start server {host=} {port=}")
    waitress.serve(app,host=host,port=port)