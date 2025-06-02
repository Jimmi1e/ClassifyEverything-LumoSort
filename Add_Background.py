from PIL import Image, ImageFilter, ImageDraw,ExifTags,ImageFont, ImageOps
from collections import defaultdict
from fractions import Fraction
from datetime import datetime, timezone, timedelta
import re
import os
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
import time
import math
from pathlib import Path
os.environ['OMP_NUM_THREADS'] = '10'
def parse_iso8601(date_str):
    try:
        return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    except ValueError:
        pass
    iso_regex = re.compile(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)?(Z|[+-]\d{2}:\d{2})?$')
    match = iso_regex.match(date_str)
    
    if match:
        year, month, day, hour, minute, second, fraction, tz_info = match.groups()
        fraction = fraction or '0'
        fraction = int(fraction)
        new_date_str = f"{year}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}.{fraction:03}"
        if tz_info:
            new_date_str += tz_info
        
        return datetime.fromisoformat(new_date_str).replace(tzinfo=timezone.utc if tz_info is None else None)
    
    raise ValueError("Invalid ISO 8601 format")
def get_dominant_color(image):
    small_image = image.resize((50, 50))
    pixels = small_image.getdata()
    most_common_color = Counter(pixels).most_common(1)[0][0]
    return most_common_color
def get_main_colors(image, num_colors=3):
    image = image.resize((50, 50))
    pixels = np.array(image)
    colors = pixels.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors,n_init=10)
    kmeans.fit(colors)
    main_colors = kmeans.cluster_centers_.astype(int)
    main_colors = [tuple(color) for color in main_colors]
    return main_colors
