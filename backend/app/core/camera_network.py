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
    "AB3_GATE":Camera(id="AB3_GATE",label="AB3 Gate",folder_name="ab3_gate"),
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

EDGES:list[Tuple[str,str]]=[
    ("MAIN_GATE",     "ENTRY_CAM"),
    ("ENTRY_CAM",     "AB4"),
    ("ENTRY_CAM",     "MAIN_BUILDING"),
    ("ENTRY_CAM",     "DIRECTOR_VH"),
    ("ENTRY_CAM",     "DIRECTOR_GATE"),
    ("AB4",           "ENTRY_CAM"),
    ("AB4",           "MAIN_BUILDING"),
    ("MAIN_BUILDING", "AB4"),
    ("AB4",           "HOSTEl_AB3"),
    ("AB4",           "AB3_GATE"),
    ("AB4",           "LHC_SC"),
    ("AB4",           "EXIT_CAM"),
    ("MAIN_BUILDING", "SC_DIRECTOR"),
    ("MAIN_BUILDING", "HOSTEL_AB3"),
    ("MAIN_BUILDING", 'LHC_SC'),
    ("SC_DIRECTOR",   "LHC_SC"),
    ("HOSTEL_AB3",    "AB3_GATE"),
    ("HOSTEL_AB3",    "EXIT_CAM"),
    ("AB3_GATE",      "EXIT_CAM"),
    ("LHC_SC",        "HOSTEL_LHC"),
    ("LHC_SC",        "EXIT_CAM"),
    ("HOSTEL_LHC",    "AB3_GATE"),
    ("HOSTEL_LHC",    "EXIT_CAM"),
    ("DIRECTOR_VH",   "DIRECTOR_GATE"),
    ("DIRECTOR_GATE", "EXIT_CAM"),

]

def build_adjacency()-> Dict[str,Set[str]]:
    adj: Dict[str,Set[str]]={c: set() for c in CAMERAS}

    for src,dst in EDGES:
        adj[src].add(dst)

    return adj

def get_neighbours(camera_id:str)->list[str]:
    return sorted(build_adjacency().get(camera_id,set()))

def bfs_order(start:str= ROOT_CAMERA)->List[str]:
    visited,queue,seen=[],[start],{start}
    adj=build_adjacency()

    while queue:
        node=queue.pop(0)
        visited.append(node)
        for nb in sorted(adj.get(node,[])):
            if nb not in seen:
                seen.add(nb)
                queue.append(nb)

    return visited
    


ADJACENCY=build_adjacency()
print(ADJACENCY)
print("-"*50)
print(bfs_order())