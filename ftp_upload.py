import socket
import os

def ftp_store(host, port, local_path, remote_path):
    """通过 FTP 上传文件到路由器（主动模式）"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect((host, port))
    
    def read_line():
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(1)
            if not chunk:
                break
            data += chunk
        return data
    
    def cmd(c):
        s.sendall((c + "\r\n").encode())
        return read_line().decode().strip()
    
    print(cmd("USER root"))
    print(cmd("PASS root"))
    print(cmd("TYPE I"))
    
    # 主动模式数据端口
    data_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_listen.bind(("0.0.0.0", 0))
    data_listen.listen(1)
    data_port = data_listen.getsockname()[1]
    local_ip = s.getsockname()[0]
    ip_parts = local_ip.split(".")
    p1, p2 = data_port // 256, data_port % 256
    print(cmd("PORT {},{},{},{},{},{}".format(*ip_parts, p1, p2)))
    
    print(cmd("STOR " + remote_path))
    
    data_listen.settimeout(20)
    try:
        data_conn, _ = data_listen.accept()
    except socket.timeout:
        print("数据连接超时")
        return False
    
    # 发送文件
    file_size = os.path.getsize(local_path)
    sent = 0
    with open(local_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            data_conn.sendall(chunk)
            sent += len(chunk)
            if sent % (512*1024) < 8192:
                print("  已上传 {}/{} 字节".format(sent, file_size))
    data_conn.close()
    data_listen.close()
    
    print(read_line().decode().strip())
    print(cmd("QUIT"))
    s.close()
    print("✅ 上传完成: {} 字节".format(sent))
    return True

if __name__ == "__main__":
    local = r"C:\Users\lzh\Desktop\firmware\openwrt.bin"
    print("=== 上传固件到路由器 /tmp/openwrt.bin ===")
    ftp_store("192.168.31.1", 21, local, "/tmp/openwrt.bin")
