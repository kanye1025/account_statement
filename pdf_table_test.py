from PyPDF2 import  PdfReader, PdfWriter
from PIL import Image
import os
import io
import fitz
file = "D:\\Users\\kanye2\\Desktop\\银行流水\\银行流水\\1669097456441_1159645.pdf"
from PIL import Image
file_reader = PdfReader(file)
f = open(file,'rb')
b = f.read()
pdf = fitz.open(stream = b)  # PyMuPdf安装后，包的名字叫fitz
n = 1  # 判断找到多少张图片
is_exists_im = False
adr_temp = "D:\\Users\\kanye2\\Desktop\\银行流水\\银行流水\\"
for p in pdf:  # 遍历pdf的每一页
    ims = p.get_images()  # 获取当前页的图片，返回一个list
    if ims:
        is_exists_im = True  # 如果图片不为空
        for im in ims:  # 遍历没张图片
            # 以下和删除图片无关，只是把删除的图片保存起来
            image = pdf.extract_image(im[0])
            im_info = image['image']
            im_ext = image['ext']
            image_ = Image.open(io.BytesIO(im_info))
            im_name = str(n) + '.' + str(im_ext)
            im_path = os.path.join(adr_temp, im_name)
            image_.save(im_path)

            pdf._deleteObject(im[0])  # 删除图片
            n += 1
if is_exists_im is True:
    ret = pdf.write()
    pdf.save("D:\\Users\\kanye2\\Desktop\\银行流水\\银行流水\\1669097456441_1159645_2.pdf")
    pdf.close()
