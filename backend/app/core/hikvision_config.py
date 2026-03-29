"""
hikvision_config.py
====================
Per-camera Hikvision connection config.
Each camera has its own IP.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class HikvisionCamera:
    camera_id:  str
    label:      str
    ip:         str
    port:       int = 80
    rtsp_port:  int = 554
    username:   str = "admin"
    password:   str = "admin123"
    channel:    int = 1

    @property
    def mjpeg_url(self) -> str:
        return (
            f"http://{self.username}:{self.password}@{self.ip}:{self.port}"
            f"/ISAPI/Streaming/channels/{self.channel}01/httpPreview"
        )

    @property
    def snapshot_url(self) -> str:
        return (
            f"http://{self.username}:{self.password}@{self.ip}:{self.port}"
            f"/ISAPI/Streaming/channels/{self.channel}/picture"
        )

    @property
    def rtsp_url(self) -> str:
        return (
            f"rtsp://{self.username}:{self.password}"
            f"@{self.ip}:{self.rtsp_port}"
            f"/h264/ch{self.channel}/main/av_stream"
        )


HIKVISION_CAMERAS: Dict[str, HikvisionCamera] = {
    "MAIN_GATE":     HikvisionCamera("MAIN_GATE",     "Main Gate Entrance",         ip="192.168.1.101"),
    "ENTRY_CAM":     HikvisionCamera("ENTRY_CAM",     "Entry Camera",               ip="192.168.1.102"),
    "AB4":           HikvisionCamera("AB4",           "AB4",                        ip="192.168.1.103"),
    "MAIN_BUILDING": HikvisionCamera("MAIN_BUILDING", "Main Building",              ip="192.168.1.104"),
    "HOSTEL_AB3":    HikvisionCamera("HOSTEL_AB3",    "Hostel AB3",                 ip="192.168.1.105"),
    "AB3_GATE":      HikvisionCamera("AB3_GATE",      "AB3 Gate",                   ip="192.168.1.106"),
    "SC_DIRECTOR":   HikvisionCamera("SC_DIRECTOR",   "SC Director Bungalow",       ip="192.168.1.107"),
    "LHC_SC":        HikvisionCamera("LHC_SC",        "LHC-SC",                     ip="192.168.1.108"),
    "HOSTEL_LHC":    HikvisionCamera("HOSTEL_LHC",    "Hostel LHC",                 ip="192.168.1.109"),
    "DIRECTOR_VH":   HikvisionCamera("DIRECTOR_VH",   "Director's Bungalow VH",     ip="192.168.1.110"),
    "DIRECTOR_GATE": HikvisionCamera("DIRECTOR_GATE", "Director's Bungalow Gate",   ip="192.168.1.111"),
    "EXIT_CAM":      HikvisionCamera("EXIT_CAM",      "Exit Camera",                ip="192.168.1.112"),
}
