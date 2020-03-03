import os
import face_recognition
import cv2
import datetime

from flask import (
    g
)

from . import file
from flask_clustering.db import get_db

class thumbnail_path_gen():
    def __init__(self, user_id, file_id, file_path):
        self.thumbnail_token = ("/home/hanchi/work/face_clustering/flask_clustering/thumbnail",
                           str(user_id)+"_"+str(file_id),
                           os.path.splitext(file_path)[1])

    def get_index_path(self, index):
        return os.path.join(self.thumbnail_token[0],
                            self.thumbnail_token[1]+"_"+str(index)+self.thumbnail_token[2])

def bulk_thumbnail(db=None):
    files = file.get_files_in_level(0)
    if not db:
        db = get_db()

    fcount = 0
    last_commit_time = datetime.datetime.now()
    for f in files:
        tpg = thumbnail_path_gen(g.user['id'], f['id'], f['path'])
        npa = load_numpy_array(f['path'])
        boxes = face_recognition.face_locations(npa)
        for i in range(len(boxes)):
            cv2.imwrite(tpg.get_index_path(i),
                        get_face_array(npa[:, :, ::-1], boxes[i]))
            (top, right, bottom, left) = boxes[i]
            db.execute(
                'INSERT INTO'
                ' face (user_id, file_id, face_index, top, right, bottom, left, origin_path, thumb_path)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (g.user['id'], f['id'], i, top, right, bottom, left, f['path'], tpg.get_index_path(i))
            )

        check_level = 1
        if len(boxes) > 0:
            check_level = 2

        db.execute(
            'UPDATE file SET check_level = ?'
            ' WHERE id = ?',
            (check_level, f['id'])
        )

        if (datetime.datetime.now() - last_commit_time).total_seconds() > 10:
            last_commit_time = datetime.datetime.now()
            db.commit()
        fcount += 1

    db.commit()

    
def bulk_thumbnail_query(db=None):
    files = file.get_files_in_level(0)
    if not db:
        db = get_db()
    
    for f in files:
        tpg = thumbnail_path_gen(g.user['id'], f['id'], f['path'])
        npa = load_numpy_array(f['path'])
        boxes = face_recognition.face_locations(npa)
        for i in range(len(boxes)):
            (top, right, bottom, left) = boxes[i]
            db.execute(
                'INSERT INTO'
                ' face (user_id, file_id, face_index, top, right, bottom, left, origin_path, thumb_path)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (g.user['id'], f['id'], i, top, right, bottom, left, f['path'], tpg.get_index_path(i))
            )

    db.commit()

def bulk_thumbnail_image(db=None):
    files = file.get_files_in_level(0)

    for f in files:
        tpg = thumbnail_path_gen(g.user['id'], f['id'], f['path'])
        npa = load_numpy_array(f['path'])
        boxes = face_recognition.face_locations(npa)
        for i in range(len(boxes)):
            cv2.imwrite(tpg.get_index_path(i),
                        get_face_array(npa[:, :, ::-1], boxes[i]))
    
def make_thumbnail(user_id, file_id, file_path):
    tpg = thumbnail_path_gen(user_id, file_id, file_path)
    npa = load_numpy_array(file_path)
    boxes = face_recognition.face_locations(npa)
    
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
