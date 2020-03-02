import os
import face_recognition
import cv2

from flask_clustering.db import get_db

class thumbnail_path_gen():
    def __init__(self, user_id, file_id, file_path):
        self.thumbnail_token = ("/home/hanchi/work/face_clustering/flask_clustering/thumbnail",
                                str(user_id)+"_"+str(file_id),
                                os.path.splitext(file_path)[1])

    def get_index_path(self, index):
        return os.path.join(self.thumbnail_token[0],
                            self.thumbnail_token[1]+"_"+str(index)+self.thumbnail_token[2])

class Face():
    def __init__(self, path, index, box, encoding):
        self.path = path
        self.index = index
        self.box = box
        self.encoding = encoding

    def get_file_name(self):
        (file,ext) = os.path.splitext(os.path.basename(self.path))
        return file+"-"+str(self.index)+ext
    
class Cluster():
    def __init__(self):
        self.faces = []
    
    def get_encoding_from_files(self):
        db = get_db()
        paths = db.execute('SELECT path FROM file').fetchall()
        for p in paths:
            img = face_recognition.load_image_file(p['path'])
            boxes = face_recognition.face_locations(img, model="cnn")

            if not boxes:
                continue
            
            encodings = face_recognition.face_encodings(img, boxes)

            faces = []
            i = 0
            for box, encoding in zip(boxes, encodings):
                face = Face(p, i, box, encoding)
                faces.append(face)
                i = i + 1

            self.faces.extend(faces)
        return len(paths)

    def cluster(self):
        clt = DBSCAN(metric="euclidean")
        clt.fit(self.face_encodings)

        label_ids = np.unique(clt.labels_)
        num_unique_faces = len(np.where(label_ids > -1)[0])

        os.system("rm -rf /home/hanchi/work/face_clustering/flask_clustering/cluster/ID*")
        for label_id in label_ids:
            dir_name = "/home/hanchi/work/face_clustering/flask_clustering/cluster/ID%d" % label_id
            os.mkdir(dir_name)

            indexes = np.where(clt.labels_ == label_id)[0]

            for i in indexes:
                box = self.faces[i].box
                path = self.faces[i].path
                img = cv2.imread(path)
                face_img = self.getFaceImage(img, box)
                cv2.imwrite(dir_name+self.faces[i].get_file_name())

    
def make_thumbnail(user_id, file_id, file_path):
    tpg = thumbnail_path_gen(user_id, file_id, file_path)
    npa = load_numpy_array(file_path)
    boxes = face_recognition.face_locations(npa, model='cnn')
    
    for i in range(len(boxes)):
        cv2.imwrite(tpg.get_index_path(i),
                    get_face_array(npa[:, :, ::-1], boxes[i]))

    db = get_db()
    for i in range(len(boxes)):
        (top, right, bottom, left) = boxes[i]
        db.execute(
            'INSERT INTO'
            ' face (user_id, file_id, face_index, top, right, bottom, left, origin_path, thumb_path)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (user_id, file_id, i, top, right, bottom, left, file_path, tpg.get_index_path(i))
        )
    db.commit()

    
def get_located_image_path(path):
    located_dir_path = "/home/hanchi/work/face_clustering/flask_clustering/located"
    thumbnail_dir_path = "/home/hanchi/work/face_clustering/flask_clustering/thumbnail"
    file_name = os.path.basename(path)
    located_path = os.path.join(located_dir_path, file_name)
    thumbnail_path = os.path.join(thumbnail_dir_path, file_name)

    npa = load_numpy_array(path)
    locas = face_recognition.face_locations(npa)
    draw_face_list_on_npa(npa, locas)
    
    cv2.imwrite(located_path, npa[:, :, ::-1])
    return located_path

def load_numpy_array(path):
    return face_recognition.load_image_file(path)

def draw_face_list_on_npa(npa, locas):
    for location in locas:
        (top, right, bottom, left) = location
        cv2.rectangle(npa, (left, top), (right, bottom), (255, 0, 0), 2)
    return npa

def get_face_array(npa, box):
    img_height, img_width = npa.shape[:2]
    (top, right, bottom, left) = box
    # (x,y)=((right+left)/2, (bottom+top)/2)
    # box_width = right - left
    # box_height = bottom - top
    # top = max(top - box_height, 0)
    # bottom = min(bottom + box_height, img_height - 1)
    # left = max(left - box_width, 0)
    # right = min(right + box_width, img_width - 1)
    return npa[top:bottom, left:right]


#get_located_image_path('/home/hanchi/work/face_clustering/IMG_5133.JPG')
# image = face_recognition.load_image_file("IMG_5133.JPG")

# cv2.imshow('origin', image[:, :, ::-1])
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# face_locations = face_recognition.face_locations(image)
# print(face_locations)
# (top, right, bottom, left) = face_locations[0]
# cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

# cv2.imshow('IMG_5133.JPG.LOCA', image[:, :, ::-1])
# cv2.waitKey(0)
# cv2.destroyAllWindows()
