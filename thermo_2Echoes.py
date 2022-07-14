import os
import numpy as np
from skimage.transform import resize

from file_handler import readNPYs, saveNIFTI


def get_deltaPhi(I_ref, I_H):
    deltaPhi = np.arctan(((I_ref.real*I_H.imag)-(I_ref.imag*I_H.real))\
                        /((I_ref.real*I_H.real)+(I_ref.imag*I_H.imag)+np.finfo(I_ref.real.dtype).eps))
    return deltaPhi

def get_deltaT(deltaPhi, B0, TE, gamma = 42.58, alpha = -0.01):
    #ϒ = 42.58 MHz/T is the gyromagnetic ratio of H1
    #α = − 0.01 ppm/°C is the PRF thermal coefficient for aqueous tissue
    #B0 is the main magnetic field strength
    #TE is the echo time of pulse sequence
    #ΔΦ is the difference between reference phase images acquired before heating at a known temperature and images acquired during heating cycle at different temperatures.
    deltaT = deltaPhi / ((gamma * alpha * B0 * TE) + np.finfo(deltaPhi.real.dtype).eps)
    return deltaT

def get_deltaT_2TE(deltaPhi_TE1, deltaPhi_TE2, B0, TE1, TE2, gamma = 42.58, alpha = -0.01):
    #ϒ = 42.58 MHz/T is the gyromagnetic ratio of H1
    #α = − 0.01 ppm/°C is the PRF thermal coefficient for aqueous tissue
    #B0 is the main magnetic field strength
    #TE is the echo time of pulse sequence
    #ΔΦ is the difference between reference phase images acquired before heating at a known temperature and images acquired during heating cycle at different temperatures.
    n = (deltaPhi_TE2 - deltaPhi_TE1)
    deltaT = deltaPhi / ((gamma * alpha * B0 * TE) + np.finfo(deltaPhi.real.dtype).eps)
    return deltaT

def GetNSave_TempMaps_SingleEcho(dynamic_root, out_root, FieldStrength, tpSplit=True, static_root="", useStatic=False):
    TE = float(dynamic_root.split("EchoTime_")[1])

    # name_parts = dynamic_root.split(os.path.sep)
    # name_parts2 = static_root.split(os.path.sep)

    dynim_H = readNPYs(dynamic_root)

    if useStatic:
        im_ref = readNPYs(static_root)
        t_real = resize(im_ref.real, dynim_H.shape[1:])
        t_imag = resize(im_ref.imag, dynim_H.shape[1:])
        im_ref = t_real + 1j* t_imag
    #meta = metaStat

    #To use the first timepoint as reference scan, to use the base ref scan, comment it out
    if not useStatic:
        im_ref = dynim_H[0]
    #meta = metaDyn

    deltaTs = []
    deltaPhis = []
    for i, im_H in enumerate(dynim_H):
        deltaPhi = get_deltaPhi(im_ref, im_H)
        deltaPhis.append(deltaPhi)
        deltaT = get_deltaT(deltaPhi=deltaPhi, B0=FieldStrength, TE=TE)
        deltaTs.append(deltaT)
    deltaTs = np.array(deltaTs).transpose(1,2,3,0)
    deltaPhis = np.array(deltaPhis).transpose(1,2,3,0)

    # saveNIFTI(array=deltaPhis,save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts[-1]}_deltaPhi.nii.gz")
    # saveNIFTI(array=deltaTs,save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts2[-1]}_deltaT.nii.gz")
    saveNIFTI(array=deltaPhis,save_path=f"{out_root}", filename=f"deltaPhi.nii.gz")
    saveNIFTI(array=deltaTs,save_path=f"{out_root}", filename=f"deltaT.nii.gz")

    if tpSplit:
        for tp in range(deltaPhis.shape[-1]):
            if not useStatic and tp==0:
                continue 
            # saveNIFTI(array=deltaPhis[...,tp],save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts[-1]}_TP{tp if not useStatic else tp+1}_deltaPhi.nii.gz")
            # saveNIFTI(array=deltaTs[...,tp],save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts2[-1]}_TP{tp if not useStatic else tp+1}_deltaT.nii.gz")
            saveNIFTI(array=deltaPhis[...,tp],save_path=f"{out_root}", filename=f"TP{tp if not useStatic else tp+1}_deltaPhi.nii.gz")
            saveNIFTI(array=deltaTs[...,tp],save_path=f"{out_root}", filename=f"TP{tp if not useStatic else tp+1}_deltaT.nii.gz")
