import os
import cv2
import argparse

parser = argparse.ArgumentParser()

def read_file(det_file_path):
    # detections should be x1, y1, x2, y2, conf, cls_conf, cls_pred
    img_dict = {}
    f = open(det_file_path,'r')
    for line in f.readlines():
        # print(line)
        spt = line.strip().split(',') # 1203,-1,809.0,141.0,53.0,29.0,0.9999504,-1,-1,-1
        frame_id = spt[0]
        if not img_dict.get(frame_id):
            img_dict[frame_id]=[]
        x1,y1,x_width,y_height,conf = int(float(spt[2])),int(float(spt[3])),int(float(spt[4])),int(float(spt[5])),float(spt[6])
        img_dict[frame_id].append([x1,y1,x_width,y_height,conf,1,0])
    return img_dict # returned as [x1,y1,w,h,conf,1,0]
    
def rectangle_img(img,bbx,show_conf=False):
    for bbox in bbx:
        x1,y1,x_width,y_height,conf = bbox[0],bbox[1],bbox[2],bbox[3],bbox[4]
        cv2.rectangle(img,(x1,y1),(x1+x_width,y1+y_height),(255,255,0),2)
        # if show_conf:
        #     cv2.putText(img,'holothurian %.2f'%conf,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),1)
        # else:
        #     cv2.putText(img,'holothurian',(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),1)
    return img

drawing= False
deleting = False
x_min,y_min = 0 , 0
x_max,y_max = 0 , 0

def draw_rectangle(event,x,y,flags,param):
    global x_min,y_min,x_max,y_max,drawing,img2,deleting,img3
    # if not deleting:
    img2 = img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_min,y_min = x,y
        x_max,y_max = x,y
    elif event == cv2.EVENT_LBUTTONDBLCLK:
        deleting = True
        img3 = img2.copy()
        x_min,y_min = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            x_max,y_max = x,y
            cv2.rectangle(img2,(x_min,y_min),(x_max,y_max),(0,0,255),2)
            cv2.imshow('img',img2)
    elif event ==cv2.EVENT_LBUTTONUP:
        if drawing == True:
            x_max,y_max = x,y
            cv2.rectangle(img,(x_min,y_min),(x_max,y_max),(0,0,255),2)
            cv2.imshow('img',img)
            drawing = False
def write_txt_file(output_dir,img_dict,mode='det'):
    # img_dict is [x1,y1,w,h,conf,1,0]
    output_path = os.path.join(output_dir,mode+'.txt')
    det_list = []
    if mode == 'det':
        f = open(output_path,'w')
        for key,val in img_dict.items():
            for x1,y1,w,h,conf,cls_conf,cls_id in val:
                det_list.append([int(key),x1,y1,w,h,conf])
        det_list = sorted(det_list)
        for key,x1,y1,w,h,conf in det_list:
            tmp = [x1,y1,w,h,conf]
            line = str(key)+',-1,'+','.join([str(i) for i in tmp])+',-1,-1,-1'+'\n'
            f.writelines(line)
        f.close()

def find_bbx_to_del(np_lists,x,y):
    for i,(x1,y1,w,h,conf,a,b) in enumerate(np_lists):
        if x1 < x < x1+w and y1 < y < y1 +h:
            return i
    return None

parser.add_argument('--start_frame',default=0,type=int)
parser.add_argument('--det_file',type=str,default='det/det.txt')
parser.add_argument('--img_folder',type=str,default='img1')
args = parser.parse_args()

if __name__ == "__main__":
    img_num = len(os.listdir(args.img_folder))
    img_id = args.start_frame   
    while(img_id<img_num):
        img_dict = read_file(args.det_file)
        img_id+=1
        img_path = os.path.join(args.img_folder,str(img_id)+'.jpg')
        img = cv2.imread(img_path)
        print(img_path)
        if img_dict.get(str(img_id)):
            img = rectangle_img(img,img_dict[str(img_id)])
        else:
            img = img
        cv2.namedWindow('img',cv2.WINDOW_NORMAL)
        # cv2.namedWindow('img')
        cv2.setMouseCallback('img',draw_rectangle)
        cv2.imshow('img',img)
        key = cv2.waitKey(1) & 0XFF
        if key != ord('d') or key != ord('u') or key != ord('q'):
            while True:
                key2 = cv2.waitKey(1) & 0XFF
                cv2.imshow('img',img)
                if drawing :
                    cv2.rectangle(img2,(x_min,y_min),(x_max,y_max),(0,0,255),2)
                    cv2.imshow('img',img2)
                if deleting:
                    if img_dict.get(str(img_id)):
                        i = find_bbx_to_del(img_dict[str(img_id)],x_min,y_min)
                        if i is not None:
                            xa,ya,w,h = img_dict[str(img_id)][i][0],img_dict[str(img_id)][i][1],img_dict[str(img_id)][i][2],img_dict[str(img_id)][i][3]
                            xb,yb = xa+w,ya+h
                            cv2.rectangle(img3,(xa,ya),(xb,yb),(0,255,255),2)
                            cv2.imshow('img',img3)
                            if key2 == ord('r'):
                                img_dict[str(img_id)].pop(i)
                                deleting = False
                if key2 == ord('q'):
                    break
                if key2 == ord('s'):
                    #[x1,y1,x2,y2,conf]
                    if x_max-x_min != 0:
                        if not img_dict.get(str(img_id)):
                            img_dict[str(img_id)] = []
                        img_dict[str(img_id)].append([x_min,y_min,x_max-x_min,y_max-y_min,1,1,0])
                    write_txt_file('./det',img_dict,'det')
                    img_id -= 1
                    break
                if key2 == ord('d'):
                    deleting = False
                    break
                elif key2 == ord('u'):
                    deleting = False
                    img_id-=2
                    break
        if key2 == ord('q'):
            break