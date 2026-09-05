import numpy as np
import torch
from torch.jit import script

import os
import argparse
from mtcnn_pytorch.src.get_nets import PNet, RNet, ONet

def convert_pt(net, output):
    assert isinstance(net, torch.nn.Module)
    # img = np.random.randint(0, 255, size=(48, 48, 3), dtype=np.int32)
    # img = img.astype(np.float32)
    # img = (img / 255. - 0.5) / 0.5 # torch style norm
    # img = img.transpose((2, 0, 1))
    # img = torch.from_numpy(img).unsqueeze(0).float()

    traced_script_module = torch.jit.script(net)
    traced_script_module.save(output)
import os
import argparse

parser = argparse.ArgumentParser(description='ArcFace PyTorch to onnx')
parser.add_argument('--output', type=str, default="onet.pt", help='output onnx path')
args = parser.parse_args()
backbone = ONet()
convert_pt(backbone, args.output)