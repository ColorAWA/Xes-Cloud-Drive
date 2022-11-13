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
import shutil,requests,json
import wx;from webbrowser import open as web

class up:
    def _getUploadParams(self, filename, md5):
        url = 'https://code.xueersi.com/api/assets/get_oss_upload_params'
        params = {"scene": "offline_python_assets", "md5": md5, "filename": filename}
        response = requests.get(url=url, params=params)
        data = json.loads(response.text)['data']
        # 我破解到的C站api
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
        file = wx.TextEntryDialog(None,'请在下面的文本框中输入文件地址','下载文件','')
        file.ShowModal()
        try:
            url = file.GetValue()
            if url != '':
                if ('https' and 'livefile.xesimg.com') in url:
                    web(url)
                    self.log.AppendText('文件：{}  下载成功！\n'.format(url))
                else:
                    wx.MessageDialog(None,'请输入正确的网址！','提示').ShowModal()
                    self.log.AppendText('文件：{}  下载失败！错误：文件不存在\n')
        except IndexError:
            pass

    def upload(self,event):
        self.file = wx.FileDialog(None,message="上传文件",
                        defaultDir=os.getcwd(),
                        style=wx.FD_OPEN,
                        wildcard="所有文件|*.*")
        self.file.ShowModal()
        if self.file:
            for x in range(1):
                try:
                    path=self.file.GetPath()
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
App.MainLoop()
