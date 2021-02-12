import socket

request_header = (
    "GET / HTTP/1.1\r\n"
    "Accept: image/gif, image/jpeg, */*\r\n"
    "Accept-Language: ja\r\n"
    "Accept-Encoding: gzip, deflate\r\n"
    "User-Agent: Mozilla/4.0 (Compatible; MSIE 6.0; Windows NT 5.1;)\r\n"
    "Host: www.xxx.zzz\r\n"
    "Connection: Keep-Alive\r\n"
    "\r\n"
)


def read(s):
    msg = b""
    while True:
        data = s.recv(1024)
        msg += data
        if len(data) < 1024:
            break
    return msg


def get():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("", 1235))

    print(s.send(bytes(request_header, "utf-8")))

    msg = read(s)

    print(msg.decode("utf-8"))
    s.close()


if __name__ == "__main__":
    get()
