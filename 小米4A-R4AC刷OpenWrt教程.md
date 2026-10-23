# 小米路由器 4A 100M（R4AC）刷 OpenWrt 完整教程

> 亲测成功：小米路由器 4A 100M 版（型号 R4AC，MT7628AN），MiWiFi 稳定版 2.18.58 → OpenWrt 23.05.5。
> 全程无需拆机、无需编程器，纯软件漏洞拿 root + 刷机。

---

## ⚠️ 重要声明

1. **刷机有风险，变砖自负**。请严格按照本文步骤操作，不要跳步。
2. 本文记录的**踩坑和变砖教训**，都是血泪换来的，务必读完再动手。
3. **务必先备份**，尤其是 Factory 分区（含 MAC、无线校准数据），备份了才有救砖底气。

---

## 一、设备信息

| 项目 | 内容 |
|------|------|
| 型号 | 小米路由器 4A 100M 版（R4AC） |
| 芯片 | MediaTek MT7628AN |
| 内存 / Flash | 64MB / 16MB |
| 官方固件版本 | 2.18.58（已验证可刷） |
| 目标系统 | OpenWrt 23.05.5 |
| 刷机方式 | 软件漏洞提权（OpenWRTInvasion），无需拆机 |

> ⚠️ **注意区分百兆版和千兆版**：本教程只针对 **100M 百兆版（R4AC）**。千兆版（R4AG / R4A Gigabit）芯片是 MT7621，固件不通用，混刷必砖。

---

## 二、所需工具

