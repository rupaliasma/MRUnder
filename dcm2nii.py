import os
from glob import glob
from tqdm import tqdm
from utils.HandleDicom import FolderRead
from utils.HandleNifti import FileSave
import numpy as np
import json


root_original = r"D:\Hyperthermia_Data102\SarkomaV1" #path where the DICOMs are
nitfi_root = r"D:\Hyperthermia_Data102\SarkomaV1_NII" #path where NITIs will be stored, split as mag and phase
cmplx_im_root = r"D:\Hyperthermia_Data102\SarkomaV1_ComplexNII" #path where NITIs will be stored, combined as complex

mags = glob(f"{root_original}/**/MAG", recursive=True)
idCounter = 0
subIDs = {}

for mag_path in tqdm(mags):
    try:
        pha_path =  mag_path.replace("MAG", "PHA")
        filesMAG = os.listdir(mag_path)
        seriesIDsMAG = set([f.split("_")[0] for f in filesMAG])
        for sID in seriesIDsMAG:
            seriesFilesMAG = sorted([f for f in filesMAG if sID in f])            
            seriesFilesPHA = [f.replace(sID, f"Serie{int(f.split('Serie')[1].split('_')[0])+1:03d}") for f in seriesFilesMAG]

            seriesFilesMAG = [os.path.join(mag_path,f) for f in seriesFilesMAG]
            seriesFilesPHA = [os.path.join(pha_path,f) for f in seriesFilesPHA]

            magvol = FolderRead(dicom_names=seriesFilesMAG).squeeze()
            phavol = FolderRead(dicom_names=seriesFilesPHA).squeeze()

            subName = mag_path.split(root_original)[1].split(os.path.sep)
            if subName[0] != "":
                subName = subName[0]
            else:
                subName = subName[1]
            if not subName in subIDs.keys():
                subIDs[subName] = idCounter
                idCounter += 1
            subID = subIDs[subName]

            new_mag_path = mag_path.replace(subName, str(subID))

            nii_path = new_mag_path.replace(root_original, nitfi_root)
            os.makedirs(os.path.dirname(nii_path), exist_ok=True)
            FileSave(magvol, nii_path+"_"+sID+".nii.gz")
            FileSave(phavol, nii_path.replace("MAG", "PHA")+"_"+sID+".nii.gz")

            phavol = np.interp(phavol, (phavol.min(), phavol.max()), (-np.pi, +np.pi))
            complexvol = np.multiply(magvol, np.exp(1j*phavol))
            nii_path_complex = new_mag_path.replace(root_original, cmplx_im_root).replace(os.path.sep+"MAG", "")
            os.makedirs(nii_path_complex, exist_ok=True)

            with open(nii_path_complex+"/"+sID+".npy", 'wb') as f:
                np.save(f, complexvol)
    except Exception as ex:
        print(ex)

with open(f"{root_original}/subIDs.json", 'w') as fp:
    json.dump(subIDs, fp)