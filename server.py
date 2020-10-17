if __name__ == "__main__":
    import os
    from main import app
    import waitress

    port = os.environ["PORT"]
    print(f"start server {port=}")
    waitress.serve(app, port=port)
