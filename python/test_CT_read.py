from pyDICOS import CT, Filename, ErrorLog, Volume
import numpy as np

class CTLoader:
    def __init__(self, filename=None, ct_object=None):
        self.depth_size = 0
        self.height_size = 0
        self.width_size = 0
        self.section_size = 0
        self.data_arrays = []
        if filename is not None and ct_object is not None:
            raise ValueError("Cannot set both filename and CT object simultaneously.")
        
        if filename is not None:
            self.ct_object = CT()
            self.load_file(filename)
        
        elif ct_object is not None:
            self.ct_object = ct_object
            self.load_ct_object()

    def load_file(self, filename):
        errorlog_ = ErrorLog()
        if self.ct_object.Read(Filename(filename), errorlog_, None):
            print("Loaded CT from file")
        else:
            print("Failed to load CT from file")        
    
    def load_ct_object(self):
        print("Using provided CT object")

    def get_data(self):
        sectionIt = self.ct_object.Begin()

        sectionCount = 0
        while sectionIt != self.ct_object.End():
            pSection = sectionIt.deref()
            pixel_data_type = pSection.GetPixelDataType()

            if Volume.IMAGE_DATA_TYPE.enumUnsigned16Bit == pixel_data_type:
                volume = pSection.GetPixelData()
                self.depth_size = volume.GetDepth()
                self.height_size = volume.GetUnsigned16().GetHeight()
                self.width_size = volume.GetUnsigned16().GetWidth()

                data_array = np.zeros((self.depth_size, self.height_size, self.width_size), dtype=np.uint16)

                for i in range(volume.GetDepth()):
                    xyPlane = volume.GetUnsigned16()[i]
                    for j in range(xyPlane.GetHeight()):
                        for k in range(xyPlane.GetWidth()):
                                data_array[i, j, k] = xyPlane.Get(j, k)
                self.data_arrays.append(data_array)
            next(sectionIt)
            print(sectionCount)
            sectionCount += 1
        return self.data_arrays


def main():
    # Example 1: Load CT from a file
    filename = "SimpleCT/SimpleCT0000.dcs"
    ct_loader_file = CTLoader(filename=filename)
    ct_loader_file.get_data()
    for idx, data_array in enumerate(ct_loader_file.data_arrays):
        print(f"Section {idx + 1}:\n{data_array}")

    # Example 2: Load CT from an existing CT object
    CTObject = CT()
    errorlog_ = ErrorLog()
    if CTObject.Read(Filename("SimpleCT/SimpleCT0000.dcs"), errorlog_, None):
        ct_loader_object = CTLoader(ct_object=CTObject)
        ct_loader_object.get_data()
        for idx, data_array in enumerate(ct_loader_object.data_arrays):
            print(f"Section {idx + 1}:\n{data_array}")
    else:
        print("Failed to load CT")


if __name__ == "__main__":
    main()