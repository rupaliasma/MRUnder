import os
from glob import glob
from tqdm import tqdm
from utils.HandleDicom import FolderRead
from utils.HandleNifti import FileSave
import numpy as np
import json


root_original = r"D:\Hyperthermia_Data102\Sarkoma" #path where the DICOMs are
nitfi_root = r"D:\Hyperthermia_Data102\Sarkoma_NII" #path where NITIs will be stored, split as mag and phase
cmplx_nitfi_root = r"D:\Hyperthermia_Data102\Sarkoma_ComplexNII" #path where NITIs will be stored, combined as complex

def dcm2nii(dicom_folder, nii_path):
    data = FolderRead(dicom_folder).squeeze()
    FileSave(data, nii_path)


mags = glob(f"{root_original}/**/MAG", recursive=True)
idCounter = 0
subIDs = {}

for mag_path in tqdm(mags):
    pha_path =  mag_path.replace("MAG", "PHA")
    magvol = FolderRead(mag_path).squeeze()
    phavol = FolderRead(pha_path).squeeze()

    subName = mag_path.split(root_original)[1].split(os.path.sep)[0]
    if not subName in subIDs.keys():
        subIDs[subName] = idCounter
        idCounter += 1
    subID = subIDs[subName]

    new_mag_path = mag_path.replace(subName, str(subID))

    nii_path = new_mag_path.replace(root_original, nitfi_root)
    os.makedirs(os.path.dirname(nii_path), exist_ok=True)
    FileSave(magvol, nii_path+".nii.gz")
    FileSave(phavol, nii_path.replace("MAG", "PHA")+".nii.gz")

    complexvol = np.multiply(magvol, np.exp(1j*phavol))
    nii_path_complex = new_mag_path.replace(root_original, cmplx_nitfi_root).replace(os.path.sep+"MAG", "")
    os.makedirs(os.path.dirname(nii_path_complex), exist_ok=True)
    FileSave(magvol, nii_path_complex+".nii.gz")

with open(f"{root_original}/subIDs.json", 'w') as fp:
    json.dump(subIDs, fp)