def add_wite_border(image,width,height,new_width,new_height):
    dominant_color = (255, 255, 255)
    new_image = Image.new("RGB", (new_width, new_height),dominant_color)
    offset = ((new_width - width) // 2, (new_height - height) // 2)
    new_image.paste(image, offset)
    return new_image
def add_blured_background(image,width,height, corner_radius=120, shadow_offset=(60, 60), shadow_blur=15):

    blurred_image = image.filter(ImageFilter.GaussianBlur(40))
    new_image = blurred_image.resize((int(width * 2), int(height * 2)))
    temp_width, temp_height = new_image.size

    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), image.size], corner_radius, fill=255
    )
    rounded_image = ImageOps.fit(image, image.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)

    shadow = Image.new("RGBA", (image.width + shadow_offset[0], image.height + shadow_offset[1]), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [(shadow_blur, shadow_blur), (image.width, image.height)],
        corner_radius,
        fill=(0, 0, 0, 180)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))


    offset = ((temp_width - width) // 2, (temp_height - height) // 2)
    new_image.paste(shadow, (offset[0] + shadow_offset[0] // 2, offset[1] + shadow_offset[1] // 2), shadow)
    new_image.paste(rounded_image, offset, rounded_image)
    return new_image
def add_dominant_color_background(image,width,height,new_width,new_height):
    dominant_color = get_dominant_color(image)
    new_image = Image.new("RGB", (new_width, new_height),dominant_color)
    offset = ((new_width - width) // 2, (new_height - height) // 2)
    new_image.paste(image, offset)
    return new_image
def add_dominant_color_circle(image,width,height,new_width,new_height):
    main_colors = get_main_colors(image, num_colors=5)
    dominant_color = (255, 255, 255)
    new_image = Image.new("RGB", (new_width, new_height),dominant_color)
    draw = ImageDraw.Draw(new_image)
    
    # 定义圆形参数
    radius = 250
    gap = 200
    circle_height = radius * 2 + 200  # 圆形区域的总高度
    
    # 计算垂直边距（确保上下完全相等）
    vertical_margin = (new_height - height) // 2
    
    # 放置图片（正好在正中间）
    offset = ((new_width - width) // 2, vertical_margin)
    new_image.paste(image, offset)
    
    # 计算圆形位置（在底部边距区域的中心）
    center_y = new_height - vertical_margin // 2
    
    # 计算所有圆的总宽度
    total_width = (radius * 2 + gap) * len(main_colors) - gap
    start_x = (new_width - total_width) // 2  # 使圆形组居中
    
    # 画圆形
    for i, color in enumerate(main_colors):
        x = start_x + i * (radius * 2 + gap) + radius
        draw.ellipse([(x - radius, center_y - radius), 
                     (x + radius, center_y + radius)], 
                     fill=color)
    
    return new_image
def add_watermark(image, watermark_path, new_width, new_height):
    """添加水印到图片
    
    Args:
        image: PIL Image对象
        watermark_path: 水印图片路径
        new_width: 新图片宽度
        new_height: 新图片高度
    
    Returns:
        添加水印后的图片
    """
    if not watermark_path:
        return image
        
    try:
        watermark = Image.open(watermark_path)
        watermark_width, watermark_height = watermark.size
        
        # 计算新的水印大小
        scale = min(new_width * 0.25 / watermark_width, new_height * 0.25 / watermark_height)
        new_watermark_size = (int(watermark_width * scale), int(watermark_height * scale))
        
        # 调整水印大小
        watermark = watermark.resize(new_watermark_size, Image.LANCZOS)
        
        # 计算水印位置（底部居中）
        watermark_x = (new_width - new_watermark_size[0]) // 2
        watermark_y = new_height - new_watermark_size[1] - int(new_height * 0.05)  # 底部留5%的边距
        watermark_position = (watermark_x, watermark_y)
        
        # 如果水印有透明通道，使用它作为mask
        mask = watermark if watermark.mode == 'RGBA' else None
        
        # 粘贴水印
        image.paste(watermark, watermark_position, mask)
        return image
        
    except Exception as e:
        print(f"添加水印时出错: {str(e)}")
        return image  # 如果出错，返回原图
def get_img_xmp(image):
    img_xmp = image.getxmp()
    # print(img_xmp)
    paremeterdic={}
    xmp_data=img_xmp['xmpmeta']['RDF']['Description']
    paremeterdic['LensModel']=xmp_data['LensModel']
    paremeterdic['Model']=xmp_data['Model']
    paremeterdic['FocalLength']=float(Fraction(xmp_data['FocalLength']))
    paremeterdic['FNumber']=float(Fraction(xmp_data['FNumber']))
    paremeterdic['ExposureTime']=float(Fraction(xmp_data['ExposureTime']))
    paremeterdic['ISOSpeedRatings']=int(xmp_data['ISOSpeedRatings']['Seq']['li'])
    paremeterdic['Make']=xmp_data['Make']
    date_str=xmp_data['DateTimeOriginal']
    # try:
    #     date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    # except:
    date_obj = parse_iso8601(date_str)
    paremeterdic['DateTimeOriginal']=date_obj.strftime('%Y:%m:%d %H:%M:%S')
    return paremeterdic
def get_img_exif(image):
    img_exif = image._getexif()
    if not img_exif:
        result_dict=get_img_xmp(image)
        return result_dict
    result_dict=defaultdict(str)
    for key, val in img_exif.items():
        if key in ExifTags.TAGS:
            result_dict[ExifTags.TAGS[key]]=val
    return result_dict
def add_Parameter(image):
    parameter_dict=get_img_exif(image)
    width, height = image.size
    lowest_len=min(width,height)
    # self_adative_roit=math.ceil(width*height/(3000*6000)*0.4)
    self_adative_roit=min(width,height)/3500
    watermark = Image.new('RGB', (width, int(lowest_len*0.1)), color=(255, 255, 255))
    watermark_width, watermark_height = watermark.size
    draw = ImageDraw.Draw(watermark)

    Boldfont = ImageFont.truetype("fonts\Roboto-Bold.ttf", int(90*self_adative_roit))
    Lightfont = ImageFont.truetype("fonts\Roboto-Light.ttf", int(70*self_adative_roit))
    #lens
    text = parameter_dict["LensModel"]
    text_position = (int(watermark_height*0.2), int(watermark_height*0.2))
    draw.text(text_position, text, font=Boldfont, fill='black')
    
    #Camera
    text = parameter_dict["Model"]
    text_position = (int(watermark_height*0.2), int(watermark_height)//2+int(10*self_adative_roit)) 
    draw.text(text_position, text, font=Lightfont, fill='gray')
    
    #Parameter
    focal_length=parameter_dict['FocalLength']
    f_number=parameter_dict['FNumber']
    exposure_time = Fraction(parameter_dict['ExposureTime']).limit_denominator() if parameter_dict['ExposureTime'] else 'NA'
    iso=parameter_dict['ISOSpeedRatings']
    para='  '.join([str(focal_length) + 'mm', 'f/' + str(f_number), str(exposure_time)+'s','ISO' + str(iso)])
    _, _, text_width, text_height = Boldfont.getbbox(para)
    text_position = (watermark_width - text_width - int(watermark_height*0.2), int(watermark_height*0.2)) 
    draw.text(text_position, para, font=Boldfont, fill='black') 
    
    #Time
    date=datetime.strptime(parameter_dict['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
    date=date.strftime( '%Y-%m-%d %H:%M')
    text_position = (watermark_width - text_width - int(watermark_height*0.2), int(watermark_height)//2+int(10*self_adative_roit))  # 在图像顶部居中
    draw.text(text_position, date, font=Lightfont, fill='gray')
    
    # Gray line
    draw.line([(watermark_width - text_width - int(50*self_adative_roit) -int(watermark_height*0.2), int(50*self_adative_roit)), (width - text_width - int(50*self_adative_roit) -int(watermark_height*0.2), int(watermark_height)-int(50*self_adative_roit))], fill=(128, 128, 128), width=int(10*self_adative_roit))
      
    # logo
    brand=parameter_dict['Make']
    logo_height=int(watermark_height*0.7)
    logo=get_logo(brand)
    logo=resize_image_with_height(logo,logo_height)
    logo_position = (watermark_width - text_width - int(70*self_adative_roit) -logo.size[0]-int(watermark_height*0.2), int((watermark_height-logo.size[1])//2))  # 在图像顶部居中
    watermark.paste(logo, logo_position)
    
    new_img=Image.new('RGB', (width, int(height+watermark_height)), color=(255, 255, 255))
    new_img.paste(image, (0, 0))
    new_img.paste(watermark, (0, height))
    temp_width,temp_height=new_img.size
    new_background=Image.new('RGB', (int(temp_width*1.05), int(temp_height*1.025)), color=(255, 255, 255))
    new_background.paste(new_img, (int(temp_width*0.025), int(temp_height*0.025)))
    return new_background
def resize_image_with_height(image, height):
    width, old_height = image.size

    scale = height / old_height
    new_width = round(width * scale)

    resized_image = image.resize((new_width, height), Image.LANCZOS)
    image.close()

    return resized_image
def get_logo(brand):
    script_dir = Path(__file__).parent
    file = script_dir / 'logos' / f"{brand.lower().split(' ')[0]}.png"
    logo = Image.open(file)
    return logo
def add_border(image_path, output_path, background_kind=''):
    image = Image.open(image_path)
    width, height = image.size
    
    # 计算圆形背景的参数
    radius = 250  # dominant_color_circle的圆形半径
    gap = 200     # 圆形之间的间隔
    circle_height = radius * 2 + 200  # 圆形区域的总高度
    
    # 计算新的输出尺寸（如果未指定）
    border_height = circle_height + 150  # 圆形高度加上额外边距
    total_vertical_margin = border_height * 2  # 上下边距总和等于圆形区域高度的两倍
    new_height = height + total_vertical_margin
    # 保持原图比例
    scale = new_height / height
    new_width = int(width * scale)
    
    if background_kind == 'dominant_color':
        new_image=add_dominant_color_background(image,width,height,new_width,new_height)
    elif background_kind == 'dominant_color_circle':
        new_image=add_dominant_color_circle(image,width,height,new_width,new_height)
    elif background_kind=='blured':
        new_image=add_blured_background(image,width,height)
        temp_width,temp_height = new_image.size
        left = (temp_width - new_width) // 2
        top = (temp_height - new_height) // 2
        right = left + new_width
        bottom = top + new_height
        new_image = new_image.crop((left, top, right, bottom))
    elif background_kind=='white':
        new_image=add_wite_border(image,width,height,new_width,new_height)
    elif background_kind=='parameter':
        new_image=add_Parameter(image)
    
    new_image.save(output_path,dpi=(240,240), lossless=True)

# 背景类型定义
background_kind = {
    1: 'dominant_color',
    2: 'dominant_color_circle',
    3: 'blured',
    4: 'white',
    5: 'parameter'
}

# 背景类型显示名称
background_display_names = {
    1: "主色调背景",
    2: "主色调圆形背景",
    3: "模糊背景",
    4: "纯白背景",
    5: "自定义参数"
}

def process_images(input_folder, output_folder, background=1, progress_callback=None, log_callback=None):
    """
    处理图片，添加背景
    :param input_folder: 输入文件夹路径
    :param output_folder: 输出文件夹路径
    :param background: 背景类型（1-5）
    :param progress_callback: 进度回调函数
    :param log_callback: 日志回调函数
    """
    if log_callback:
        log_callback("开始处理图片...")
        log_callback(f"输入文件夹: {input_folder}")
        log_callback(f"输出文件夹: {output_folder}")
        
    # 验证背景类型
    if background not in background_kind:
        raise ValueError(f"无效的背景类型: {background}，可用的背景类型为: {list(background_kind.keys())}")
        
    if log_callback:
        log_callback(f"背景类型: {background_display_names[background]}")
    
    try:
        star_time=time.time()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # 获取所有图片文件
        image_files = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        total_images = len(image_files)
        
        if total_images == 0:
            msg = "没有找到图片文件！"
            if log_callback:
                log_callback(msg)
            else:
                print(msg)
            return
            
        if log_callback:
            log_callback(f"共找到 {total_images} 个图片文件")
        else:
            print(f"共找到 {total_images} 个图片文件")
        
        for i, filename in enumerate(image_files):
            try:
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, filename)
                
                if log_callback:
                    log_callback(f"\n处理图片 {i+1}/{total_images}: {filename}")
                else:
                    print(f"\n处理图片 {i+1}/{total_images}: {filename}")
                
                # 使用实际的背景类型值
                add_border(input_path, output_path, background_kind=background_kind[background])
                          
                if progress_callback:
                    progress_callback((i + 1) * 100 // total_images)
                    
            except Exception as e:
                error_msg = f"处理图片 {filename} 时出错: {str(e)}"
                if log_callback:
                    log_callback(error_msg)
                else:
                    print(error_msg)
                continue
                
        end_time=time.time()
        
        completion_msg = f"\n处理完成!\n总耗时: {end_time-star_time:.2f} 秒\n成功处理 {total_images} 张图片"
        if log_callback:
            log_callback(completion_msg)
        else:
            print(completion_msg)
        
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        if log_callback:
            log_callback(error_msg)
        else:
            print(error_msg)
        raise

if __name__ == "__main__":
#Define the input folder path
    input_folder = "2024.11.09Gold 200\ 去色罩"
#Define the output folder path
    output_folder = "2024.11.09Gold 200\加背景3"
    background_type=input('Choose the background type:\n1:dominant_color\n2:dominant_color_circle\n3:blured\n4:white\n')
    process_images(input_folder, output_folder,background=background_type)