import os
from glob import glob
from tqdm import tqdm

root = r"D:\Hyperthermia_Data102\SarkomaV1"

folders = glob(f"{root}/*/*/dynamic/*/MAG", recursive=True)

for folder in tqdm(folders):
    folderPHA = folder.replace("MAG", "PHA")
    filesMAG = os.listdir(folder)
    filesPHA = os.listdir(folderPHA)
    filesPHAClean = []
    if len(filesMAG) != len(filesPHA):
        try:
            for fM in filesMAG:
                if "Serie" not in fM:
                    os.remove(f"{folder}/{fM}")
                sID = fM.split("Serie")[1].split("_")[0]
                sIDNext = f'{int(sID)+1:03d}'
                fM2P = fM.replace("Serie"+sID, "Serie"+sIDNext)
                if fM2P in filesPHA:
                    filesPHAClean.append(fM2P)
                else:
                    os.remove(f"{folder}/{fM}")
            for fP in filesPHA:
                if fP not in filesPHAClean:
                    os.remove(f"{folderPHA}/{fP}")
        except:
            print(folder)