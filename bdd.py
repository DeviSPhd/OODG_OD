# -*- coding: utf-8 -*-

import detectron2
from detectron2.utils.logger import setup_logger

setup_logger()

import argparse
import copy
import os
import random
import warnings

import cv2
import detectron2
# Commented out IPython magic to ensure Python compatibility.
import imageio
import imgaug as ia
import imgaug.augmenters as iaa
import matplotlib.pyplot as plt
# import some common libraries
# import some common libraries
import numpy as np
import torch
import torchvision
# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.config import get_cfg
from detectron2.data import (DatasetCatalog, DatasetMapper, MetadataCatalog,
                             build_detection_test_loader,
                             build_detection_train_loader)
from detectron2.data import detection_utils as utils
from detectron2.data import transforms as T
from detectron2.data.datasets import (register_coco_instances,load_coco_json,
                                      register_pascal_voc)
from detectron2.engine import DefaultPredictor, DefaultTrainer
from detectron2.evaluation import COCOEvaluator, inference_on_dataset
from detectron2.evaluation.coco_evaluation import COCOEvaluator
# import some common detectron2 utilities
from detectron2.model_zoo import model_zoo
from detectron2.structures import (BitMasks, Boxes, BoxMode, Keypoints,
                                   PolygonMasks, RotatedBoxes, boxes)
from detectron2.utils.logger import setup_logger
from detectron2.utils.visualizer import Visualizer
# %matplotlib inline
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from matplotlib.image import BboxImage
from PIL import Image
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from utils.utils_aug_final import *

warnings.filterwarnings("ignore")

def Solarize(img, boxs, level):  # [0, 256]  
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    solarize = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.Solarize(level, threshold=(32, 128)))
    img_aug, bb_aug= solarize(image=img, bounding_boxes=bbs)
    return img_aug

def auto_contrast(img, boxs,level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape) 
    auto_cont = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.pillike.Autocontrast(level))
    img_aug, bb_aug = auto_cont(image=img, bounding_boxes=bbs)
    return img_aug

def emboss(img, boxs,level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    emboss = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.Emboss(alpha=(0, 1.0), strength=level))
    img_aug, bb_aug = emboss(image=img, bounding_boxes=bbs)
    #return img_aug, bb_aug
    return img_aug

def Enhancecolor(img, boxs,level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    enhancecolor = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.pillike.EnhanceColor(level))
    img_aug, bb_aug = enhancecolor(image=img, bounding_boxes=bbs)
    return img_aug

def EnhanceSharpness(img, boxs, level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    enhanceSharpness = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.pillike.EnhanceSharpness(level))
    img_aug, bb_aug = enhanceSharpness(image=img, bounding_boxes=bbs)
    return img_aug

def Posterize(img, boxs, level): 
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    posterize = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.pillike.Posterize(int(level)))
    img_aug, bb_aug = posterize(image=img, bounding_boxes=bbs)
    return img_aug

def Enhancecontrast(img, boxs, level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    enhancecontrast = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.pillike.EnhanceContrast(level))
    img_aug, bb_aug = enhancecontrast(image=img, bounding_boxes=bbs)
    return img_aug

def Brightness(img, boxs, level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    brightness = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.pillike.EnhanceBrightness(level))
    img_aug, bb_aug = brightness(image=img, bounding_boxes=bbs)
    return img_aug

def AddToHue(img, boxs, level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    addtohue = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.AddToHue((-255,255)))
    img_aug, bb_aug = addtohue(image=img, bounding_boxes=bbs)
    return img_aug

def Blur(img, boxs, level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    blur = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.OneOf([iaa.GaussianBlur(sigma =(0.0, 3.0)),iaa.MedianBlur(k=(3, 7)),iaa.MotionBlur(k=15)]))
    img_aug, bb_aug = blur(image=img, bounding_boxes=bbs)
    return img_aug

