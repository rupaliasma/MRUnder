import numpy as np
import SimpleITK as sitk

p = r"D:\Hyperthermia_Data102\Sarkoma_ComplexNII_Under\1DVarden25Mask\0\20140225\dynamic\EchoTime_4.76.npy"
data = np.load(p)

data = np.abs(data) #Magnitude
# data = np.angle(data) #Phase

data = data.transpose()
image = sitk.GetImageFromArray(data)
sitk.Show(image)
