import socket
from dataclasses import dataclass
from typing import Optional


@dataclass
class HTTPResponse:
    version: float
    status_code: int
    status_message: str
    header: Optional[dict[str, str]] = None
    content: Optional[bytes] = None

    def __post_init__(self):
        if self.header is None:
            self.header = {}
        self.header["Host"] = socket.gethostname()

    def set_content(self, data: bytes):
        self.content = data
        self.header["Content-Length"] = str(len(data))

    def get_header_string(self):
        return (
            "\r\n".join(f"{key}: {value}" for key, value in self.header.items())
            + "\r\n"
        )

    def to_bytes(self):
        data = b""
        http_header = (
            f"HTTP/{self.version} {self.status_code} {self.status_message}\r\n"
            f"{self.get_header_string()}"
            "\r\n"
        ).encode("utf-8")

        data += http_header

        if self.content is not None:
            data += self.content

        return data


def read_http_header(s, decoded=""):

    data = s.recv(1024)
    decoded += data.decode("utf-8")

    if (header_end_index := decoded.find("\r\n\r\n")) == -1:
        return read_header(s, decoded)

    return decoded.split("\r\n")


@dataclass
class RequestHandler:
    route: dict[str, callable]

    def add(self, path, function):
        self.route[path] = function

    def get_function(self, path):
        return self.route.get(path)


def return_simple_html():
    with open("simple.html", "rb") as f:
        file_data = f.read()
    return file_data


if __name__ == "__main__":
    request_handler = RequestHandler({})
    request_handler.add("/html", return_simple_html)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((socket.gethostname(), 1235))
        s.listen(5)

        while True:
            client_socket, address = s.accept()
            with client_socket:
                http_header = read_http_header(client_socket)
                request_line = http_header[0]
                METHOD, PATH, HTTP_VERSION = request_line.split()

                response = HTTPResponse(1.0, 200, "OK")
                if (func := request_handler.get_function(PATH)) is not None:
                    content = func()
                    response.set_content(content)

                client_socket.send(response.to_bytes())
