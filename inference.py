import net
import torch
import os
import numpy as np
import cv2
from video_stream import Cv2FileVideoStream
import requests
import time
import argparse
import requests
import sqlite3
from datetime import datetime
url = "http://127.0.0.1:5000/api/recognize"

# Your API Key
# api_key = "3f9e6b48724f0d9b0c3a7d98e72a5fbc0b3d6a4ef1234567890abcdef123456"


adaface_models = {
    'ir_50':"pretrained/adaface_ir50_ms1mv2.ckpt",
}


def fetch_name_by_id(id, table_name="employee"):
    """Fetches name from the database using person_id."""
    with sqlite3.connect("cctv_database.db") as conn:
        cursor = conn.cursor()
        query = f"SELECT name FROM {table_name} WHERE uniqueid = ? LIMIT 1"
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        
        if result:
            return result[0]  # Return the name
        else:
            return None  # No matching record found

def load_pretrained_model(architecture='ir_50'):
    # load model and pretrained statedict
    assert architecture in adaface_models.keys()
    model = net.build_model(architecture)
    statedict = torch.load(adaface_models[architecture])['state_dict']
    model_statedict = {key[6:]:val for key, val in statedict.items() if key.startswith('model.')}
    model.load_state_dict(model_statedict)
    model.eval()
    return model

def to_input(pil_rgb_image):
    np_img = np.array(pil_rgb_image)
    brg_img = ((np_img[:,:,::-1] / 255.) - 0.5) / 0.5
    tensor = torch.tensor([brg_img.transpose(2,0,1)]).float().cuda()
    return tensor
with open('database.txt', 'r') as file:
    names_list = [line.strip() for line in file]




def save_to_database(name, person_id, camera_id):
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if camera_id==1:
        camera_loc="Entry"
    else:
        camera_loc="Exit"
    
    with sqlite3.connect("cctv_database.db") as conn:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO cctv (person_id, name, date_time,camera_id) VALUES (?, ?, ?,?)",
                           (person_id, name, date_time,camera_loc))

        
        conn.commit()


def main():
    # check=False
    model = load_pretrained_model('ir_50').cuda()
    feature, norm = model(torch.randn(2,3,112,112).cuda())
    #time.sleep(10)

    database_features = torch.load('database.pt')
    database_features = torch.cat(database_features).T.cuda()
                      
    vid_stream = Cv2FileVideoStream('imran.mp4')#rtsp://admin:aivstudios@12@192.168.100.105:554/streaming/channels/101
    check = {}
    H = vid_stream.height
    W = vid_stream.width

    camera_id=1

    vid_stream.start()
    while(True):
        if not vid_stream.running():
            break
        if not vid_stream.more():
            continue

        aligned_rgb_imgs,bboxes,frame = vid_stream.read()
        frame_resized = cv2.resize(frame, (frame.shape[1] // 4, frame.shape[0] // 2))

        cv2.imshow('Video', frame_resized)
        
        # cv2.imshow('Video', frame)  # Display the frame

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        name = None

        for box,aligned_rgb_img in zip(bboxes,aligned_rgb_imgs):
            h = box[3]-box[1]
            w = box[2]-box[0]
            bgr_tensor_input = to_input(aligned_rgb_img)
            feature, _ = model(bgr_tensor_input)
            similarity_scores = torch.cat([feature]) @ database_features
            out = torch.argmax(similarity_scores,dim=1)
            score = float(similarity_scores[0][int(out)])
            # print(score)
            if score>=0.4:
                id_ = int(out)
                if id_<=len(names_list):
                    personid = names_list[id_]
                    personid=personid.split('.jpg')[0]
                    name = fetch_name_by_id(personid, "employee")


                if personid:
                    
                    if personid in check.keys():
                        last_time = check[personid][1]
                        last_camera = check[personid][0]
                        if time.time()-last_time>10:
                            save_to_database(name, personid, camera_id)
                            check[personid]=[camera_id,time.time()]
                            print('Added to database after 10 sec rule is over',name,personid, camera_id)
                        else:
                            if last_camera==camera_id:
                                print('Already Dectected not saving in database')
                                pass
                            else:
                                save_to_database(name, personid, camera_id)
                                check[personid]=[camera_id,time.time()]
                                print('Added to database detected by another camera',name,personid, camera_id)
                    else:
                        save_to_database(name, personid, camera_id)
                        check[personid]=[camera_id,time.time()]
                        print('First time detected',name,personid, camera_id)


                    personid = None
        time.sleep(0.1)            # check=True
        # if check:
        #     break
        vid_stream.task_done()
    

    # Releasing the video   
    vid_stream.stop()



if __name__ == "__main__":
    main()