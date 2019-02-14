#WARNING!
#always run this before using sortImagesForTarining.py!

#CODE WILL AUTOMATICLY REMOVE ALL UNWANTED FILES (it keeps only thumb files with already fixed size)
import os
from time import sleep

unsorted_file_dir = "./data/4K Stogram/"

sub_dir = os.walk(unsorted_file_dir)
for sub_dir, j, k in sub_dir:
    if (not(sub_dir.endswith(".thumb.stogram"))):
        filelist = [f for f in os.listdir(sub_dir) if (f.endswith(".mp4") or f.endswith(".jpg"))]
        print(len(filelist), " of files will be deleted from", sub_dir, "! You have 3 seconds to cancel this action!")
        sleep(3)
        for f in filelist:
            for retry in range(100):
                try:
                    os.remove(os.path.join(sub_dir, f))
                    break
                except:
                    print("Access denied, atempt:", retry)