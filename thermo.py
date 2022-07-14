import os
import sys
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

def get_deltaT_Spiros(I_ref, I_H, TE, B0, alpha=-0.01):
    CONSTANT=(1/(alpha*TE*B0*2*np.pi))*1000.0 
    return np.angle(I_H*np.conj(I_ref))*CONSTANT

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

def GetNSave_TempMaps_DualEcho(echoes, out_root, FieldStrength, useMethodSpiros=False, tpSplit=True, static_root="", useStatic=False):
    data = []
    TEs = []
    for echo_path in echoes:
        echo_TE = float(echo_path.split("EchoTime_")[1])
        TEs.append(echo_TE)
        dynim_H = readNPYs(echo_path)
        data.append(dynim_H)

    if useStatic:
        dynStartInd = 0
        sys.exit("Static can not be used with dual-echo temperature calculation, useStatic should be False")
    else:
        dynStartInd = 1

        dataRefTE1 = data[0][0] #First Echo of the reference (the first dynamic TP)
        dataRefTE2 = data[-1][0] #Second or Final Echo of the reference (the first dynamic TP)

        dataRef = dataRefTE2 * np.conj(dataRefTE1)
        DTE = TEs[-1] - TEs[0] #the difference of echoes

    deltaTs = []
    deltaPhis = []
    for i in range(dynStartInd, len(data[0])):
        imHTE1=data[0][i] #First Echo
        imHTE2=data[-1][i] #Second or Final Echo

        imH = imHTE2 * np.conj(imHTE1)        

        if useMethodSpiros:
            deltaT = get_deltaT_Spiros(dataRef, imH, B0=FieldStrength, TE=DTE)
        else:
            deltaPhi = get_deltaPhi(dataRef, imH)
            deltaPhis.append(deltaPhi)
            deltaT = get_deltaT(deltaPhi=deltaPhi, B0=FieldStrength, TE=DTE)
        deltaTs.append(deltaT)
    deltaTs = np.array(deltaTs).transpose(1,2,3,0)
    if not useMethodSpiros:
        deltaPhis = np.array(deltaPhis).transpose(1,2,3,0)

    # saveNIFTI(array=deltaPhis,save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts[-1]}_deltaPhi.nii.gz")
    # saveNIFTI(array=deltaTs,save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts2[-1]}_deltaT.nii.gz")
    if not useMethodSpiros:
        saveNIFTI(array=deltaPhis,save_path=f"{out_root}", filename=f"deltaPhi.nii.gz")
    saveNIFTI(array=deltaTs,save_path=f"{out_root}", filename=f"deltaT.nii.gz")

    if tpSplit:
        for tp in range(deltaPhis.shape[-1]):
            if not useStatic and tp==0:
                continue 
            # saveNIFTI(array=deltaPhis[...,tp],save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts[-1]}_TP{tp if not useStatic else tp+1}_deltaPhi.nii.gz")
            # saveNIFTI(array=deltaTs[...,tp],save_path=f"{out_root}", filename=f"{name_parts[-4]}_{name_parts[-3]}_{name_parts2[-1]}_TP{tp if not useStatic else tp+1}_deltaT.nii.gz")
            if not useMethodSpiros:
                saveNIFTI(array=deltaPhis[...,tp],save_path=f"{out_root}", filename=f"TP{tp if not useStatic else tp+1}_deltaPhi.nii.gz")
            saveNIFTI(array=deltaTs[...,tp],save_path=f"{out_root}", filename=f"TP{tp if not useStatic else tp+1}_deltaT.nii.gz")