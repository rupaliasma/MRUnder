import SimpleITK as sitk
import os
import numpy as np
import nibabel as nib

def readDICOM_dynamic(root, return_meta=False):
    meta_obtained = False
    #magnitude
    reader = sitk.ImageSeriesReader() #reader object
    series_ids = reader.GetGDCMSeriesIDs(os.path.join(root, "MAG")) #get dicom filenames
    mag_img = []
    for ID in series_ids:
        reader = sitk.ImageSeriesReader() #reader object
        dicom_names = reader.GetGDCMSeriesFileNames(os.path.join(root, "MAG"), ID) #get dicom filenames
        reader.SetFileNames(dicom_names) #add filenames to the reader
        if return_meta and not meta_obtained:
            reader.MetaDataDictionaryArrayUpdateOn()
            reader.LoadPrivateTagsOn()
        image = reader.Execute() #read
        mag_img.append(sitk.GetArrayFromImage(image).astype(np.float64)) #convert the image, which is now SimpleITK image, to numpy array
        if return_meta and not meta_obtained:
            meta = {
                #from DICOM tags: https://www.dicomlibrary.com/dicom/dicom-tags/
                "TE": float(reader.GetMetaData(0, "0018|0081")),
                "FieldStrength": float(reader.GetMetaData(0, "0018|0087"))
            }
            meta_obtained = True
    mag_img = np.array(mag_img)
        
    #phase
    reader = sitk.ImageSeriesReader() #reader object
    series_ids = reader.GetGDCMSeriesIDs(os.path.join(root, "PHA")) #get dicom filenames
    ph_img = []
    for ID in series_ids:
        reader = sitk.ImageSeriesReader() #reader object
        dicom_names = reader.GetGDCMSeriesFileNames(os.path.join(root, "PHA"), ID) #get dicom filenames
        reader.SetFileNames(dicom_names) #add filenames to the reader
        image = reader.Execute() #read
        tmp = sitk.GetArrayFromImage(image).astype(np.float64) #convert the image, which is now SimpleITK image, to numpy array
        ph_img.append(np.interp(tmp, (tmp.min(), tmp.max()), (-np.pi, +np.pi)))
    ph_img = np.array(ph_img)

    #Complex number z = x + jy, where x is the real part and y is the imaginary part
    #Magnitude: mag=abs(z), Phase: ph=angle(z)
    #Complex number from mag and phase: mag * e (jph)
    complex_image = mag_img * np.exp(1j*ph_img)
    ksp = np.fft.ifftshift(np.fft.fft2(np.fft.fftshift(complex_image, axes=(-2,-1)), axes=(-2,-1)), axes=(-2,-1))

    if return_meta:
        return complex_image, ksp, meta
    else:
        return complex_image, ksp

def readDICOM_static(root, return_meta=False):    
    #magnitude
    reader = sitk.ImageSeriesReader() #reader object
    dicom_names = reader.GetGDCMSeriesFileNames(os.path.join(root, "MAG")) #get dicom filenames
    reader.SetFileNames(dicom_names) #add filenames to the reader
    if return_meta:
        reader.MetaDataDictionaryArrayUpdateOn()
        reader.LoadPrivateTagsOn()
    image = reader.Execute() #read
    mag_img = sitk.GetArrayFromImage(image).astype(np.float64) #convert the image, which is now SimpleITK image, to numpy array
    if return_meta:
        meta = {
            #from DICOM tags: https://www.dicomlibrary.com/dicom/dicom-tags/
            "TE": float(reader.GetMetaData(0, "0018|0081")),
            "FieldStrength": float(reader.GetMetaData(0, "0018|0087"))
        }

    #phase
    reader = sitk.ImageSeriesReader() #reader object
    dicom_names = reader.GetGDCMSeriesFileNames(os.path.join(root, "PHA")) #get dicom filenames
    reader.SetFileNames(dicom_names) #add filenames to the reader
    image = reader.Execute() #read
    ph_img = sitk.GetArrayFromImage(image).astype(np.float64) #convert the image, which is now SimpleITK image, to numpy array
    ph_img = np.interp(ph_img, (ph_img.min(), ph_img.max()), (-np.pi, +np.pi))

    #Complex number z = x + jy, where x is the real part and y is the imaginary part
    #Magnitude: mag=abs(z), Phase: ph=angle(z)
    #Complex number from mag and phase: mag * e (jph)
    complex_image = mag_img * np.exp(1j*ph_img)

    #get the centred kspace
    ksp = np.fft.ifftshift(np.fft.fft2(np.fft.fftshift(complex_image, axes=(-2,-1)), axes=(-2,-1)), axes=(-2,-1))
    #scaner actually provides/acquires this ksp

    if return_meta:
        return complex_image, ksp, meta
    else:
        return complex_image, ksp

def saveNIFTI(array, save_path, filename):
    array = np.transpose(array) 
    os.makedirs(save_path, exist_ok=True)
    nib.save(nib.Nifti1Image(array, np.eye(4)), os.path.join(save_path, filename))  