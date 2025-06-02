from PIL import Image
import os
from pathlib import Path

def get_optimal_image(img, target_size):
    """根据目标尺寸优化图像大小，保持图像质量"""
    current_size = img.size[0]  # 假设是正方形图像
    
    # 如果当前尺寸小于目标尺寸，使用高质量放大
    if current_size < target_size:
        return img.resize((target_size, target_size), Image.LANCZOS)
    # 如果当前尺寸大于目标尺寸，使用高质量缩小
    elif current_size > target_size:
        return img.resize((target_size, target_size), Image.LANCZOS)
    return img

def convert_png_to_ico(png_path, output_dir=None, sizes=None):
    """将PNG图像转换为ICO格式"""
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]
    
    try:
        # 确保输出目录存在
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.basename(png_path)
            file_name, _ = os.path.splitext(base_name)
            ico_path = os.path.join(output_dir, f"{file_name}.ico")
        else:
            ico_path = os.path.splitext(png_path)[0] + ".ico"
        
        with Image.open(png_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 为每个尺寸创建优化后的图像
            optimized_images = []
            for size in sizes:
                optimized_img = get_optimal_image(img, size)
                optimized_images.append((size, size))
            
            # 保存优化后的图像
            img.save(ico_path, format='ICO', sizes=optimized_images)
            print(f"成功生成ICO: {ico_path}")
            print(f"包含尺寸: {', '.join([f'{s}x{s}' for s in sizes])}")
            return ico_path
    except Exception as e:
        print(f"ICO转换失败: {str(e)}")
        return None

def convert_png_to_icns(png_path, output_dir=None, sizes=None):
    """将PNG图像转换为ICNS格式（macOS图标）"""
    if sizes is None:
        sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    try:
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.basename(png_path)
            file_name, _ = os.path.splitext(base_name)
            icns_path = os.path.join(output_dir, f"{file_name}.icns")
        else:
            icns_path = os.path.splitext(png_path)[0] + ".icns"
        
        with Image.open(png_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 创建临时PNG文件
            temp_dir = Path(output_dir) / "temp_icons" if output_dir else Path("temp_icons")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 为每个尺寸创建优化后的PNG文件
            temp_files = []
            for size in sizes:
                optimized_img = get_optimal_image(img, size)
                temp_path = temp_dir / f"icon_{size}x{size}.png"
                optimized_img.save(temp_path, format='PNG')
                temp_files.append(temp_path)
            
            # 使用iconutil命令生成icns（仅在macOS上可用）
            # 如果在Windows上，我们只生成一系列PNG文件
            if os.name == 'posix':  # macOS
                try:
                    iconset_path = temp_dir / "icon.iconset"
                    iconset_path.mkdir(exist_ok=True)
                    
                    for size, temp_file in zip(sizes, temp_files):
                        icon_name = f"icon_{size}x{size}.png"
                        os.rename(temp_file, iconset_path / icon_name)
                    
                    os.system(f"iconutil -c icns -o {icns_path} {iconset_path}")
                    print(f"成功生成ICNS: {icns_path}")
                except Exception as e:
                    print(f"ICNS生成失败（仅支持macOS）: {str(e)}")
            else:
                print("注意：ICNS格式仅在macOS系统上支持生成")
                print(f"已生成对应尺寸的PNG文件在: {temp_dir}")
            
            print(f"包含尺寸: {', '.join(str(s) for s in sorted(sizes))}")
            return icns_path if os.name == 'posix' else str(temp_dir)
            
    except Exception as e:
        print(f"转换失败: {str(e)}")
        return None
    finally:
        # 清理临时文件
        if 'temp_dir' in locals():
            if os.name != 'posix':  # 在非macOS系统上保留PNG文件
                for file in temp_dir.glob("icon.iconset"):
                    try:
                        file.unlink()
                    except:
                        pass
                try:
                    temp_dir.rmdir()
                except:
                    pass

def main():
    # 使用相对路径
    script_dir = Path(__file__).parent
    input_png = script_dir / "icon" / "logo.png"
    output_dir = script_dir / "icon"
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 自定义尺寸（可选）
    custom_ico_sizes = [16, 32, 48, 64, 128, 256, 512]    # ICO格式尺寸
    custom_icns_sizes = [16, 32, 64, 128, 256, 512, 1024]  # ICNS格式尺寸
    
    # 执行转换
    try:
        # 验证输入文件
        if not input_png.exists():
            print(f"错误：输入文件不存在 - {input_png}")
            return
        
        if input_png.suffix.lower() != '.png':
            print(f"错误：输入文件必须是PNG格式 - {input_png}")
            return
        
        # 生成ICO
        print("\n正在生成ICO文件...")
        ico_path = convert_png_to_ico(
            str(input_png), 
            output_dir=str(output_dir), 
            sizes=custom_ico_sizes
        )
        
        # 生成ICNS
        print("\n正在生成ICNS文件...")
        icns_path = convert_png_to_icns(
            str(input_png), 
            output_dir=str(output_dir), 
            sizes=custom_icns_sizes
        )
        
        print("\n转换完成！")
        if ico_path: print(f"ICO文件位置: {ico_path}")
        if icns_path: print(f"ICNS/PNG文件位置: {icns_path}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()    