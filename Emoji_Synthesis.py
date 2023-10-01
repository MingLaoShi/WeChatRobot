import requests
import logging
from datetime import datetime
from Util import dowanload_Image_From_Url,send_image_on_wechat,send_msg_on_wechat
from PIL import Image
from io import BytesIO

class emoji_synthesis:
    def __init__(self,logger) -> None:
        self.logger=logger

    def trans_to_unicode(self,char):
        unicode_codepoint = ord(char)
        # 将 Unicode 码点转换为十六进制，并添加 \u 前缀
        unicode_hex = hex(unicode_codepoint)
        unicode_repr = "u" + unicode_hex[2:].zfill(4)
        return unicode_repr
    
    def synthesis(self,msg):
        emojis=msg[1]
        now = datetime.now()
        formatted_date = now.strftime("%Y%m%d")
        url=f"https://www.gstatic.com/android/keyboard/emojikitchen/20201001/{self.trans_to_unicode(emojis[1])}/{self.trans_to_unicode(emojis[1])}_{self.trans_to_unicode(emojis[0])}.png"
        print(url)
        filepath=dowanload_Image_From_Url(url,'log\\emoji',f'{emojis[1]}_{emojis[0]}.png')
        if filepath!='error':
            image = Image.open(filepath)
            send_image_on_wechat(emojis,image)
        else:
            send_msg_on_wechat('表情合成',f'{emojis}表情不支持')
        # print(hex(ord(emojis[0])),hex(ord(emojis[1])))

def test():
    emoji_synthesis(logging).synthesis(('dfa','😀😀'))
if __name__=='__main__':
    test()