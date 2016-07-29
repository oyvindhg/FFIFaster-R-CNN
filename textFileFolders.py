import os

# NB: THIS FILE HAS TO BE IN THE "DEVKIT" FOLDER

####################################VARIABLES########################################

#The first folder in IMAGES corresponds to the first folder in ANNOTATIONS and so on
IMAGES = ['VOCdevkit/VOC2007/JPEGImages']
ANNOTATIONS = ['VOCdevkit/VOC2007/Annotations']

#####################################################################################


if __name__ == "__main__":

    txtFile = open('allImages.txt', 'w')

    i = 0
    for relImPath in IMAGES:

        files = sorted(os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), relImPath)))
        annotationFiles = sorted(os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ANNOTATIONS[i])))

        j = 0
        for filename in files:

            assert (filename.split('.')[0] == annotationFiles[j].split('.')[0]), "Name in image file and annotation file not correspoding in line %d (zero based line numbering)!" % j

            txtFile.write(filename.split('.')[0] + ' ')
            txtFile.write(relImPath + ' ')
            txtFile.write(ANNOTATIONS[i] + '\n')

            j += 1

        i += 1

    txtFile.close()