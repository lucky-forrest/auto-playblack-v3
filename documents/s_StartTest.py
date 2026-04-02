# -*- coding: UTF-8 -*-
import os
import stat
import eap
import core
import time
import s_Seed
import autoit
import shutil
import Config
import logging
import s_DownLoadzip
import sys
reload(sys)
sys.setdefaultencoding('utf8')
logger = logging.getLogger('s_StartTest.py')

global test_type, lot_num, local_filename, dirct, StationID,path ,Password

#判断op是否登录
def log_in():
    global autoit, time, logger
    try:
        if autoit.win_exists(core.daemonInfo['TESTER']['exe']):                    #先判断执行窗口是否存在
            autoit.win_set_state(core.daemonInfo['TESTER']['exe'],5)               #放大执行窗口
            time.sleep(0.2)
            #hdl_main = autoit.win_get_handle(core.daemonInfo['TESTER']['main'])
            battery_x = core.daemonInfo['TESTER']['battery_x']
            battery_y = core.daemonInfo['TESTER']['battery_y']
            color = autoit.pixel_get_color(int(battery_x), int(battery_y))          #获取当前电源的颜色
            logger.debug(color)
            autoit.mouse_click("left", int(battery_x), int(battery_y))              #关闭电源
            time.sleep(0.2)
            autoit.win_close("[Class:ThunderRT6FormDC]")                            #关闭执行窗口
            time.sleep(0.2)
            if autoit.win_exists("[Class:#32770]"):                                 #是否终止程序弹框
                autoit.control_click("[Class:#32770]", "Button1")
            time.sleep(0.2)
            logger.debug(u'window already exit')
        if not autoit.win_exists(core.daemonInfo['TESTER']['main']):                #判断初始界面是否存在
            Password = core.daemonInfo['TESTER']['password']
            autoit.run(programth)                                                   # 运行软件
            time.sleep(2)
            hdl_main = autoit.win_get_handle(core.daemonInfo['TESTER']['main'])
            autoit.win_activate_by_handle(hdl_main)
            autoit.win_set_state(core.daemonInfo['TESTER']['main'], 5)                             #放大窗口
            time.sleep(0.2)
            login_x = core.daemonInfo['TESTER']['login_x']
            login_y = core.daemonInfo['TESTER']['login_y']
            autoit.mouse_click("left", int(login_x), int(login_y))                      #点击登录按钮
            if not autoit.win_exists("[Class:#32770]"):
                autoit.control_click(hdl_main, "ToolbarWindow32")                   #如果没有弹出登录窗口就再点一次登录按钮
            autoit.control_click(hdl_main, "TBitBtn4")                              #点击选择用户名称
            loginName_x = core.daemonInfo['TESTER']['loginName_x']
            loginName_y = core.daemonInfo['TESTER']['loginName_y']
            autoit.mouse_click("left", int(loginName_x), int(loginName_y))          #点击选择工程师
            autoit.control_set_text(hdl_main, "Edit2", Password)                    #输入密码
            autoit.control_click(hdl_main, "Button1")                               #点击确认
            #autoit.win_wait_active(core.daemonInfo['TESTER']['main'])
            logger.debug(u'Op login successfully')
            return True
    except BaseException as ex:
        logger.debug(u'Get log in exception message: {}'.format(ex))
        print (u'Get log in exception message: {}'.format(ex))
        return False


# 加载程序
def load_program(path,grade):
    global autoit, time, logger
    try:
        hdl_main = autoit.win_get_handle(core.daemonInfo['TESTER']['main'])
        autoit.win_activate_by_handle(hdl_main)
        time.sleep(0.2)
        autoit.control_click(hdl_main, "Button3")                                                  #添加程序
        time.sleep(0.2)
        autoit.win_wait(u"打开",30)
        hdl_main = autoit.win_get_handle(u"打开")
        autoit.win_activate_by_handle(hdl_main)
        time.sleep(0.2)
        autoit.win_set_state(hdl_main, 5)                                                           #放大打开窗口
        time.sleep(0.2)
        autoit.control_set_text(u"",core.daemonInfo['TESTER']['box'], path)                          # 输入文件路径
        time.sleep(0.2)
        autoit.control_click("", "Button1")                                                           #打开程序
        time.sleep(0.2)
        autoit.control_click(core.daemonInfo['TESTER']['main'], "Button7")                             #执行程序
        return True
    except BaseException as ex:
        logger.debug(u'Get load program exception message: {}'.format(ex))
        print (u'Get load program exception message: {}'.format(ex))
        return False


