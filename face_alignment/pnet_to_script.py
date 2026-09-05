import numpy as np
import torch
from torch.jit import script

import os
import argparse
from mtcnn_pytorch.src.get_nets import PNet, RNet, ONet

parser = argparse.ArgumentParser(description='ArcFace PyTorch to onnx')
parser.add_argument('--output', type=str, default='PNet.pt', help='output onnx path')
args = parser.parse_args()

backbone = PNet()
# Convert the model to TorchScript
scripted_model = script(backbone)

# Save the TorchScript model to a file
scripted_model.save("pnet_scripted.pt")
#convert_pt(backbone, args.output)