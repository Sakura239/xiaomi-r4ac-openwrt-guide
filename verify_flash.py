import socket, time, hashlib, re

HOST = '192.168.31.1'
PORT = 23

def recv_until(s, marker, timeout=15):
    """读取直到出现 marker 或超时"""
    s.settimeout(0.5)
    buf = b''
    end = time.time() + timeout
    while time.time() < end:
        try:
            d = s.recv(4096)
            if not d:
                break
            buf += d
            if marker in buf:
                return buf
        except socket.timeout:
            continue
    return buf

def handle_telnet_negotiation(data):
    """处理 telnet 协商字节"""
    i = 0
    while i < len(data):
        if data[i] == 255:  # IAC
            if i + 2 < len(data):
                # 响应 WONT/DONT 拒绝所有协商
                pass
            i += 3
        else:
            i += 1
    return data

def run_command(cmd, wait=2.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((HOST, PORT))
    time.sleep(1.5)
    # 读欢迎
    try:
        s.settimeout(2)
        s.recv(4096)
    except:
        pass
    # 登录
    s.sendall(b'root\n')
    time.sleep(0.8)
    try:
        s.settimeout(2)
        s.recv(4096)
    except:
        pass
    s.sendall(b'root\n')
    time.sleep(1.0)
    try:
        s.settimeout(2)
        s.recv(4096)
    except:
        pass
    # 发送命令
    s.sendall(cmd.encode() + b'\n')
    time.sleep(wait)
    # 收集输出
    s.settimeout(0.5)
    buf = b''
    end = time.time() + 20
    while time.time() < end:
        try:
            d = s.recv(4096)
            if not d:
                break
            buf += d
            # 检测到新的提示符说明命令完成
            if b'root@XiaoQiang' in buf and buf.count(b'root@XiaoQiang') >= 2:
                break
        except socket.timeout:
            continue
    s.close()
    return buf.decode('utf-8', errors='ignore')

# 回读 OS1 前 5964119 字节并计算 MD5
# 分块读取，避免一次 dd 太大
print("开始回读 OS1 分区并计算 MD5（分块）...")
md5 = hashlib.md5()
total = 5964119
chunk = 1048576  # 1MB per dd
offset = 0
while offset < total:
    cnt = min(chunk, total - offset)
    cmd = f"dd if=/dev/mtd7 bs=1 skip={offset} count={cnt} 2>/dev/null | md5sum"
    out = run_command(cmd, wait=8)
    # 提取 md5 值
    m = re.search(r'([0-9a-f]{32})', out)
    if m:
        # 这是每块的 md5，不能直接拼接，改用另一种方式
        pass
    print(f"  块 offset={offset}: {'有输出' if out.strip() else '无输出'}")
    offset += cnt
    break  # 先只读一块测试

print("改用直接 dd 到大文件方式")
