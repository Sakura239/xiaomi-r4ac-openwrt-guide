# 小米路由器 4A 100M（R4AC）刷 OpenWrt 教程

[![OpenWrt](https://img.shields.io/badge/OpenWrt-23.05.5-blue?logo=openwrt)](https://openwrt.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Router](https://img.shields.io/badge/Xiaomi-4A%20100M-orange)](https://www.mi.com/)

> 亲测成功：小米路由器 4A 100M 版（型号 R4AC，MT7628AN），从 MiWiFi 稳定版 2.18.58 刷入 OpenWrt 23.05.5。
> **全程无需拆机、无需编程器**，纯软件漏洞提权 + 刷机。

![封面图](cover.png)

---

## 📖 项目简介

本项目提供一套**完整、可复现**的教程，教你如何给小米路由器 4A 100M 版（R4AC）刷入 OpenWrt 系统。

刷机后，这台几十块钱的路由器将解锁大量进阶能力：

- 🔓 完全的 root 权限和软件自由
- 🌐 可作**旁路由 / 透明网关**（科学上网、去广告、DNS 优化）
- 🧩 海量 LuCI 插件生态（AdGuard、SmartDNS、DDNS、多拨等）
- 📡 自定义 WiFi 频段与功率（支持只开 5G）
- 🛠️ 完整的 Linux 网络工具箱

教程覆盖了**从零到成功**的全流程，并重点记录了**两次变砖、两次救砖**换来的血泪教训，帮你避开所有坑。

---

## 🚀 快速开始

### 适用设备

| 项目 | 内容 |
|------|------|
| 型号 | 小米路由器 4A 100M 版（R4AC） |
| 芯片 | MediaTek MT7628AN |
| 内存 / Flash | 64MB / 16MB |
| 官方固件 | 2.18.58（已验证） |
| 目标系统 | OpenWrt 23.05.5 |

> ⚠️ **只适用于百兆版（R4AC）**。千兆版（R4AG / R4A Gigabit）芯片是 MT7621，固件不通用，混刷必砖。

### 三步概览

1. **拿 root**：用 [OpenWRTInvasion](https://github.com/acecilia/OpenWRTInvasion) 漏洞脚本开启 telnet/ssh
2. **刷固件**：上传 OpenWrt 固件，校验 SHA256 后后台刷入
3. **配系统**：设密码、装中文、配 WiFi

**完整图文教程请阅读**：👉 [《小米4A-R4AC刷OpenWrt教程.md》](./小米4A-R4AC刷OpenWrt教程.md)

---

## 📁 目录结构

```
.
├── 小米4A-R4AC刷OpenWrt教程.md     # 📖 核心教程（从这里开始）
├── README.md                        # 项目说明（本文件）
├── remote_command_execution_vulnerability.py  # 漏洞利用脚本（来自 OpenWRTInvasion）
├── script.sh                        # 漏洞利用的 shell 载荷
├── script_tools/                    # 所需二进制（busybox、dropbear，MIPS 架构）
│   ├── busybox-mipsel
│   └── dropbearStaticMipsel.tar.bz2
├── ftp_upload.py                    # FTP 上传固件脚本（Windows 可用）
├── ftp_backup.py                    # FTP 下载分区备份脚本
├── telnet_exec.py                   # telnet 自动化执行脚本（处理协商字节）
├── verify_flash.py                  # 刷写后校验脚本
├── tcp_file_server.py               # 本地文件服务（配合漏洞脚本）
├── speedtest_urls_template.xml      # 漏洞利用所需模板
└── requirements.txt                 # Python 依赖
```

---

## 🛠️ 环境要求

- **Python 3.8+**（脚本支持原生 Windows，无需 Docker）
- **Git**（克隆本项目）
- 电脑与路由器**网线直连**（有线最稳）
- 固件：`openwrt-23.05.5-ramips-mt76x8-xiaomi_mi-router-4a-100m-squashfs-sysupgrade.bin`

### 固件 SHA256 校验值

```
862d1dd37e0b5fe6b2f36fb74c20903372f130dd2e04c24bd53eb3c3a01780a4
```

> 🔴 **刷机前必须核对**，防止固件损坏导致变砖。

---

## ⚠️ 核心血泪教训（务必先读）

| 教训 | 后果 | 正确做法 |
|------|------|----------|
| telnet **前台**跑 `mtd` | 会话断开 → 固件写一半 → **变砖** | 用 `nohup + &` 后台执行 |
| 刷写中反复 `dd` 读 flash 校验 | 弱设备系统被拖垮 | 刷完耐心等 90 秒自动重启 |
| 不备份 Factory 分区 | 丢 MAC + 无线校准数据 | 刷前必做全分区备份 |
| 百兆/千兆固件混用 | 直接变砖 | 认准 `mi-router-4a-100m` |

---

## 🔧 常见问题

- **脚本运行失败？** OpenWRTInvasion 有瞬时不稳定性，再跑一次通常成功。
- **`/tmp` 空间不足？** 重启路由器后重试（`/tmp` 是内存盘）。
- **刷完连不上 192.168.1.1？** 确认网卡拿到 `192.168.1.x` 网段 IP，必要时手动设静态 IP。

更多问题见教程的 FAQ 章节。

---

## 🙏 致谢

- 漏洞与利用：[UltramanGaia](https://github.com/UltramanGaia/Xiaomi_Mi_WiFi_R3G_Vulnerability_POC) 的原版漏洞，[acecilia/OpenWRTInvasion](https://github.com/acecilia/OpenWRTInvasion) 的集成工具
- 刷机指导：[OpenWrt 官方论坛](https://forum.openwrt.org/t/xiaomi-mi-router-4a-gigabit-edition-r4ag-r4a-gigabit-fully-supported-but-requires-overwriting-spi-flash-with-programmer/36685)
- 设备支持：[OpenWrt Wiki - Xiaomi Mi Router 4A (100M)](https://openwrt.org/toh/xiaomi/mi_router_4a_mir4a_100m)

## 📄 免责声明

本项目仅供学习和技术交流使用。刷机操作可能使设备失去保修、导致变砖或数据丢失。请在充分理解风险的前提下操作，作者不对任何损失负责。
