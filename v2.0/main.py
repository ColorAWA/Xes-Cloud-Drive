from webbrowser import open as web

try:
    import wx
except ModuleNotFoundError:
    from tkinter.messagebox import showerror,askyesno
    from os import system
    showerror('提示','您还没有安装wxPython！')
    yes_no = askyesno('选择','是否安装？')
    if yes_no == True:
        system('pip install wxPython')

import os,hashlib
import requests,json
import wx;from webbrowser import open as web

class up:
    def _getUploadParams(self, filename, md5):
        url = 'https://code.xueersi.com/api/assets/get_oss_upload_params'
        params = {"scene": "offline_python_assets", "md5": md5, "filename": filename}
        response = requests.get(url=url, params=params)
        data = json.loads(response.text)['data']
        #我破解到的C站api
        return data
        
    def uploadAbsolutePath(self, filepath):
        md5 = None
        contents = None
        fp = open(filepath, 'rb')
        contents = fp.read()
        fp.close()
        md5 = hashlib.md5(contents).hexdigest()

        if md5 is None or contents is None:
            raise Exception("文件不存在")

        uploadParams = self._getUploadParams(filepath, md5)
        requests.request(method="PUT", url=uploadParams['host'], data=contents, headers=uploadParams['headers'])
        return uploadParams['url']

class download(wx.Dialog):
    def __init__(self):
        super().__init__(None,title='文件下载',size=(500,200))
        self.Center()
        panel = wx.Panel(self)

        wx.StaticText(panel,label='请在下面的文本框中输入文件地址：',pos=(100,20)).SetFont(wx.Font(15,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL))
        self.file = wx.TextCtrl(panel,pos=(100,50),size=(305,30))
        self.file.SetFont(wx.Font(15,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL))
        download_start = wx.Button(panel,label='开始下载',pos=(395,135),size=(90,30))
        download_start.SetFont(wx.Font(15,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL))
        download_start.Bind(wx.EVT_BUTTON,self.download_file)
        self.Bind(wx.EVT_CLOSE,self.close)

    def download_file(self,event):
        t1 = threading.Thread(target=download_file)
        t1.start()
        del t1

    def close(self,event):
        self.SetFocus()
        self.Destroy()

class Window(wx.Frame):
    def __init__(self):
        super().__init__(None,title='学而思网盘',size=(400,300),style=wx.DEFAULT_FRAME_STYLE^(wx.MAXIMIZE_BOX))
        self.Center()
        self.SetIcon(wx.Icon("xes.ico"))
        self.panel = wx.Panel(self)
        wx.StaticBitmap(self.panel,bitmap=wx.Bitmap("logo.png"),pos=(100,0))
        upload = wx.BitmapButton(self.panel,bitmap=wx.Bitmap("upload.png"),size=(100,30),pos=(70,70))
        upload.SetFont(wx.Font(15,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_LIGHT))
        upload.Bind(wx.EVT_BUTTON,self.upload)
        download = wx.BitmapButton(self.panel,bitmap=wx.Bitmap("download.png"),size=(100,30),pos=(220,70))
        download.SetFont(wx.Font(15,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_LIGHT))
        download.Bind(wx.EVT_BUTTON,self.download)
        wx.StaticText(self.panel,label='日志',pos=(167,105)).SetFont(wx.Font(20,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_LIGHT))
        self.log = wx.TextCtrl(self.panel,style=wx.TE_MULTILINE|wx.TE_MULTILINE,pos=(0,140),size=(380,120))
        self.Show()

    def download(self,event):
        global download_Frame
        download_Frame = download()
        download_Frame.ShowModal()
        del download_Frame

    def upload(self,event):
        self.upload_file = wx.FileDialog(None,message="上传文件",
                        defaultDir=os.getcwd(),
                        style=wx.FD_OPEN,
                        wildcard="所有文件|*.*")
        self.upload_file.ShowModal()
        if self.upload_file:
            for x in range(1):
                try:
                    path=self.upload_file.GetPath()
                    myuploader=up()
                    try:
                        url=myuploader.uploadAbsolutePath(path)
                    except Exception("文件不存在"):
                        wx.MessageDialog(None,'文件不存在！','提示').ShowModal()
                        self.log.AppendText('文件：{}  上传失败！错误：文件不存在\n'.format(path))
                        break
                    url = wx.TextEntryDialog(None,'文件网址：','生成成功！',url,style=wx.OK)
                    url.Center()
                    url.ShowModal()
                    self.log.AppendText('文件：{}  上传成功！\n'.format(path))
                except:
                    pass
                
App = wx.App()
Frame = Window()
def download_file():
    for x in range(1):
        
        '''
        根据文件直链和文件名下载文件

        Parameters
        ----------
        url: 文件直链
        file_name : 文件名（文件路径）

        '''
        # 文件下载直链
        # 请求头    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }
        try:
            url = download_Frame.file.GetValue()
            if url != '':
                if 'https://' in url:
                    if ('https://livefile.xesimg.com/programme/python_assets/') in url:
                        # 发起 head 请求，即只会获取响应头部信息
                        head = requests.head(url, headers=headers)
                        # 文件大小，以 B 为单位
                        file_size = head.headers.get('Content-Length')
                        if file_size is not None:
                            file_size = int(file_size)
                        response = requests.get(url, headers=headers, stream=True)
                        if response.status_code == 404:
                            wx.MessageDialog(None,'文件：{}  下载失败！错误：文件不存在'.format(url),'提示').ShowModal()
                            break
                        # 一块文件的大小
                        chunk_size = 1024
                        x = 1
                        while True:
                            if url[-x] == '/':
                                file_name = url[(-x+1):-1] + url[-1]
                                del x
                                break
                            else:
                                x += 1
                        with open(file_name, mode='wb') as f:
                        # 写入分块文件
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                f.write(chunk)
                        Frame.log.AppendText('文件：{}  下载成功！\n'.format(url))
                    else:
                        Frame.log.AppendText('文件：{}  下载失败！错误：不是学而思直链\n'.format(url))
                        wx.MessageDialog(None,'文件：{}  下载失败！错误：不是学而思直链'.format(url),'提示').ShowModal()
                        break
                else:
                    wx.MessageDialog(None,'下载功能仅支持https协议！','提示').ShowModal()
                    break
            else:
                wx.MessageDialog(None,'请输入链接！','提示').ShowModal()
                break
        except:
            pass
    else:
        wx.MessageDialog(None,'下载成功！','提示').ShowModal()
App.MainLoop()
