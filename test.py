import matplotlib.pyplot as plt
import pyvisa
import visa
import time
from datetime import datetime # std library

class Tektronix_MSO64:
    def __init__(self):
        visa_dll = 'c:/windows/system32/visa32.dll'
        self.rm = pyvisa.ResourceManager()
        # res = rm.list_resources()
        # print(rm)
        # print(res)
        self.inst = self.rm.open_resource('TCPIP0::192.168.1.4::inst0::INSTR')
        ##############################################
        self.inst.write("*IDN?")
        print(self.inst.read())
        self.inst.write('CLEAR')
        self.inst.write('ACQuire:MODe?')
        print(self.inst.read())
        self.inst.timeout = 25000
        self.inst.write('ACQUIRE:STOPAFTER RUNSTOP')
        self.inst.write('ACQuire:STATE RUN')


    def set_HORIZONTAL(self,POSITION,SCALE):#HORIZONTAL position,HORIZONTAL scale /us
        self.inst.write('HORIZONTAL:POSITION %s'%POSITION)
        self.inst.write('HORIZONTAL:SCALE %se-6'%SCALE)

    def open_ch(self,ch):#关闭相应通道
        self.inst.write('DISplay:GLObal:CH%s:STATE ON'%ch)

    def close_ch(self,ch):#打开相应通道
        self.inst.write('DISplay:GLObal:CH%s:STATE OFF'%ch)

    def vertical_ch(self,ch,scale,position):#通道，ch scale/mv，ch POSition，
        self.inst.write('CH%s:BANDWIDTH FULl'%ch)#at its maximum bandwidth
        self.inst.write('CH%s:SCAle %sE-3'%(ch,scale))
        self.inst.write('CH%s:POSition %s'%(ch,position))
        self.inst.write('CH%s:COUPLING DC'%ch)#直流
        self.inst.write('CH%s:TERMINATION 10.0E+5'%ch)#1兆欧

    def trigger_set(self,ch,level):#通道，触发电压
        self.inst.write('TRIGGER:A:EDGE:COUPLING DC')#边沿触发
        self.inst.write('TRIGGER:A:EDGE:SOURCE CH%s'%ch)
        self.inst.write('TRIGGER:A:EDGE:SLOPE RISE')#上升沿触发
        self.inst.write('TRIGGER:A:LEVEL:CH4 %s'%level)

    def begin_trigger(self):#开启一次触发
        self.inst.write('ACQuire:STOPAfter SEQuence')
        while 1:#等触发了才借宿
            time.sleep(1)
            self.inst.write('TRIGGER:STATE?')
            TRIGGER_STATE =self.inst.read()
            if TRIGGER_STATE[0] == "S":
                print('have triggered')
                break

    def data_caul(self,ch):#通道
        self.inst.write('DATA:SOURCE CH%s'%ch)
        self.inst.write('DATa:ENCdg ASCIi')
        self.inst.write('WFMOUTPRE:BYT_NR 4')
        self.inst.write('DATA:START 1')
        self.inst.write('DATA:STOP 250e6')
        self.inst.write('WFMOUTPRE?')
        preamble= self.inst.read()
        #获取HORIZONTAL:POSITION
        self.inst.write('HORIZONTAL:POSITION?')
        HORIZONTAL_p=self.inst.read()
        HORIZONTAL_pfloat=float(HORIZONTAL_p)
        #获取HORIZONTAL:SCALE
        self.inst.write('HORIZONTAL:SCALE?')
        HORIZONTAL_S=self.inst.read()
        HORIZONTAL_Sfloat=float(HORIZONTAL_S)
        #获取ch POSition
        self.inst.write('CH%s:POSition?'%ch)
        divus_str = self.inst.read()
        divus_float = float(divus_str)
        #获取ch SCAle
        self.inst.write('CH%s:SCAle?'%ch)
        div_str = self.inst.read()
        div_float = float(div_str)
        #########################################################获取采样点数目
        j=0
        point_str=' '
        for i in range(0,len(preamble)):
            if preamble[i]==',':
                j+=1
            elif j==4:
                point_str=point_str+preamble[i]
            elif j==5:
                point_len=len(point_str)
                point_str=point_str[2:(point_len-6)]
                break
        point_int=int(point_str)
        print('point_num：%d'%point_int)
        ######################################################数据处理
        data = self.inst.query('CURVE?')
        x = []
        dat = [' ']
        dat1 = []
        j = 0
        for i in range(0, len(data)):
            if data[i] == ',':
                dat1.append(float(dat[j])/32000*div_float*5-div_float*divus_float)
                x.append((int(j)/point_int*HORIZONTAL_Sfloat*10-HORIZONTAL_Sfloat*10*HORIZONTAL_pfloat/100))
                j += 1
                dat.append(' ')
            else:
                dat[j] = dat[j] + data[i]
        plt.plot(x, dat1)

    def close(self):
        self.inst.close()
        self.rm.close()

    def get_screen(self):
        self.inst.write('SAVE:IMAGE "F:/scoIMAGE/waveform_screen.bmp"')
        time.sleep(1)
        self.inst.write('FILESYSTEM:READFILE "F:/scoIMAGE/waveform_screen.bmp"')
        img = self.inst.read_raw()
        dt = datetime.now()
        fileName = dt.strftime("%Y%m%d_%H%M%S.bmp")  # 以当前时间建立文件名
        imgFile = open('./waveform/' + fileName, "wb")  # 打开图片文件，如果没有就会新建一个
        imgFile.write(img)
        imgFile.close()
        self.inst.write('FILESYSTEM:DELETE "F:/scoIMAGE/waveform_screen.bmp"')





if __name__ == "__main__":
    fig = plt.figure()
    my=Tektronix_MSO64()
    my.set_HORIZONTAL(10,200)
    my.open_ch(4)
    my.open_ch(3)
    my.open_ch(2)
    my.open_ch(1)
    my.vertical_ch(4,2000,1)
    my.vertical_ch(3,2000,2)
    my.vertical_ch(2,2000,2)
    my.vertical_ch(1,2000,2)
    my.trigger_set(4,2)
    my.begin_trigger()
    my.data_caul(4)
    my.data_caul(3)
    my.data_caul(2)
    my.data_caul(1)
    my.get_screen()
    plt.show()
    my.close()