#批次信息
def new_lot(lot_id):
    global logger, time, autoit
    try:
        autoit.win_wait(core.daemonInfo['TESTER']['exe'], 30)
        autoit.win_set_state(core.daemonInfo['TESTER']['exe'],5)               #放大执行窗口
        time.sleep(0.2)
        #hdl_main = autoit.win_get_handle(core.daemonInfo['TESTER']['main'])
        battery_x = core.daemonInfo['TESTER']['battery_x']
        battery_y = core.daemonInfo['TESTER']['battery_y']
        autoit.mouse_click("left", int(battery_x), int(battery_y))              #打开电源
        time.sleep(1)
        zidong_x = core.daemonInfo['TESTER']['zidong_x']
        zidong_y = core.daemonInfo['TESTER']['zidong_y']
        autoit.mouse_click("left", int(zidong_x), int(zidong_y))  # 打开电源
        autoit.win_wait(u"芯片批号设置",10)
        hdl_main = autoit.win_get_handle(u"芯片批号设置")
        autoit.win_activate_by_handle(hdl_main)
        time.sleep(0.1)
        autoit.control_click(hdl_main, "Thunderrt6textbox2")                              #点击芯片号/小批号输入框
        time.sleep(0.2)
        autoit.control_set_text(hdl_main, "Thunderrt6textbox2", lot_id)                   #输入批次
        time.sleep(0.5)
        autoit.control_click(hdl_main, "ThunderRT6CommandButton1")                        #点击设置按钮




        # #lot id Click on the coordinates
        # lot_x = core.daemonInfo['TESTER']['lot_x']
        # lot_y = core.daemonInfo['TESTER']['lot_y']
        # autoit.mouse_click(u"left",int(lot_x),int(lot_y))  # 输入批次号
        # time.sleep(0.1)
        # autoit.send(lot_id)
        # time.sleep(0.1)
        # autoit.control_click("", u"确定")  # 确定批次信息
        # time.sleep(0.1)
        # hdl_main = autoit.win_get_handle(core.daemonInfo['TESTER']['main'])
        # autoit.win_activate_by_handle(hdl_main)
        # time.sleep(0.1)
        # # Start Test
        # start_x = core.daemonInfo['TESTER']['start_x']
        # start_y = core.daemonInfo['TESTER']['start_y']
        # autoit.mouse_click(u"left", int(start_x),int(start_y))  # 开始测试
        return True
    except Exception as ex:
        logger.debug(u'system_setup failed: {}'.format(ex))
        print (u'system_setup failed: {}'.format(ex))
        return False

def createfiles(filepathname):
    try:
        os.makedirs(filepathname)
    except Exception as err:
        print(str(filepathname) + "已经存在！")

