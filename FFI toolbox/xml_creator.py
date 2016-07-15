from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
import os



def save_xml(doc, root, folder = 'saveDatXML'):

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)

    if not os.path.exists(path):
        os.makedirs(path)

    filename = root.find('filename').text.split('.')[0] + '.xml'

    print filename

    with open(os.path.join(path, filename), 'wb') as file_handle:
        doc.write(file_handle)



def create_xml(folder_name, file_name, im_size, objects):

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
    fid_n.text = 341012865

    own = SubElement(root, 'owner')
    fid_s = SubElement(own, 'flickrid')
    fid_s.text = 'Fried Camels'
    o_name = SubElement(own, 'name')
    o_name.text = 'Jinky the Fruit Bat'

    size = SubElement(root, 'size')
    width = SubElement(size, 'width')
    width.text = im_size[0]
    height = SubElement(size, 'height')
    height.text = im_size[1]
    depth = SubElement(size, 'depth')
    depth.text = im_size[2]

    seg = SubElement(root, 'segmented')
    seg.text = 0

    for elem in objects:
        obj = SubElement(root, 'object')
        name = SubElement(obj, 'name')
        name.text = obj.getName()
        pose = SubElement(obj, 'pose')
        pose.text = 'Left'
        truncated = SubElement(obj, 'truncated')
        truncated.text = 1
        diff = SubElement(obj, 'difficult')
        diff.text = 0
        bounds = SubElement(obj, 'bndbox')
        xmin = SubElement(bounds, 'xmin')
        xmin = obj.getXmin()
        ymin = SubElement(bounds, 'ymin')
        ymin = obj.getYmin()
        xmax = SubElement(bounds, 'xmax')
        xmax = obj.getXmax()
        ymax = SubElement(bounds, 'ymax')
        ymax = obj.getYmax()


    save_xml(doc, root)




if __name__ == '__main__':
    create_xml('VOC2007', '000001.jpg')