import net
import torch
import os
from face_alignment import align
import numpy as np
import cv2
import time
from tabulate import tabulate
import glob
from natsort import natsorted
from tqdm import tqdm

adaface_models = {
    'ir_50':"pretrained/adaface_ir50_ms1mv2.ckpt",
}


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
    #print(np_img.shape)
    brg_img = ((np_img[:,:,::-1] / 255.) - 0.5) / 0.5
    tensor = torch.tensor([brg_img.transpose(2,0,1)]).float()
    return tensor
    
def to_input_test(path):
    np_img = cv2.imread(path)
    np_img = cv2.resize(np_img,(112,112))
    brg_img = ((np_img / 255.) - 0.5) / 0.5
    tensor = torch.tensor([brg_img.transpose(2,0,1)]).float()
    return tensor

if __name__ == '__main__':

    model = load_pretrained_model('ir_50').cuda()
    feature, norm = model(torch.randn(2,3,112,112).cuda())
    model.eval()

    test_image_path = natsorted(glob.glob('images/*'))

    features = []
    st=time.time()
    

    f = open("database.txt", "w")
    k=0
  

    index = []
    image_name = []
    print(test_image_path)
    for img_path in tqdm(test_image_path):
        original_name = os.path.basename(img_path)
        img = cv2.imread(img_path)
        #print(path)
        aligned_rgb_img, _  = align.get_aligned_face(img)
        if aligned_rgb_img==[]:
            continue
        bgr_tensor_input = to_input(aligned_rgb_img)
        with torch.no_grad():
            feature, _ = model(bgr_tensor_input.cuda())
            image_name.append(original_name)
            features.append(feature)
            k += 1 


    et = time.time()
    delta = et-st
    print('FPS = ',len(features)/delta)
    print((image_name))
    for i in range(len(image_name)):
        f.write(image_name[i]+'\n')
    f.close()
    torch.save(features, "database.pt")