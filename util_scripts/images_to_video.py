import cv2
import os
import imageio
import numpy as np

# data_folder_test = "../exp_owlii_benchmark/dysdf/basketball/tnerfResFields1234567/save/it400000-test_coarse"
data_folder = "/home/kaixi/Git/ResFields/DATA_ROOT/Owlii/basketball"
cam_folder = "cam_train_8"
image_folder = os.path.join(data_folder, cam_folder, "rgb")
mask_folder = os.path.join(data_folder, cam_folder, "mask")

print(image_folder)

images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
masks = [mask for mask in os.listdir(mask_folder) if mask.endswith(".png")]
img_indices = [int(img.split("/")[-1].split(".")[0]) for img in images]
mask_indices = [int(mask.split("/")[-1].split(".")[0]) for mask in masks]


sorted_images = [img for _, img in sorted(zip(img_indices, images))]
sorted_masks = [mask for _, mask in sorted(zip(mask_indices, masks))]


# frame = cv2.imread(os.path.join(data_folder, sorted_images[0]))
# height, width, layers = frame.shape

# video_save_path = os.path.join(data_folder, cam_folder, cam_folder + ".mp4")
# gif_save_path = os.path.join(data_folder, cam_folder, cam_folder + ".gif")
# video = cv2.VideoWriter(video_save_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (width,height))

# gif_save_path = os.path.join(data_folder_test, "result.gif")


image_lst = []
for i in range(len(sorted_images)):
    img = cv2.imread(os.path.join(image_folder, sorted_images[i]))
    mask = cv2.imread(os.path.join(mask_folder, sorted_masks[i]))
    masked_img = np.zeros(img.shape, dtype=np.uint8)
    masked_img.fill(255)
    masked_img[mask > 0] = img[mask > 0]
    # image_lst.append(masked_img)
    filename = os.path.join("/home/kaixi/Projects/Mixed_Reality/Resfields_Ouput/cam_train/basketball/cam_8", f"{i:03}.png")
    cv2.imwrite(filename, masked_img) 
    
    # frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # image_lst.append(frame_rgb)
    
    # video.write(masked_img)
    
# imageio.mimsave(gif_save_path, image_lst, loop=0, fps=30)

# cv2.destroyAllWindows()
# video.release()