def Noise(img, boxs, level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    noise = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.OneOf([iaa.imgcorruptlike.GaussianNoise(severity=2),iaa.imgcorruptlike.ImpulseNoise(severity=2),iaa.imgcorruptlike.ShotNoise(severity=2)]))
    img_aug,bbs_aug = noise(image=img, bounding_boxes=bbs)
    return img_aug

def Clouds(img, boxs, level):
    bbs=BoundingBoxesOnImage([BoundingBox(*bb)for bb in boxs],shape=img.shape)
    cloudaug = iaa.BlendAlphaBoundingBoxes(None,foreground=iaa.BlendAlphaMask(iaa.InvertMaskGen(level, iaa.VerticalLinearGradientMaskGen()),iaa.Clouds()))
    img_aug,bbs_aug = cloudaug(image=img, bounding_boxes=bbs)
    return img_aug

def fliplr(img, boxes, level):
    flip = iaa.Fliplr(level)
    img_aug = flip(image=img)
    return img_aug

def centercrop(img, boxes, level):
    crop = iaa.CenterCropToAspectRatio(level)
    img_aug = crop(image=img)
    return img_aug

ALL_TRANSFORMS = [
            (fliplr, 0.5, 1.0),
            (centercrop, 1.0, 1.5),
            (auto_contrast, 10, 20),
            (Solarize, 0.2, 1.0),       
            (emboss, 0.5, 2.0),
            (Enhancecolor, 0.5, 3.0),
            (EnhanceSharpness, 0.5, 2.0),
            (Enhancecontrast, 0.5, 1.5),  
            (Posterize, 1, 4),
            (Brightness, 0.5, 1.5), 
            (AddToHue, -255.0, 255.0),
            (Blur, 0, 15),
            (Noise, 1, 2),
            (Clouds,0.5, 1.0)
                    ]

class RandAugment:
  
      def __call__(self, image, boxes):
        ops_all = random.choices(ALL_TRANSFORMS, k=1)
        #print(ops_all)
               
        for ops in ops_all:
          #print(type(image))
          op= ops[0]
          minval = ops[1]
          maxval=ops[2]
          
          level =np.random.uniform(minval,maxval,1)[0]

          #print(op,minval,maxval,level)
          img = op(image, boxes,level)
                  
        return img
class InterAug:
   
    def __call__(self, img, boxs):
        #return_dict={}        
        augch = np.random.choice(ALL_boxchoices)
        #print(augch)
        #return_dict['augch']=augch
        bbs = BoundingBoxesOnImage(
            [
                BoundingBox(*bb)
                for bb in boxs
                
            ],
            img.shape
        )
        if augch == 'RandAugment1':
           aug = RandAugment()
           aug_image = aug(img, boxs)

        elif augch == 'boxunion': 
           if len(bbs)>1:
              #print("length")
              #print(len(bbs))
              bb1= np.random.choice(bbs.bounding_boxes)
              #ia.imshow(bb1.draw_on_image(img,size=2))
              bb2= np.random.choice(bbs.bounding_boxes)
              #ia.imshow(bb2.draw_on_image(img,size=2))
              if bb1 == bb2:
                 bb2= np.random.choice(bbs.bounding_boxes)
              bb_union = bb1.union(bb2)
              #ia.imshow(bb_union.draw_on_image(img,size=2))
              bb_union = conarray(bb_union)
              aug = RandAugment()
              #print("aug=",aug)
              aug_image = aug(img,bb_union)
           else:
              #print("box length is 1")
              aug = RandAugment()
              #print(aug)
              aug_image = aug(img,boxs) 
         
        elif augch == 'remove1box1':
           if len(bbs)>1:
              #print("length")
              #print(len(bbs))
              bb1= np.random.choice(bbs.bounding_boxes)
              #ia.imshow(bb1.draw_on_image(img,size=2))
              bb2= np.random.choice(bbs.bounding_boxes)
              #ia.imshow(bb2.draw_on_image(img,size=2))
              if bb1 == bb2:
                 bb2= np.random.choice(bbs.bounding_boxes)
              bb_union = bb1.union(bb2)
              #ia.imshow(bb_union.draw_on_image(img,size=2))
              boxchoice = ['bb_remb1', 'bb_remb2']
              op = np.random.choice(boxchoice)
              #print(op)
              if op == 'bb_remb1':
                 bb_remb,bb_remb1,bb_remb2= remove1box(bb_union,bb1)
           
              else:
                 bb_remb,bb_remb1,bb_remb2 = remove1box(bb_union,bb2)
           
              bb_remb = contextarea(bb_remb, bb_remb1, bb_remb2)
              #print(bb_remb)
              aug = RandAugment()
              #print("aug=",aug)
              aug_image = aug(img,bb_remb)
                            
           else:
              #print("box length is 1")
              aug = RandAugment()
              #print(aug)
              aug_image = aug(img,boxs)                   
        else:
           if len(bbs)>1:
              bb1= np.random.choice(bbs.bounding_boxes)
              #ia.imshow(bb1.draw_on_image(img,size=2))
              bb2= np.random.choice(bbs.bounding_boxes)
              #ia.imshow(bb2.draw_on_image(img,size=2))
              if bb1 == bb2:
                 bb2= np.random.choice(bbs.bounding_boxes)
              bb_union = bb1.union(bb2)
             # ia.imshow(bb_union.draw_on_image(img,size=2))
              bb_remb,bb_remb1,bb_remb2 = remove2box(bb_union, bb1,bb2)
           
              bb_remb = contextarea(bb_remb, bb_remb1, bb_remb2)
                #print(bb_remb)
              aug = RandAugment()
              aug_image = aug(img,bb_remb)  
           else:
              #print("box length is 1 when remove2box")
              aug = RandAugment()
              #print(aug)
              aug_image = aug(img,boxs)   
             
        return aug_image

