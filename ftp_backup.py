import socket
import os

def ftp_retrieve(host, port, remote_path, local_path):
    """通过 FTP 下载文件（极简 FTP 客户端，主动模式）"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((host, port))
    
    def read_line():
        data = b""
        while not data.endswith(b"\n"):
            chunk = s.recv(1)
            if not chunk:
                break
            data += chunk
        return data
    
    # 读欢迎信息
    print(read_line().decode().strip())
    
    # 发送命令
    def cmd(c):
        s.sendall((c + "\r\n").encode())
        return read_line().decode().strip()
    
    # 登录
    print(cmd("USER root"))
    print(cmd("PASS root"))
    
    # 二进制模式
    print(cmd("TYPE I"))
    
    # 主动模式 - 需要数据端口
    # 先开一个数据端口
    data_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_listen.bind(("0.0.0.0", 0))
    data_listen.listen(1)
    data_port = data_listen.getsockname()[1]
    
    # 发送 PORT 命令
    local_ip = s.getsockname()[0]
    ip_parts = local_ip.split(".")
    p1, p2 = data_port // 256, data_port % 256
    port_cmd = "PORT {},{},{},{},{},{}".format(*ip_parts, p1, p2)
    print(cmd(port_cmd))
    
    # 发送 RETR
    print(cmd("RETR " + remote_path))
    
    # 接受数据连接
    data_listen.settimeout(10)
    try:
        data_conn, _ = data_listen.accept()
    except socket.timeout:
        print("数据连接超时")
        return False
    
    # 接收数据
    with open(local_path, "wb") as f:
        while True:
            chunk = data_conn.recv(8192)
            if not chunk:
                break
            f.write(chunk)
    data_conn.close()
    data_listen.close()
    
    # 读完成信息
    print(read_line().decode().strip())
    
    # 退出
    print(cmd("QUIT"))
    s.close()
    return True

if __name__ == "__main__":
    os.makedirs("backup", exist_ok=True)
    files = ["mtd1.bin", "mtd2.bin", "mtd3.bin", "mtd4.bin", "mtd5.bin", "mtd6.bin"]
    for f in files:
        remote = "/tmp/backup/" + f
        local = "backup/" + f
        print("\n=== 下载 {} ===".format(f))
        try:
            ftp_retrieve("192.168.31.1", 21, remote, local)
            print("✅ {} 下载完成，大小 {} 字节".format(f, os.path.getsize(local)))
        except Exception as e:
            print("❌ {} 下载失败: {}".format(f, repr(e)))
