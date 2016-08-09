from xml.etree.ElementTree import ElementTree, Element, SubElement
import xml.etree.ElementTree as ET
import os
from ImageObject import ImageObject

#####################################VARIABLES#########################################

#Name of the folder containing the XML files. This can be specified through arguments.
#XML_FOLDER = 'Annotations'


#######################################################################################

def save_xml(doc, root, path):

    #path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder) # Not used since this function started taking full paths

    if not os.path.exists(path):
        os.makedirs(path)

    filename = root.find('filename').text.split('.')[0] + '.xml'

    with open(os.path.join(path, filename), 'wb') as file_handle:
        doc.write(file_handle)

    print 'Saved', filename, 'successfully!'

def read_xml(imagefilename, path):

    image_name = imagefilename.split('.')[0] + '.xml'

    try:
        tree = ET.parse(os.path.join(path, image_name))
    except IOError: #No xml file found
        return None
    root = tree.getroot()
    objects = []

    for object in root.iter("object"):
        name = object.find("name").text
        bndbox = object.find("bndbox")
        xmin = int(bndbox.find("xmin").text)
        xmax = int(bndbox.find("xmax").text)
        ymin = int(bndbox.find("ymin").text)
        ymax = int(bndbox.find("ymax").text)

        final_object = ImageObject(name, xmin, ymin, xmax, ymax)
        objects.append(final_object)

    return objects


def create_xml(path, folder_name, file_name, w, h, d, objects):

    root = Element('annotation')
    doc = ElementTree(root)

    folder = SubElement(root, 'folder')
    folder.text = folder_name

    file = SubElement(root, 'filename')
    file.text = file_name

    source = SubElement(root, 'source')
    db = SubElement(source, 'database')
    db.text = 'The VOC2007 Database'
    ann = SubElement(source, 'annotation')
    ann.text = 'PASCAL VOC2007'
    im = SubElement(source, 'image')
    im.text = 'flickr'
    fid_n = SubElement(source, 'flickrid')
    fid_n.text = '341012865'

    own = SubElement(root, 'owner')
    fid_s = SubElement(own, 'flickrid')
    fid_s.text = 'Fried Camels'
    o_name = SubElement(own, 'name')
    o_name.text = 'Jinky the Fruit Bat'

    size = SubElement(root, 'size')
    width = SubElement(size, 'width')
    width.text = str(w)
    height = SubElement(size, 'height')
    height.text = str(h)
    depth = SubElement(size, 'depth')
    depth.text = str(d)

    seg = SubElement(root, 'segmented')
    seg.text = '0'

    for elem in objects:
        obj = SubElement(root, 'object')
        name = SubElement(obj, 'name')
        name.text = elem.getName()
        pose = SubElement(obj, 'pose')
        pose.text = 'Left'
        truncated = SubElement(obj, 'truncated')
        truncated.text = '1'
        diff = SubElement(obj, 'difficult')
        diff.text = '0'
        bounds = SubElement(obj, 'bndbox')
        xmin = SubElement(bounds, 'xmin')
        xmin.text = str(elem.getXmin())
        ymin = SubElement(bounds, 'ymin')
        ymin.text = str(elem.getYmin())
        xmax = SubElement(bounds, 'xmax')
        xmax.text = str(elem.getXmax())
        ymax = SubElement(bounds, 'ymax')
        ymax.text = str(elem.getYmax())

    save_xml(doc, root, path)



if __name__ == '__main__':

    obj = ImageObject('dog', 20, 30, 100, 120)
    obj2 = ImageObject('person', 50, 60, 220, 180)

    obj_list = [obj, obj2]

    create_xml('VOC2007', '000001.jpg', 1920, 1080, 3, obj_list)