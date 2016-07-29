import os

####################################VARIABLES########################################

#The first folder in IMAGES corresponds to the first folder in ANNOTATIONS and so on
IMAGES = ['VOCdevkit/VOC2007/JPEGImages']
ANNOTATIONS = ['VOCdevkit/VOC2007/Annotations']

#####################################################################################


if __name__ == "__main__":

    txtFile = open('allImages.txt', 'w')
    #txtFilePerson = open('personImages.txt', 'w')

    i = 0
    for relImPath in IMAGES:
        imPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), relImPath)

        files = sorted(os.listdir(imPath))

        for filename in files:
            txtFile.write(filename.split('.')[0] + ' ')

            txtFile.write(relImPath + ' ')
            txtFile.write(ANNOTATIONS[i] + '\n')

            #txtFilePerson.write(filename.split('.')[0] + '  1\n')


        i = i + 1


    txtFile.close()
    #txtFilePerson.close()