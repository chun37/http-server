import socket
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


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


html_template = """
<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="utf-8">
        <title>{}</title>
    </head>
    <body>
        {}
    </body>
</html>
"""[
    1:-1
]


@dataclass
class FileServer:
    path: str

    def get_html(self):
        target_path = Path(f".{self.path}")
        if target_path.exists() is False:
            return None

        if target_path.is_dir():
            inner_html = self.get_directories_html(target_path)
        else:
            inner_html = self.get_file_html(target_path)

        return html_template.format(self.path, inner_html)

    def get_file_html(self, file):
        return file.read_text()

    def get_li_tag(self, file):
        return (
            f'<li><a href="/{file}">{file.name}{"/" if file.is_dir() else ""}</a></li>'
        )

    def get_directories_html(self, file):
        files = file.glob("*")
        return "<ul>\n" + "\n".join(self.get_li_tag(f) for f in files) + "\n</ul>"


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((socket.gethostname(), 1235))
        s.listen(5)

        while True:
            client_socket, address = s.accept()
            with client_socket:
                http_header = read_http_header(client_socket)
                request_line = http_header[0]
                METHOD, PATH, HTTP_VERSION = request_line.split()
                print(PATH)

                html = FileServer(PATH).get_html()
                if html is None:
                    response = HTTPResponse(1.0, 404, "Not Found")
                else:
                    response = HTTPResponse(1.0, 200, "OK")
                    response.set_content(html.encode("utf-8"))

                client_socket.send(response.to_bytes())
