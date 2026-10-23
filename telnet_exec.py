import socket
import time
import sys

IAC = 255  # Interpret As Command
DONT = 254
DO = 253
WONT = 252
WILL = 251

def handle_telnet_negotiation(data):
    """处理 telnet 协商字节，返回处理后的数据"""
    i = 0
    result = []
    while i < len(data):
        if data[i] == IAC:
            if i + 1 < len(data):
                cmd = data[i+1]
                if cmd in (DO, DONT, WILL, WONT):
                    # 三字节命令
                    if i + 2 < len(data):
                        opt = data[i+2]
                        # 响应：拒绝所有 DO，接受 WILL
                        if cmd == DO:
                            # 回复 WONT
                            pass  # 我们在外面统一处理
                        i += 3
                    else:
                        i += 2
                else:
                    # 两字节命令
                    i += 2
            else:
                i += 1
        else:
            result.append(data[i])
            i += 1
    return bytes(result)

def telnet_exec(host, port, commands, wait_after=2.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(8)
    s.connect((host, port))
    
    # 发送协商响应
    def respond_negotiation(raw):
        i = 0
        responses = b""
        while i < len(raw):
            if raw[i] == IAC and i + 2 < len(raw):
                cmd = raw[i+1]
                opt = raw[i+2]
                if cmd == DO:
                    responses += bytes([IAC, WONT, opt])
                elif cmd == WILL:
                    responses += bytes([IAC, DO, opt])
                i += 3
            else:
                i += 1
        if responses:
            try:
                s.sendall(responses)
            except:
                pass
    
    def recv_all(duration=1.5):
        s.settimeout(0.3)
        buf = b""
        end = time.time() + duration
        while time.time() < end:
            try:
                d = s.recv(4096)
                if not d:
                    break
                respond_negotiation(d)
                buf += handle_telnet_negotiation(d)
            except socket.timeout:
                continue
            except Exception:
                break
        return buf

    time.sleep(1.5)
    output = recv_all(1.5)
    
    # 登录
    s.sendall(b"root\n")
    time.sleep(1.2)
    output += recv_all(1.2)
    s.sendall(b"root\n")
    time.sleep(1.2)
    output += recv_all(1.5)
    
    # 执行命令
    for cmd in commands:
        s.sendall((cmd + "\n").encode())
        time.sleep(wait_after)
        output += recv_all(wait_after)
    
    s.sendall(b"exit\n")
    time.sleep(0.3)
    try:
        s.close()
    except:
        pass
    return output.decode("utf-8", errors="replace")

if __name__ == "__main__":
    cmds = sys.argv[1:] if len(sys.argv) > 1 else ["echo test"]
    out = telnet_exec("192.168.31.1", 23, cmds)
    print(out)
