#################################################
import argparse
import os
import sys
from pathlib import Path
import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from utils.general import (LOGGER, cv2, check_file, check_img_size, check_imshow, check_requirements, colorstr,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, time_sync
#####################################################


#import pi camera
from picamera2 import Picamera2
from time import time

#mavsdk stuff
import asyncio
from mavsdk import System
import sys
from mavsdk.telemetry import Telemetry 

#image transfer stuff
import socket 

GCSSocket = "172.20.10.3"
UAVSocket = "172.20.10.12"
Server = "194.195.243.227"


global picam2
global model
global counter, count
global smokeLat, smokeLon

counter = 0
picam2 = Picamera2()


weights = '/home/pi/yoloUpdated/yolov5/smoke.pt'

@torch.no_grad()

async def run(
):
    
    preview_config = picam2.still_configuration(main={"size": (800, 600)})
    picam2.configure(preview_config)
    
    counter = 0
    
    picam2.start()
     
    print('STARTTTTT')
    weights=ROOT / '/home/pi/yoloUpdated/yolov5/smoke.pt',  # model.pt path(s)
    source=ROOT / 'data/images',  # file/dir/URL/glob, 0 for webcam
    data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
    imgsz=(640, 640)  # inference size (height, width)
    conf_thres=0.25  # confidence threshold
    iou_thres=0.45  # NMS IOU threshold
    max_det=1000 # maximum detections per image
    #device='' # cuda device, i.e. 0 or 0,1,2,3 or cpu
    view_img=False  # show results
    save_txt=False  # save results to *.txt
    save_conf=False  # save confidences in --save-txt labels
    save_crop=False  # save cropped prediction boxes
    nosave=False  # do not save images/videos
    classes=1  # filter by class: --class 0, or --class 0 2 3
    agnostic_nms=False  # class-agnostic NMS
    augment=False  # augmented inference
    visualize=False  # visualize features
    update=False  # update all models
    project=ROOT / 'runs/detect',  # save results to project/name
    name='exp',  # save results to project/name
    exist_ok=False  # existing project/name ok, do not increment
    line_thickness=3  # bounding box thickness (pixels)
    hide_labels=False  # hide labels
    hide_conf=False  # hide confidences
    half=False  # use FP16 half-precision inference
    dnn=False  # use OpenCV DNN for ONNX inference

    device = 'cpu'
    device = select_device(device)

    model = DetectMultiBackend('/home/pi/yoloUpdated/yolov5/smoke.pt', device=device, dnn=False, data=ROOT / 'data/coco128.yaml', fp16=False)

    ## pre starting checkup
    """
    print("Getting ready")
    device = 'cpu'
    device = select_device(device)
    model = DetectMultiBackend('/home/pi/yoloUpdated/yolov5/smoke.pt', device=device, dnn=False, data=ROOT / 'data/coco128.yaml', fp16=False)
    preview_config = picam2.still_configuration(main={"size": (800, 600)})
    picam2.configure(preview_config)
    
    counter = 0
    
    picam2.start()
    """
    #serial port setup
    drone = System()
   # await drone.connect(system_address="serial:///dev/ttyS2:921600")
    await drone.connect(system_address="serial:///dev/serial0:57600")
    print("Waiting for drone to connect...")
        
        
        
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break
            
            
            
   
    async for flight_mode in drone.telemetry.flight_mode():
        print("FlightMode:", str(flight_mode))
        if str(flight_mode) == 'MANUAL':
            print("YEEEE HAWWWW")
            print("I feel the need...the need for speed!")
            break
            
    async for gps in drone.telemetry.position():
        
       # gps = drone.telemetry.position()       
        print(gps)
        oldCounter = counter
        data1 = picam2.capture_array()
        print('image captured')
        save_img = data1
        source = save_img
        stride, names, pt = model.stride, model.names, model.pt
        imgsz = check_img_size(imgsz, s=stride)  # check image size
        bs = 1
        model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup
        dt, seen = [0.0, 0.0, 0.0], 0
        dataset = LoadImages(save_img, img_size=imgsz, stride=stride, auto=pt)
        dataset = dataset.__next__()
        im = dataset[0]
        im0s = dataset[1]
        s = dataset[2]
        t1 = time_sync()
        im = torch.from_numpy(im).to(device)
        im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1
        
        pred = model(im, augment=augment, visualize=False)
        t3 = time_sync()
        dt[1] += t3 - t2
        
       # classes = 1
        
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        dt[2] += time_sync() - t3
        flag = 0
        for i, det in enumerate(pred):  # per image
            seen += 1
            im0= im0s.copy()

            #p = Path(p)  # to Path
            #save_path = str(save_dir / p.name)  # im.jpg
            #txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # im.txt
            #s += '%gx%g ' % im.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            imc = im0.copy() if save_crop else im0  # for save_crop
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                counter = counter + 1
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    #s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                    print("SMOOOKEEEE")
                    cv2.imwrite('/home/pi/yoloUpdated/yolov5/runs/detect/result%05d.jpeg' % (counter), im0)
                    
                
        # Print time (inference-only)
       # LOGGER.info(f'{s}Done. ({t3 - t2:.3f}s)')

        # Print results
       # t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
       # LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
        #if save_txt or save_img:
        #    s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        #    LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
        if update:
            strip_optimizer(weights)  # update model (to fix SourceChangeWarning)
        
        if (oldCounter<counter and gps.relative_altitude_m>5):
            smokeLat =str(round(gps.latitude_deg,3))
            smokeLon = str(round(gps.longitude_deg,3))
            ################################################
            ################################################

          
            print(">> Loading image")

            with open("/home/pi/yoloUpdated/yolov5/runs/detect/result%05d.jpeg" % (counter), "rb") as img:
              f = img.read()
              byte_im = bytearray(f)
              
            print(">> Image loaded")

            img_len = len(byte_im)

            print(f">> image size : {img_len} bytes")
            """
            if(len(smokeLat) == 5):
              smokeLat = '0'+smokeLat

            if(len(smokeLat) == 5):
              smokeLon = '0'+smokeLon
            print(len(smokeLat))
            print(len(smokeLon))
            """

            HEADERSIZE = 3 #bytes

            msg = img_len.to_bytes(HEADERSIZE,'little')+byte_im

            # Sending Confirmation
            sConfirm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sConfirm.connect((Server, 5555))
            #sConfirm.close()
            
            print(">> Waiting for Server ...")
            Identification = False
            while True:
                print(">> Server Communication establishing ...")
                print(f">>Fire detected at {str(gps)}")
                print(f">> Connection from {Server} has been estalished ...")
                print(f">> Sending {len(msg)-HEADERSIZE} bytes")
                if not Identification:
                    ID = str.encode("UAV")
                    sConfirm.send(ID)
                    Identification = True
                    flag = 1
                    sConfirm.send(msg)
                    break
        if flag == 1:
            break
if __name__ == "__main__":
    print("Getting ready")
        # Start the main function
   # asyncio.ensure_future(run(**vars(opt))

    # Runs the event loop until the program is canceled with e.g. CTRL-C
   # asyncio.get_event_loop().run_forever()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

            
            
        



        
            



    
