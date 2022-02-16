import os
import nibabel as nib
from skimage.transform import resize
import numpy as np
import matplotlib.pyplot as plt

def saveNIFTI(array, save_path, filename):
    array = np.transpose(array) 
    os.makedirs(save_path, exist_ok=True)
    nib.save(nib.Nifti1Image(array, np.eye(4)), os.path.join(save_path, filename))  

def get_temperature(delta_phi, B0, TE, gamma = 42.58, alpha = -0.01):
    #ϒ = 42.58 MHz/T is the gyromagnetic ratio of H1
    #α = − 0.01 ppm/°C is the PRF thermal coefficient for aqueous tissue
    #B0 is the main magnetic field strength
    #TE is the echo time of pulse sequence
    #ΔΦ is the difference between reference phase images acquired before heating at a known temperature and images acquired during heating cycle at different temperatures.
    delta_T = delta_phi / ((gamma * alpha * B0 * TE) + np.finfo(delta_phi.real.dtype).eps)
    return delta_T

def get_delta_phi(I_ref, I_H):
    delta_phi = np.arctan(((I_ref.real*I_H.imag)-(I_ref.imag*I_H.real))\
                        /((I_ref.real*I_H.real)+(I_ref.imag*I_H.imag)+np.finfo(I_ref.real.dtype).eps))
    return delta_phi

dynamic_root = r"C:\Users\HP\OneDrive\Soumick Share\Erlangen\Data\Bankel_Irmgard\20201210\dynamic\EchoTime_4.76"
static_root = r"C:\Users\HP\OneDrive\Soumick Share\Erlangen\Data\Bankel_Irmgard\20201210\driftRef\EchoTime_4.76"
FieldStrength = 1.5
TE = 4.76

im_ref, _, metaStat = readDICOM_static(static_root, return_meta=True)
dynim_H, _, metaDyn = readDICOM_dynamic(dynamic_root, return_meta=True)

t_real = resize(im_ref.real, dynim_H.shape[1:])
t_imag = resize(im_ref.imag, dynim_H.shape[1:])
im_ref = t_real + 1j* t_imag
meta = metaStat

#To use the first timepoint as reference scan, to use the base ref scan, comment it out
im_ref = dynim_H[0]
meta = metaDyn

delta_Ts = []
delta_phis = []
for i, im_H in enumerate(dynim_H):
    delta_phi = get_delta_phi(im_ref, im_H)
    delta_phis.append(delta_phi)
    delta_T = get_temperature(delta_phi=delta_phi, B0=FieldStrength, TE=TE)
    delta_Ts.append(delta_T)
delta_Ts = np.array(delta_Ts)
delta_phis = np.array(delta_phis)

saveNIFTI(array=delta_phis, save_path=dynamic_root+"/Processed", filename="phi.nii.gz")
saveNIFTI(array=delta_Ts, save_path=dynamic_root+"/Processed", filename="deltaT.nii.gz")
#sds