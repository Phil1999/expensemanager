from waitress import serve
from expensemanager.wsgi import application

if __name__ == '__main__':
    serve(application, host = "localhost", port = '8000')