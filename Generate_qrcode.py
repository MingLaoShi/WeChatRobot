import qrcode
import uuid
import os
import logging
class generate_qrcode:
    def __init__(self,logger) -> None:
        self.logger=logger

    def generate(self,message):
        text=message[1]
        code_img=qrcode.make(text)
        img_name=str(uuid.uuid4())+'.png'
        self.logger.info("二维码生成成功。")
        if __debug__:
            file_path=os.path.join('log','qrcode',img_name)
            code_img.save(file_path)
        
def test():
    generate_qrcode(logging).generate(('wo','这是个测试用的qrcode图像'))

if __name__=='__main__':
    test()