def DownloadProgram():
    autoit.win_set_state(core.daemonInfo['TESTER']['main'],5)
    hdl_main = autoit.win_get_handle(core.daemonInfo['TESTER']['main'])
    autoit.win_activate_by_handle(hdl_main)
    autoit.win_set_state(core.daemonInfo['TESTER']['main'],3)



    #autoit.mouse_click(u"left", int(unload_x), int(unload_y))

    # try:
    #     # End test
    #     end_x = core.daemonInfo['TESTER']['end_x']
    #     end_y = core.daemonInfo['TESTER']['end_y']
    #     autoit.mouse_click(u"left", int(end_x), int(end_y))             # 停止
    #     time.sleep(0.1)
    #     # Click on the unload coordinates
    #     unload_x = core.daemonInfo['TESTER']['unload_x']
    #     unload_y = core.daemonInfo['TESTER']['unload_y']
    #     autoit.mouse_click(u"left", int(unload_x), int(unload_y))
    #     time.sleep(0.2)
    #     hdl_main = autoit.win_get_handle(u"Confirm")
    #     autoit.win_activate_by_handle(hdl_main)
    #     time.sleep(0.2)
    #     autoit.control_click("", u"&Yes")                                #卸载程序
    #     time.sleep(0.2)
    #     logger.debug(u"End Test Program successfully")
    #     #upload_test_data(r'C:\AccoTest\STS8200CROSS\DATALOG\ETA5053V280DD1E_A_S6_4SITE_218B67014-SJ-D18-C118-S6-1_2021-10-23_0_36_26_.XLS',r'ftp://192.168.6.56/QT/ETA5053V280DD1E_A_S6_4SITE_218B67014-SJ-D18-C118-S6-1_2021-10-23_0_36_26_.XLS')
    # except BaseException as ex:
    #     logger.debug(u'End Test Program exception message: {}'.format(ex))


    time.sleep(0.1)
    global eap,os,s_DownLoadzip
    evt = 'E_StartTest'
    data = core.msgInfo[evt]
    body = eap.get_body(data)
    # FTP Config
    port = int(body['FtpPort'])
    logger.debug('createfiles successfully: DownloadProgram')
    user = body['FtpUser']
    host = body['FTPServer']
    passwd = body['FtpPwd']
    '''
    port = '21'#body['FtpPort']
    user = 'administrator'#body['FtpUser']
    host = '192.168.6.56'#body['FTPServer']
    passwd = 'fsbrec@3388'#body['FtpPwd']
    '''
    PrgName = body['FileName']
    PrgFile = body['FilePath']


    dirct = core.daemonInfo['TESTER']['LocalPath1']
    dirct1 = core.daemonInfo['TESTER']['ConfigPath']
    address = os.path.join(dirct, PrgName)
    PrgName_zip = PrgName[:-4]
    TestType = body['TestType']
    address = os.path.join(dirct, PrgName)
    try:
        os.makedirs(dirct)
    except Exception as err:
        logger.debug('createfiles successfully: {}'.format(err))
        pass

    # Local file removed
    try:
        rr = s_DownLoadzip.isDir(dirct)
        if rr:
            logger.debug('Local file removed successfully: {}'.format(rr))
        else:
            logger.debug('Local file removed failed: {}'.format(rr))
    except Exception as rr:
        logger.debug('Local file removed  error : {}'.format(rr))
        print ("Local file removed  error")
        core.lotInfo['ReturnMessage'] = "Local file removed error"
        core.lotInfo['ReturnCode'] = "NG"
        s_Seed.start_test()
        return False
        pass

    # Connect to FTP
    try:
        data = s_DownLoadzip.Connect(host, port)
        if data:
            src = s_DownLoadzip.Login(user, passwd)
            if src:
                logger.debug('ftp connect successful: {}'.format(data, src))
            else:
                logger.debug('FTP account password error: {}'.format(data, src))
        else:
            logger.debug('ftp connect error : {}'.format(data))
    except:
        logger.debug('FTP account error : {}'.format(data))
        print ("FTP account error")
        core.lotInfo['ReturnMessage'] = "FTP account error"
        core.lotInfo['ReturnCode'] = "NG"
        s_Seed.start_test()
        return False
        pass

    # Download test program package in FTP
    try:
        #/AE/STS8200/J301/ETA5060V330DBI/FT/
        #ee = PrgFile.encode("utf8") +"/"+PrgName  #QT/BP5131SC_BP5131HAB_V0.2_T9/DataLog/
        #ee = "AE/STS8200/J301/ETA5060V330DBI/FT" +"/"+"ETA5060V330DBI_V1.3_S5_4SITE_shao_tiao.zip"  #QT/BP5131SC_BP5131HAB_V0.2_T9/DataLog/
        #ee = "ETA5060V330DBI_V1.3_S5_4SITE_shao_tiao.zip"  #QT/BP5131SC_BP5131HAB_V0.2_T9/DataLog/
        #ee = ee1.decode("utf8").encode("gbk")#PrgFile.encode("utf8")+"/"+PrgName  #QT/BP5131SC_BP5131HAB_V0.2_T9/DataLog/
        #ee = "QT/BP5131SC_BP5131HAB_V0.2_T9/DataLog"+"/"+"default03-07-17 15.58.36.dl4"  #QT/BP5131SC_BP5131HAB_V0.2_T9/DataLog/
        ee = PrgName
        #AE / STS8200 / J301 / ETA5060V330DBI / FT /
        RemotePath = PrgFile.encode("utf8")#u'AE/%BB%AA%B7%E5STS8200/J301/ETA5060V330DBI/FT/'
        data = s_DownLoadzip.DownLoadFile(address,RemotePath,ee)
        if data:
            logger.debug('Download successfully : {}'.format(data))
            print ("Download successfully")
    except:
        logger.debug('Download file empty: {}'.format(data))
        print ("Download file empty")
        core.lotInfo['ReturnMessage'] = "Download file empty"
        core.lotInfo['ReturnCode'] = "NG"
        s_Seed.start_test()
        return False
        pass

    # Download test program package in FTP and Unzip
    try:
        data = s_DownLoadzip.un_zip(address, dirct)
        if data:
            logger.debug('un_zip successfully : {}'.format(data, address))
            print ("The package was decompressed successfully")
    except:
        logger.debug('un_zip failed : {}'.format(data))
        print ("un_zip failed ")
        core.lotInfo['ReturnMessage'] = "un_zip failed"
        core.lotInfo['ReturnCode'] = "NG"
        s_Seed.start_test()
        return False
        pass

    # Get program files
    try:
        #address1 = os.path.join(dirct, PrgName_zip, TestType)
        address1 = os.path.join(dirct, PrgName_zip)
        for root, dirs, files in os.walk(address1):
            for name in files:
                if ".pgs" in name:
                    global path
                    path = os.path.join(root, name)
                    logger.debug('Get program files successfully : {}'.format(path))
                    flag = True
                    print path
                    break
            if flag:
                return True
                break
    except:
        logger.debug('Get program files error : {}'.format(path))
        print ("Get program files error ")
        core.lotInfo['ReturnMessage'] = "Get program files error"
        core.lotInfo['ReturnCode'] = "NG"
        s_Seed.start_test()
        return False
        pass

