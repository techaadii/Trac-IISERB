"""
This file encodes the exact campus camera map as Directed Graph.
Single source file for the network topology

"""

from dataclasses import dataclass
from typing import List,Tuple,Dict,Set


@dataclass(frozen=True)
class Camera:
    id:str
    label:str
    is_root:bool=False
    is_terminal:bool=False
    folder_name:str=""



CAMERAS:Dict[str,Camera]={
    "MAIN_GATE":Camera(id="MAIN_GATE",label="Main Gate Entrance",is_root=True,folder_name="main_gate"),
    "ENTRY_CAM":Camera(id="ENTRY_CAM",label="Entry Camera",folder_name="entry_cam"),
    "AB4":Camera(id="AB4",label="AB4",folder_name="ab4"),
    "MAIN_BUILDING":Camera(id="MAIN_BUILDING",label="Main Building",folder_name="main_building"),
    "HOSTEL_AB3":Camera (id="HOSTEL_AB3",label="Hostel AB3",folder_name="hostel_ab3"),
    "AB3_Gate":Camera(id="AB3_GATE",label="AB3 Gate",folder_name="ab3_gate"),
    "SC_DIRECTOR":Camera(id="SC_DIRECTOR",label="SC Director Bunglow",folder_name="sc_director"),
    "LHC_SC":Camera(id="LHC_SC",label="LHC-SC",folder_name="lhc_sc"),
    "HOSTEL_LHC":Camera(id="HOSTEL_LHC",label="Hostel LHC"),
    "DIRECTOR_VH":Camera(id="DIRECTOR_VH",label="Director's Bungalow VH",folder_name="director_vh"),
    "DIRECTOR_GATE":Camera(id="DIRECTOR_GATE",label="Director's Bungalow Gate",folder_name="director_gate"),
    "EXIT_CAM":Camera(id="EXIT_CAM",label="Exit Camera",is_terminal=True,folder_name="exit_cam"),
}

ROOT_CAMERA = "MAIN_GATE"
TERMINAL_CAMERA = "EXIT_CAM"

# lets define the directed edges between the camera's as stated in the graph diagram.

