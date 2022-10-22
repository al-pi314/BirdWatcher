#WARNING!
#always run removeNotNeededFiles.py before using this!

#CODE WILL AUTOMATICLY SPLIT IMAGES AMONG TRAIN/TEST/VALIDATION DIRECTORIES AND APPLY FILTERS TO THEM
import os
from PIL import Image, ImageEnhance 
from transforms import RGBTransform

sorted_files_dir = "./data/4K Stogram/" #File where to check for files

sub_dir = os.walk(sorted_files_dir)
c = 0
for sub_dir, j, k in sub_dir:
    print(c)
    """
    if (c >= 3):
        break
    """
    if (sub_dir.endswith(".thumb.stogram")):
        c += 1
        (dirpath, dirnames, filenames) = next(os.walk(sub_dir))
        images = filenames
        size = len(images)

        save_image_folder = sub_dir.split("/")[-1].split("\\.")[-2]
        os.makedirs("./data/train/" + save_image_folder)
        os.makedirs("./data/test/" + save_image_folder)
        os.makedirs("./data/validation/" + save_image_folder)

        train = int(0.8 * size)
        test = train + int(0.1 * size)
        validation = test + int(0.1 * size)
        
        img_counter = 0
        for image_name in images:
            image_absolute_path = sub_dir + "/" + image_name
            
            
            num_filters = 1 #this determines how many variants of one image are supported
            for f in range(num_filters):
                edit_image = Image.open(image_absolute_path)
                edit_image = edit_image.convert('RGB')
                #different filters
                """
                if (f == 0):
                    edit_image = RGBTransform().mix_with((255, 50, 0),factor=.50).applied_to(edit_image)
                elif (f == 1):
                    enhancer = ImageEnhance.Brightness(edit_image)
                    edit_image = enhancer.enhance(0.15)
                
                if (f == 0):
                    edit_image = Image.open(image_absolute_path)
                    edit_image = edit_image.convert('LA').convert('RGB')
                else:
                    pass
                """
                
                save_image_name = "/" + str(f) + "_" + image_name

                if (img_counter < train):
                    edit_image.save("./data/train/" + save_image_folder + save_image_name)
                elif (img_counter < test):
                    edit_image.save("./data/test/" + save_image_folder + save_image_name)
                else:
                    edit_image.save("./data/validation/" + save_image_folder + save_image_name)

            img_counter += 1
        print("Done sorting folder:", save_image_folder, "-------->", img_counter, "of images sorted!")