import socket


def read_http_header(s, decoded=""):

    data = s.recv(1024)
    decoded += data.decode("utf-8")

    if (header_end_index := decoded.find("\r\n\r\n")) == -1:
        return read_header(s, decoded)

    return decoded.split("\r\n")


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 1235))
        s.listen(5)

        while True:
            client_socket, address = s.accept()
            with client_socket:
                headers = read_http_header(client_socket)
                print(headers)

                client_socket.send(bytes("Welcome to the server!", "utf-8"))