ALL_boxchoices = ['boxunion', 'remove1box1', 'remove2box2']

def custom_mapper(dataset_dicts):
    dataset_dict = copy.deepcopy(dataset_dicts)  # it will be modified by code below # can use other ways to read image
    image = utils.read_image(dataset_dict["file_name"], format="BGR")
    utils.check_image_size(dataset_dict, image)
    
    pre_annos = dataset_dict.get("annotations", None)
    if pre_annos:
      boxes = [
                BoxMode.convert(x["bbox"], x["bbox_mode"], BoxMode.XYXY_ABS)
                if len(x["bbox"]) == 4
                else x["bbox"]
                for x in pre_annos
            ]
            
    aug = InterAug()
    image = aug(image, boxes)
    dataset_dict["image"] = torch.as_tensor(np.ascontiguousarray(image.transpose(2, 0, 1)))
    category_id2 = np.arange(len(dataset_dict["annotations"]))
    annos = []
    for i, j in enumerate(category_id2):
        d = pre_annos[j]
        d["bbox"] = boxes[i]
        d["bbox_mode"] = BoxMode.XYXY_ABS
        annos.append(d)
    dataset_dict.pop("annotations", None)  # Remove unnecessary field. 
    instances = utils.annotations_to_instances(annos, image.shape[:2])
    dataset_dict["instances"] = utils.filter_empty_instances(instances)
    #return dataset_dict
    return {
       # create the format that the model expects
       "image": dataset_dict["image"],
       "instances": dataset_dict["instances"],
       "width": image.shape[0],
       "height":image.shape[1]
   }



class AugTrainer(DefaultTrainer):
    @classmethod
    def build_train_loader(cls, cfg):
        return build_detection_train_loader(cfg, mapper=custom_mapper)
    @classmethod
    def build_evaluator(cls, cfg, dataset_name, output_folder=None):

        if output_folder is None:
            os.makedirs("coco_eval", exist_ok=True)
            output_folder = "coco_eval"

        return COCOEvaluator(dataset_name, cfg, False, output_folder)





