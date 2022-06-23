import os
from glob import glob
import nibabel as nib
from skimage.transform import resize
import numpy as np
import matplotlib.pyplot as plt
from file_handler import readNPYs
from pathlib import Path
from thermo import GetNSave_TempMaps_DualEcho, GetNSave_TempMaps_SingleEcho
from tqdm import tqdm

from utils import echoSort

root_input = r"D:\Hyperthermia_Data102\Reconstruction\SarkomaV1_ComplexNII_Under\SarkomaV1_ComplexNII_Under\1DVarden25Mask" #path where the complex images are - fully
# root_input = r"D:\Hyperthermia_Data102\Reconstruction\SarkomaV1_ComplexNII_Under\SarkomaV1_ComplexNII_Under\1DVarden25Mask" #path where the complex images are - undersampled image

root_output = r"S:\Biologie\AG Gaipl\Rupali\Work\Result\Reconstruction\TempMaps\DualTEs\SarkomaV1_ComplexNII_Under\1DVarden25Mask"

dualEcho = True
useMethodSpiros = False #only for dual-echo

FieldStrength = 1.5

for dynamic_path in tqdm(glob(root_input + '/**/dynamic', recursive=True)):
    try:
        echoes = echoSort(glob(dynamic_path + '/EchoTime_*'))
        echoes = [echoes[0], echoes[-1]] #just the lowest TW (for conductivity) and the highest TW (for temp)

        try:            
            if not dualEcho:
                for eh in echoes:
                    out_echo = eh.replace(root_input, root_output)
                    os.makedirs(out_echo, exist_ok=True)
                    GetNSave_TempMaps_SingleEcho(eh, out_echo, FieldStrength) 
            else:
                out_path = dynamic_path.replace(root_input, root_output)
                os.makedirs(out_path, exist_ok=True)
                GetNSave_TempMaps_DualEcho(echoes, out_path, FieldStrength, useMethodSpiros)
        except:
            print(f"Fucked-up data: {dynamic_path}")
    except:
        print(f"Fucked-up folder (Echo times data not found): {dynamic_path}")