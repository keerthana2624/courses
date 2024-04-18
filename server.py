import socket
import mimetypes
import psycopg2
import json

conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="keerthi058",
    host="Localhost"
)

cur = conn.cursor()

# Check if the table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'students'
    )
""")
table_exists = cur.fetchone()[0]

# If the table doesn't exist, create it
if not table_exists:
    cur.execute("CREATE TABLE students (username varchar, password varchar)")
    conn.commit()


# Check if the table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'teachers'
    )
""")
table_exists = cur.fetchone()[0]

# If the table doesn't exist, create it
if not table_exists:
    cur.execute("CREATE TABLE teachers (username varchar, password varchar,email varchar,phone varchar)")
    conn.commit()


# Check if the table exists
cur.execute("""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'courses'
    )
""")
table_exists = cur.fetchone()[0]

# If the table doesn't exist, create it
if not table_exists:
    cur.execute("CREATE TABLE courses (coursename varchar, price varchar,rating varchar)")
    conn.commit()

cur.close()


def run_server(host='127.0.0.1', port=2001):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server is running on {host}:{port}")
        print("Press Ctrl+C to stop the server.")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected by {addr}")

            request = client_socket.recv(2048).decode('utf-8')
            print(f"Request received:\n{request}")

            response = handleRequest(request)
            client_socket.sendall(response)
            client_socket.close()


def serverFile(file_path):
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except:
        return f"HTTP/1.1 404 NOT FOUND\n\n file not found".encode()


def userInput(request):
    body = request.split('\r\n\r\n')[1]
    postData = body
    formData = {}
    for pair in postData.split('&'):
        key, value = pair.split('=')
        formData[key] = value
    return formData


sessions = {}


def handleRequest(request):
    global conn

    parseRequest = request.split('\n')[0].split()
    method = parseRequest[0]
    uri = parseRequest[1]

    if '/favicon.ico' in request:
        return ''.encode()
    if method == 'GET':
        if uri == '/':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:{mimetypes}\r\n\r\n'.encode() + serverFile('default.html')
        if uri == '/login':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:{mimetypes}\r\n\r\n'.encode() + serverFile('login.html')
        if uri == '/teacherlogin':
            response = f'HTTP/1.1 200 OK\r\nContent-Type:{mimetypes}\r\n\r\n'.encode() + serverFile('teacherlogin.html')
        
        elif uri == '/api/table':
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM courses;")
            courses = cur.fetchall()

            response = ('HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(courses)).encode()
            # cur.close()

        elif uri.endswith('.js'):  # /scrit.js
            response = (f'HTTP/1.1 200 OK\nContent-Type: text/css\n\n').encode() + serverFile(uri[1:].strip())
        elif uri.endswith('.webp'):  # /scrit.js
            response = (f'HTTP/1.1 200 OK\nContent-Type:{mimetypes} \n\n').encode() + serverFile(uri[1:].strip())
        elif uri == '/logout':
            response = f'HTTP/1.1 302 FOUND\r\nLocation: /\r\n\r\n'.encode()

        return response

    elif method == 'POST':
        if uri == '/login':
            data = userInput(request)
            cur = conn.cursor()
            username = data.get('username').replace('+', ' ')
            password = data.get('password')
            cur.execute(
                f"SELECT EXISTS (SELECT 1 FROM students WHERE username = '{username}' AND password = '{password}') AS password_exists;")
            password_exists = cur.fetchone()[0]
            cur.close()

            if password_exists:
                response = f'HTTP/1.1 200 OK\r\nContent-Type:{mimetypes}\r\n\r\n'.encode() + serverFile(
                    'studenthomepage.html')
            else:
                response = f'HTTP/1.1 302 FOUND\r\nLocation: /login\r\n\r\n'.encode()

        elif uri == '/teacherlogin':
            data = userInput(request)
            cur = conn.cursor()
            username = data.get('username').replace('+', ' ')
            password = data.get('password')
            cur.execute(
                f"SELECT EXISTS (SELECT 1 FROM teachers WHERE username = '{username}' AND password = '{password}') AS password_exists;")
            password_exists = cur.fetchone()[0]
            cur.close()

            if password_exists:
                response = f'HTTP/1.1 200 OK\r\nContent-Type:{mimetypes}\r\n\r\n'.encode() + serverFile(
                    'teacherhomepage.html')
            else:
                response = f'HTTP/1.1 302 FOUND\r\nLocation: /teacherlogin\r\n\r\n'.encode()

        elif uri == '/teachersubmit':
            data = userInput(request)
            cur = conn.cursor()
            coursename = data.get('coursename')
            price = data.get('price')
            rating = data.get('rating')
            cur.execute(f"INSERT INTO courses values('{coursename}','{price}','{rating}');")
            conn.commit()
            cur.close()

            response = f'HTTP/1.1 200 OK\r\nContent-Type:{mimetypes}\r\n\r\n'.encode() + serverFile(
                'teacherhomepage.html')

        return response


if __name__ == '__main__':
    run_server()