if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--dataset',type=str,default='BDD')
    parser.add_argument('--OUTPUT_DIR',type=str, default="/obj_detection/checkpoints/BDD/fixed_10_epochs/")
    parser.add_argument('--model',type=str, choices=['faster_rcnn','retinanet'],default='faster_rcnn')
    parser.add_argument('--seed',type=str,default='1')
    parser.add_argument('--percent',type=float,default=0.1)
   
    args = parser.parse_args()
    print(args)
    
    string = '_seed_'+str(args.seed)+'_per_'+str(args.percent)
    if args.dataset == 'BDD':
        
        train_json_file=os.path.join("/BDD/annotations/bdd_splits","train2017"+string+'.json')

        train_imgs_dir = "/BDD/bdd100k/images/100k/train"
        val_json_file= "/BDD/annotations/label/val.json"
        val_imgs_dir =  "/BDD/bdd100k/images/100k/val"

    else:

        
        
        train_json_file=os.path.join("/home/object_detection/utils/synthetic_splits_train","train2017"+string+'.json')
        train_imgs_dir = "/home/object_detection/DATA/synthetic_fruit/train"
        val_json_file= "/home/object_detection/DATA/synthetic_fruit/annotations/validation_annotations.coco.json"
        val_imgs_dir= "/home/object_detection/DATA/synthetic_fruit/valid"
    seed = int(args.seed)
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)

    register_coco_instances("trainset", {}, train_json_file, train_imgs_dir)


    register_coco_instances("valset", {}, val_json_file,val_imgs_dir)

   
    training_dict = load_coco_json(train_json_file, train_imgs_dir,
                dataset_name="trainset")
    training_metadata = MetadataCatalog.get("trainset")
    len_training_images = len(training_dict)
    number_of_epochs = 10
    
    cfg = get_cfg()
    model_file = "COCO-Detection/"+args.model+"_R_50_FPN_3x.yaml"
    cfg.merge_from_file(model_zoo.get_config_file(model_file))
 
    cfg.DATASETS.TRAIN = ("trainset", )
    cfg.DATASETS.TEST = ("valset",)
    cfg.DATALOADER.NUM_WORKERS =4
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(model_file)
    cfg.SOLVER.IMS_PER_BATCH = 8
    cfg.SOLVER.BASE_LR = 0.0001
    cfg.SOLVER.WARMUP_ITERS = 500
    max_iterations = int( len_training_images*number_of_epochs/cfg.SOLVER.IMS_PER_BATCH)
    cfg.SOLVER.MAX_ITER = max_iterations   #adjust up if val mAP is still rising, adjust down if overfit
    cfg.SOLVER.STEPS =(int(max_iterations*0.4),int(max_iterations*0.7),int(max_iterations*0.9))
    cfg.SOLVER.GAMMA = 0.5
    cfg.SOLVER.CHECKPOINT_PERIOD = int(len_training_images/cfg.SOLVER.IMS_PER_BATCH)
    if 'faster' in args.model:
        cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE =512
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(training_metadata.thing_classes) 
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5     
    else:
        cfg.MODEL.RETINANET.NUM_CLASSES =len(training_metadata.thing_classes)
        cfg.MODEL.RETINANET.SCORE_THRESH_TEST = 0.5
    print(cfg)
    num_gpu = 1
    bs = (num_gpu * 2)
    cfg.num_gpus=num_gpu
 # pick a good LR
    cfg.TEST.EVAL_PERIOD = int(len_training_images/cfg.SOLVER.IMS_PER_BATCH)
    cfg.OUTPUT_DIR=os.path.join(args.OUTPUT_DIR,args.model,'relaaug',str(args.seed), str(args.percent)+"percent/")
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    trainer = AugTrainer(cfg)
    trainer.resume_or_load(resume= False)
    
    trainer.train()


    cfg.DATASETS.TEST = ("valset",)
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
    predictor = DefaultPredictor(cfg)
    evaluator = COCOEvaluator("valset", cfg, False, output_dir=cfg.OUTPUT_DIR,use_fast_impl=False)
    DetectionCheckpointer(trainer.model).load(cfg.MODEL.WEIGHTS)
    val_loader = build_detection_test_loader(cfg, "valset")
    foo= inference_on_dataset(trainer.model, val_loader, evaluator)
    print(foo)

   