# 总的调度函数
def scheduling_function(grade,lot_id):
    global core,logger,log_in,load_program,new_lot,s_Seed,DownloadProgram
    try:
        # if log_in():
        #     logger.debug(u'Log in function scheduled successfully')
        #     if DownloadProgram():
        #         logger.debug(u'FTP DownloadProgram successfully!')
        #         if load_program(path, grade):
        #             logger.debug(u'Load program function scheduled successfully')
        #             if new_lot(lot_id):
        #                 logger.debug(u"New lot function scheduled successfully")
        #                 core.lotInfo['ReturnMessage'] = "successfully"
        #                 core.lotInfo['ReturnCode'] = "OK"
        #                 s_Seed.start_test()
        #             else:
        #                 logger.debug(u'New lot function scheduled failed')
        #                 print (u'New lot function scheduled failed')
        #                 core.lotInfo['ReturnMessage'] = "failed"
        #                 core.lotInfo['ReturnCode'] = "NG"
        #                 s_Seed.start_test()
        #         else:
        #             logger.debug(u'Load program  function scheduled failed')
        #             print (u'Load program  function scheduled failed')
        #             core.lotInfo['ReturnMessage'] = "failed"
        #             core.lotInfo['ReturnCode'] = "NG"
        #             s_Seed.start_test()
        #     else:
        #         logger.debug(u'FTP Download Program failed')
        #         print (u'FTP Download Program failed')
        #         core.lotInfo['ReturnMessage'] = "failed"
        #         core.lotInfo['ReturnCode'] = "NG"
        #         s_Seed.start_test()
        # else:
        #     logger.debug(u'Log in function scheduled failed')
        #     print (u'Log in function scheduled failed')
        #     core.lotInfo['ReturnMessage'] = "failed"
        #     core.lotInfo['ReturnCode'] = "NG"
        #     s_Seed.start_test()
        core.lotInfo['ReturnMessage'] = "successfully"
        core.lotInfo['ReturnCode'] = "OK"
        s_Seed.start_test()
    except BaseException as ex:
        logger.debug(u'Test program loading exception message: {}'.format(ex))
        print (u'Test program loading exception message: {}'.format(ex))
        core.lotInfo['ReturnMessage'] = ex
        core.lotInfo['ReturnCode'] = "NG"
        s_Seed.start_test()

num = 0
StationID = 'True'
evt = 'E_StartTest'
data = core.msgInfo[evt]
body = eap.get_body(data)
#FTP Config
port = body['FtpPort']
user = body['FtpUser']
host = body['FTPServer']
dirct = core.daemonInfo['TESTER']['LocalPath1']
#dirct1 = body['ConfigPath']
passwd = body['FtpPwd']
PrgName = body['FileName']
PrgFile = body['FilePath']
PrgName_zip = PrgName[:-4]
#address =os.path.join(dirct, PrgName)


lot_id = body['LotID']
# dir1 = core.daemonInfo['TESTER']['dir']
# dir = unicode(dir1,"gbk").encode('utf-8')
filepath = body['FileName']
#Y:\IC标准测试程序\ACCO测试程序\ETA5060V330DBI_V1.3_S5_4SITE_shao_tiao\ETA5060V330DBI_V1.3_S5_4SITE_shao_tiao\ETA5060V330DBI_V1.3_S5_4SITE_shao_tiao.pgs
path='' #os.path.join(dir, filepath, filepath+'.pgs')
#path = dirct + '\\' + PrgName_zip
#path = dir + '\\' +filepath+'\\'+filepath+'.pgs'
StationID = body['Station']

loginName_x = core.daemonInfo['TESTER']['loginName_x']
loginName_y = core.daemonInfo['TESTER']['loginName_y']

Password = core.daemonInfo['TESTER']['Password']

battery_x = core.daemonInfo['TESTER']['battery_x']
battery_y = core.daemonInfo['TESTER']['battery_y']

main = core.daemonInfo['TESTER']['main']
name = core.daemonInfo['TESTER']['name']
programth = core.daemonInfo['TESTER']['programpath']
box = core.daemonInfo['TESTER']['box']
#DownloadProgram()
scheduling_function(StationID, lot_id)