| 工具 | 用途 |
|------|------|
| [OpenWRTInvasion](https://github.com/acecilia/OpenWRTInvasion) | 漏洞利用脚本，拿 root + 开启 telnet/ssh/ftp |
| Python 3.8+ | 运行漏洞脚本（Windows 可直接跑，无需 Docker） |
| OpenWrt 固件 | `openwrt-23.05.5-ramips-mt76x8-xiaomi_mi-router-4a-100m-squashfs-sysupgrade.bin` |
| 小米官方修复工具（MIWIFIRepairTool） | 救砖备用 |
| 官方原厂固件 2.18.58 | 救砖备用 |

### 固件下载与校验

OpenWrt 固件（务必选 `mi-router-4a-100m`，不要选 gigabit）：

```
openwrt-23.05.5-ramips-mt76x8-xiaomi_mi-router-4a-100m-squashfs-sysupgrade.bin
```

SHA256 校验值（刷机前必须核对，防止下载损坏导致变砖）：

```
862d1dd37e0b5fe6b2f36fb74c20903372f130dd2e04c24bd53eb3c3a01780a4
```

原厂固件（救砖用）：

```
https://bigota.miwifi.com/xiaoqiang/rom/r4ac/miwifi_r4ac_firmware_e9eec_2.18.58.bin
```

---

## 三、刷机流程

### 第 1 步：准备工作

1. 路由器接通电源，电脑用**网线**连到路由器的 LAN 口（有线连接最稳，避免 WiFi 中断）。
2. 浏览器打开 `http://192.168.31.1`，登录管理后台（默认密码通常贴在路由器底部标签上）。
3. **获取 stok**：登录后，地址栏 URL 会变成类似：

   ```
   http://192.168.31.1/cgi-bin/luci/;stok=<你的stok>/web/home#router
   ```

   其中 `<你的stok>` 那一长串就是 stok，复制保存下来。

> 💡 漏洞脚本必须从**登录路由器时所用的同一台电脑、同一个 IP** 运行，否则会失败。

### 第 2 步：运行漏洞脚本拿 root

```bash
# 克隆项目（如 GitHub 直连慢，可用镜像 ghfast.top 加速）
git clone https://github.com/acecilia/OpenWRTInvasion.git
cd OpenWRTInvasion

# 安装依赖
pip3 install -r requirements.txt

# 运行漏洞脚本
python3 remote_command_execution_vulnerability.py
```

按提示输入：
- **路由器 IP**：`192.168.31.1`
- **stok**：第 1 步复制的字符串

脚本运行成功后，会开启三个服务：

| 服务 | 端口 | 账号 | 密码 |
|------|------|------|------|
| telnet | 23 | root | root |
| ssh | 22 | root | root |
| ftp | 21 | root | root |

> ⚠️ 脚本有已知的瞬时不稳定性，**一次失败就再跑一次**，通常第二次就成功。

### 第 3 步：备份关键分区（救砖保险，必做！）

连接 telnet：

```bash
telnet 192.168.31.1
# 账号 root，密码 root
```

备份所有 mtd 分区（重点备份 Factory，含 MAC 和无线校准数据）：

```bash
cd /tmp
mkdir -p backup
# 查看分区表
cat /proc/mtd

# 逐分区备份（示例，按你的 /proc/mtd 实际分区来）
dd if=/dev/mtd0 of=/tmp/backup/mtd0.bin
dd if=/dev/mtd1 of=/tmp/backup/mtd1.bin
dd if=/dev/mtd2 of=/tmp/backup/mtd2.bin
dd if=/dev/mtd3 of=/tmp/backup/mtd3.bin
dd if=/dev/mtd4 of=/tmp/backup/mtd4.bin
dd if=/dev/mtd5 of=/tmp/backup/mtd5.bin
```

然后用 FTP 把这些 `.bin` 下载回电脑保存（用 FTP 客户端或脚本，例如 FileZilla，连接 `192.168.31.1:21`）。

> ⚠️ **Factory 分区是命根子**，丢了 MAC 地址和无线校准数据，即使刷活 WiFi 也会异常。

### 第 4 步：上传 OpenWrt 固件到路由器

把固件传到路由器的 `/tmp` 目录。三种方式任选：

**方式 A：FTP 上传（推荐，最稳）**

用 FTP 客户端连接 `192.168.31.1:21`，把固件上传到 `/tmp/openwrt.bin`。

**方式 B：HTTP 下载（需关闭 Windows 防火墙对入站的拦截）**

```bash
# 在电脑上起一个 HTTP 服务器（假设电脑 IP 是 192.168.31.54）
python3 -m http.server 8000

# 在路由器 telnet 里执行
cd /tmp
wget http://192.168.31.54:8000/openwrt.bin -O openwrt.bin
```

**方式 C：U 盘 / scp 等方式**

> ⚠️ **坑**：`/tmp` 是内存盘，空间有限。如果上传时提示空间不足，先 `reboot` 路由器再重试，重启后 `/tmp` 空间会恢复。

### 第 5 步：校验固件完整性

上传后**必须校验 SHA256**，确保固件完整无损：

```bash
cd /tmp
# 使用漏洞脚本自带的 busybox 计算哈希
./busybox sha256sum openwrt.bin
```

核对输出是否等于：

```
862d1dd37e0b5fe6b2f36fb74c20903372f130dd2e04c24bd53eb3c3a01780a4
```

**不一致就绝不要刷**，重新上传。

### 第 6 步：刷入固件（全教程最关键的一步！）

> 🔴 **血泪教训，务必遵守**：
> 1. **必须用 `nohup` + `&` 后台执行**，脱离 telnet 会话。否则 5.9MB 固件写 SPI flash 需要 1-2 分钟，telnet 一旦断开，前台 `mtd` 进程会被终止，导致固件只写一半 → **变砖**。
> 2. **不要在刷写过程中反复 `dd` 读 flash 校验 MD5**，会把弱设备系统拖垮。
> 3. **耐心等待**，刷完会自动重启，不要手动干预。

执行刷写命令：

```bash
cd /tmp
nohup sh -c 'mtd -e OS1 -r write /tmp/openwrt.bin OS1' > /tmp/flash.log 2>&1 &
```

命令解释：
- `mtd -e OS1`：擦除 OS1 分区（百兆版 OS1 起始地址 `0x160000`）
- `-r`：写完后自动重启（配合后台执行没问题）
- `write /tmp/openwrt.bin OS1`：把固件写入 OS1 分区

执行后**静静等待约 90 秒**，路由器会自动重启。

### 第 7 步：验证刷机成功

等待重启后，检查：

1. `192.168.31.1` 已不通（原厂系统没了）；
2. `192.168.1.1` 通了（OpenWrt 默认管理地址），ping 测试 0% 丢包；
3. 端口 80（网页）、22（SSH）、53（DNS）已开放；
4. 浏览器打开 `http://192.168.1.1`，看到 **"LuCI - Lua Configuration Interface"** 即成功。

---

## 四、刷机后初始配置

### 1. 设置 root 密码（SSH 登录）

首次通过 SSH 登录：

```bash
ssh root@192.168.1.1
```

> 提示：旧版 dropbear 可能需加参数：`ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -c 3des-cbc root@192.168.1.1`

首次登录会要求设置密码（`passwd`），设一个强密码，此密码同时用于 LuCI 网页后台和 SSH。

### 2. 安装中文界面（可选）

```bash
opkg update
opkg install luci-i18n-base-zh-cn
uci set luci.main.lang='zh-cn'
uci commit luci
```

刷新网页后台即可看到中文界面。

### 3. 配置 WiFi（示例：只开 5G）

```bash
# 关闭 2.4G，开启 5G
uci set wireless.radio0.disabled='1'
uci set wireless.radio1.disabled='0'

# 设置 5G WiFi 名称和密码
uci set wireless.default_radio1.ssid='MyWifi_5G'
uci set wireless.default_radio1.encryption='psk2'
uci set wireless.default_radio1.key='你的WiFi密码'

uci commit wireless
wifi reload
```

---

## 五、救砖指南（万一变砖）

### 判断是否变砖

- **软砖（可救）**：刷机后路由器**橙色/蓝色灯闪烁**，或开机进入恢复模式，`192.168.1.1` / `192.168.31.1` 均不通。
- **硬砖（需编程器）**：连 Bootloader 都损坏，指示灯完全不亮或无反应。本文方法基本不会造成硬砖。

> 指示灯参考（小米官方）：**蓝灯闪烁 = 系统更新中**，**红灯 = 崩溃**，**橙灯闪烁 = 恢复模式**。

### 软砖救砖步骤

1. 下载并解压小米官方修复工具 **MIWIFIRepairTool**；
2. 下载原厂固件 `miwifi_r4ac_firmware_e9eec_2.18.58.bin`（约 11MB）；
3. **拔掉路由器电源**，用牙签/卡针按住 **Reset 按钮**不松手；
4. 保持按住 Reset，**插上电源**，等待约 10-15 秒直到指示灯进入恢复状态（通常是常亮或特定闪烁），再松开 Reset；
5. 电脑用网线连接路由器 LAN 口，打开修复工具，选择原厂固件，点击刷机；
6. 等待进度条走完，路由器重启后恢复原厂系统。

救砖过程中路由器网卡一度拿到 `169.254.x.x`（自动私有地址）是正常现象，说明系统正在恢复，耐心等待即可。

---

## 六、常见问题（FAQ）

**Q1：脚本运行失败 / 报错？**
A：OpenWRTInvasion 有已知的瞬时不稳定性，再跑一次通常成功。同时确认：固件版本在支持列表（2.18.58 已验证）、电脑和路由器在同一网段、用的是登录路由器时的同一 IP。

**Q2：上传固件时 `/tmp` 空间不足？**
A：`/tmp` 是内存盘。重启路由器后重试，空间会恢复。或改用更小的上传方式。

**Q3：路由器连不上 telnet？**
A：确认漏洞脚本提示成功、端口 23 已监听。Windows 可用 `telnet` 命令或第三方工具（PuTTY、Xshell）。

**Q4：刷完连不上 192.168.1.1？**
A：先确认网卡拿到的是 `192.168.1.x` 网段的 IP。OpenWrt 默认 DHCP 段是 `192.168.1.0/24`。必要时手动给电脑设静态 IP `192.168.1.100`。

**Q5：WiFi 搜不到 / 信号差？**
A：检查 Factory 分区是否备份/还原正确，它保存了无线校准数据。若丢失需重新校准。

---

## 七、致谢

- 漏洞与利用：[UltramanGaia](https://github.com/UltramanGaia/Xiaomi_Mi_WiFi_R3G_Vulnerability_POC) 的原版漏洞，[acecilia/OpenWRTInvasion](https://github.com/acecilia/OpenWRTInvasion) 的集成工具
- 刷机指导：[OpenWrt 官方论坛](https://forum.openwrt.org/t/xiaomi-mi-router-4a-gigabit-edition-r4ag-r4a-gigabit-fully-supported-but-requires-overwriting-spi-flash-with-programmer/36685)
- 设备支持：[OpenWrt Wiki - Xiaomi Mi Router 4A (100M)](https://openwrt.org/toh/xiaomi/mi_router_4a_mir4a_100m)

## 八、免责声明

本教程仅供学习和技术交流使用。刷机操作可能使设备失去保修、导致变砖或数据丢失。请在充分理解风险的前提下操作，作者不对任何损失负责。
