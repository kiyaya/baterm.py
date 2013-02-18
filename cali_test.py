#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import pango
import threading
from threading import Thread
import serial
import time
import datetime
import re
import os
import chardet

import basiclex
import basparse
import basinterp

import cali_scan
import cali_msp430
if os.name == 'posix' :
    import pexpect
else:
    import subprocess
    
if os.name == 'nt' :
    from serial.tools.list_ports_windows import *
elif os.name == 'posix' :
    from serial.tools.list_ports_posix import *
else :
    raise ImportError("Sorry: no implementation for your platform ('%s') available" % (os.name,))

class CaliTest:
    def ConvertCN(self, s):  
        return s.encode('gb18030')  
    
    def on_FileChooserButtonOfTestMode_selection_changed(self, widget, data=None):
        # TODO:  1. There are 3 events happened at init
        #        2. No need to write configure file even the filename is not changed.
        try:
            with open("./cali.conf", "w") as f:
                content = "DEFAULT_SCRIPT=" + str(self.FileChooserButtonOfTestMode.get_filename())
                f.write(content)
        except:
            print "cali.conf create failed."
        self.EntryOfSerialNumber.grab_focus()
        
    def on_window_expose_event(self, widget, data=None):
        self.EntryOfSerialNumber.grab_focus()
        
    def on_window_destroy(self, widget, data=None):
        self.on_ButtonSend_clicked(0, "_stop")
        self.serial_close_all()
        gtk.main_quit()
        print "leaving..."
  
    def on_ButtonScan_clicked(self, widget, data=None):
        self.on_ButtonSend_clicked(0, "_scan")

    def on_ButtonMsp430_clicked(self, widget, data=None):
        self.on_ButtonSend_clicked(0, "_msp430")
        
    def on_window_key_press_event(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "F1":
            self.on_ButtonYes_clicked(0, None)
        elif key == "F2":
            self.on_ButtonNo_clicked(0, None)
        elif key == "Return":
            self.on_ButtonStart_clicked(0, None)

    def on_ToggleButtonOfDebug_toggled(self, widget, data=None):
        self.FrameOfDebug.set_visible(not self.FrameOfDebug.get_visible())   
        self.EntryOfCommand.grab_focus()
                         
    def on_ButtonStart_clicked(self, widget, data=None):     
        #serial_number = self.EntryOfSerialNumber.get_text()
        #if not serial_number.isdigit():
        #    self.insert_into_console("Please scan barcode first.\n")
        #    self.EntryOfSerialNumber.grab_focus()
        #    return 
        #self.serial_number = serial_number
        file = self.FileChooserButtonOfTestMode.get_filename()
        if file != None:
            filename, fileext = os.path.splitext(file)
            if fileext == ".cali":
                self.on_ButtonSend_clicked(0, "_batch " + self.FileChooserButtonOfTestMode.get_filename())
            elif fileext == ".bas":
                self.on_ButtonSend_clicked(0, "_ply " + self.FileChooserButtonOfTestMode.get_filename())

    def on_ButtonStop_clicked(self, widget, data=None):
        if self.ThreadOfPly != None and self.ThreadOfPly.is_alive():
            self.on_ButtonSend_clicked(0, '_stop')
        self.EntryOfSerialNumber.grab_focus()
    
    def on_ButtonYes_clicked(self, widget, data=None):
        if self.ThreadOfPly != None and self.ThreadOfPly.is_alive():
            self.on_ButtonSend_clicked(0, '_yes')
            
    def on_ButtonNo_clicked(self, widget, data=None):
        if self.ThreadOfPly != None and self.ThreadOfPly.is_alive():
            self.on_ButtonSend_clicked(0, '_no')            
        
    def on_ComboBoxOfUart_changed(self, widget):
        self.serial_close_all()                
        model = self.ComboBoxOfUart.get_model()
        active = self.ComboBoxOfUart.get_active()
        port = model[active][0]

        if port != "NONE":
            baudrate = model[active][1]
            self.serial_connect(port, baudrate)
            self.EntryOfCommand.grab_focus()
        
    def on_TextOfLog_size_allocate(self, widget, event, data=None):
        adj = self.ScrolledWindowOfLog.get_vadjustment()
        adj.set_value(adj.upper - adj.page_size)
    
    def on_FileChooserButton_file_set(self, widget):
        file = self.FileChooserButton.get_filename()
        filename, fileext = os.path.splitext(file)

        if fileext == ".cali":
            self.EntryOfCommand.set_text("_batch " + self.FileChooserButton.get_filename())
        elif fileext == ".bas":
            self.EntryOfCommand.set_text("_ply " + self.FileChooserButton.get_filename())

        self.EntryOfCommand.grab_focus()
 
    def on_ButtonSend_clicked(self, widget, cmd=None):        
        if cmd == None:
            cmd = self.EntryOfCommand.get_text()
       
        if not cmd.isspace() and cmd != '':
            cmd = cmd.split()
            cmd[0] = cmd[0].lower()
            if cmd[0].startswith('_'):  # local and mcu's command
                if cmd[0] == '_clear':
                    #if self.ThreadOfPly == None or not self.ThreadOfPly.is_alive():    # avoid accessing the shared resource: CONSOLE
                    start, end = self.TextBufferOfLog.get_bounds()
                    gobject.idle_add(self.TextBufferOfLog.delete, start, end)
                elif cmd[0] == '_ver':
                    self.insert_into_console(self.window.get_title() + '\n')
#                elif cmd[0] == '_start':
#                    if len(cmd) > 1:
#                        if cmd[1].isdigit():
#                            voltage = (int(cmd[1]) + 4) / 5 * 5
#                            self.TextBufferOfLog.insert_at_cursor("Start to calibrate at " + str(voltage) + "mV.\n")
#                            self.ButtonResultByColor.set_color(gtk.gdk.Color('green'))
                elif cmd[0] == '_scan': # should be deleted before release.
                    #Thread(target=cali_scan.CaliScan(self.ListStoreOfScan, self.ListOfPrinterSettings).run, args=(self.window, )).start()
                    #time.sleep(0.1)
                    start, end = self.TextBufferOfLog.get_bounds()
                    cali_scan.CaliScan(printer_settings_mutable = self.ListOfPrinterSettings, console_log = self.TextBufferOfLog.get_text(start, end)).run(parent_window = self.window)
                elif cmd[0] == '_msp430': # should be deleted before release.
                    cali_msp430.Msp430().run(parent_window = self.window)                                                               
                elif cmd[0] == '_stop':
                    self.condition.acquire()
                    self.condition.notifyAll()
                    self.condition.release()
                    self.set_check_status(0x80000000)                    
                    self.insert_into_console("The calibration process is stopped.\n")
                elif cmd[0] == '_yes':
                    self.condition.acquire()
                    #print "cond acquired"
                    if self.get_check_status() != 0:    # avoid twice key-event issue in Linux
                        self.set_check_status(0)
                    if self.get_ack_to_plying() != 0:
                        self.set_ack_to_plying(0)
                    #print "cond notifying"
                    self.condition.notifyAll()
                    self.condition.release()
                    #print "cond notified and released"                    
                elif cmd[0] == '_no':
                    self.condition.acquire()
                    #print "cond_ acquired"                    
                    if self.get_check_status() != 1:
                        self.set_check_status(1)
                    if self.get_ack_to_plying() != 0:
                        self.set_ack_to_plying(0)
                    #print "cond_ notifying"
                    self.condition.notifyAll()
                    self.condition.release()
                    #print "cond_ notified and released"
                elif cmd[0] == '_batch':
                    if len(cmd) > 1:
                        if os.path.isfile(cmd[1]):
                            self.insert_into_console("Batch processing with file " + cmd[1] + '\n')
                            file = open(cmd[1], 'r')
                            self.cmds = file.readlines()
                            file.close() 
                        else:
                            self.cmds = [cmd[1]]   
                           
                        self.ply_need_start = 1
                        self.ply_mode = 0   
                elif cmd[0] == '_ply':
                    if len(cmd) > 1:
                        if os.path.isfile(cmd[1]):
                            if self.ThreadOfReceiving == None or not self.ThreadOfReceiving.is_alive():
                                self.insert_into_console("Please check the UART connection and restart the program.\n")
                                self.set_check_status(1)
                            else:
                                self.insert_into_console("PLY processing with file " + cmd[1] + "\n")
                                self.cmds = cmd[1]
                                self.ply_need_start = 1
                                self.ply_mode = 1
                                                          
            else:   # device's command
                model = self.ComboBoxOfUart.get_model()
                active = self.ComboBoxOfUart.get_active()
                
                port = model[active][0]
                if port != "NONE":
                    if self.ser[port][0] != None: 
                        text = ''
                        for command in cmd:
                            text += command
                            text += ' '
                        self.ser[port][0].write(text.rstrip() + "\n")
                        time.sleep(0.2) # make sure the command is sent completely
                    
            #self.EntryOfCommand.set_text("")
            if self.FrameOfDebug.get_visible():
                self.EntryOfCommand.grab_focus()
                
    def on_ButtonClear_clicked(self, widget):
        self.on_ButtonSend_clicked(0, '_clear')
           
    def on_EntryOfCommand_activate(self, widget):
        self.on_ButtonSend_clicked(widget)
        
    def receiving(self, port, rates):    # device's feedback

        print "thread receiving starts..\n"
        line = ''
        while True:
            if(self.ply_need_start == 1):
                if self.ThreadOfPly == None or not self.ThreadOfPly.is_alive():
                    self.ThreadOfPly = Thread(target=self.plying, args=(port, self.ply_mode,))
                    self.ThreadOfPly.start()
                    time.sleep(0.1)
                    self.ThreadOfPly.join()
                self.ply_need_start = 0    
                
            self.mutex.acquire()  
            ser_is_alive = self.ser[port][0]
            self.mutex.release()
            if(ser_is_alive != None):
                try:
                    left = self.ser[port][0].inWaiting()
                    
                except serial.serialutil.SerialException:
                    self.serial_close_all()
                    ###gtk.threads_enter()
                    self.insert_into_console("\nPlease connect the serial device and reboot the program.\n")
                    ###gtk.threads_leave()
                else:
                    if left > 0 :
                        line += self.ser[port][0].read(left)   
                        if line != '' :
                            ###gtk.threads_enter()
                            self.insert_into_console(line)
                            ###gtk.threads_leave()
                        line = ''
                
            else:
                print "thread receiving exit.."
                break
                #todo: need usb plug/unplug signal
            
            time.sleep(0.01)    # avoid too much cpu resource cost
            
    def get_batching_result(self, keywords):
        keywords = keywords.upper()
        if keywords in self.batching_result:
            result = self.batching_result[keywords]
            del self.batching_result[keywords]
            return result
        else:
            return None
    
    def set_batching_result(self, data_with_2line):
        if len(data_with_2line) > 1:
            self.batching_result[data_with_2line[0]] = data_with_2line[2]
        
    def batching(self, port, cmd, check_mode):
        print "thread batching starts...\n"

        self.ser[port][0].flushInput()
        self.ser[port][0].flushOutput()
        
        #for cmd in self.cmds:
        cmd = cmd.strip()
        self.ser[port][0].write(cmd + "\n")
        if check_mode == "AUTO":
            while True:
                ch = self.ser[port][0].read(1)                
                if ch.isdigit() or self.batch_is_timeout == 1:
                    break

        time.sleep(0.5)
        text = ''
        line = cmd.upper() + " "
        if check_mode == "AUTO":
            if self.batch_is_timeout == 1:
                self.batch_is_timeout = 0
                ch = '1'
                text = "(timeout)"
            
            #self.ser[port][0].flushInput()
            if ch == '0':
                self.set_check_status(0)
                text += " is succeed\n"
            else:
                self.set_check_status(1)
                text += " is failed\n"   
            self.ack_to_plying = 0   
            #gtk.threads_enter()
            self.insert_into_console(cmd.upper() + text)
            #gtk.threads_leave()            
            line = line + ch + ' '  
        #else:
        #line = cmd.upper() + " "
        left = self.ser[port][0].inWaiting()
        if left > 0:
            line += self.ser[port][0].read(left)   
            if check_mode != "AUTO":
                ###gtk.threads_enter()
                self.insert_into_console(line)
                ###gtk.threads_leave()
            self.set_batching_result(line.split())
        self.ser[port][0].flushInput()
        print "thread batching stopped.\n"

    def plying(self, port=0, method=0):   # 0: line by line 1: Lex-Yacc method    

        print "thread plying starts.."
        self.clear_status()       
        if method == 0:
            for cmd in self.cmds:
                if self.ThreadOfBatch == None or not self.ThreadOfBatch.is_alive():
                    self.ThreadOfBatch = Thread(target=self.batching, args=(port, cmd, "AUTO"))
                    self.ThreadOfBatch.start()
                    time.sleep(0.1)
                    self.ThreadOfBatch.join(1)  # 1) join() only waits for a thread to finish. it won't make executing any thread.
                                                # 2) join(timieout) will stop blocking after timeout, but will not terminate the thread if it is still running.
                    if self.ThreadOfBatch.is_alive():
                        self.batch_is_timeout = 1
                    print 'batching ended'
                else:
                    print "batching is in use"
                if self.get_check_status() != 0:
                    #self.check_status = 2
                    break
                #time.sleep(0.01)
        else:
            prog = basparse.parse(open(self.cmds).read())
            if not prog: 
                self.set_console_text("*.BAS script basparse import error.")
                self.set_check_status(1)
            else:
                try:
                    basinterp.BasicInterpreter(prog, self).run()
                except RuntimeError:
                    self.set_console_text("*.BAS script basinterp error.")
                    self.set_check_status(1)

        CERT_VALUE = datetime.datetime.now()
        CERT_VALUE = CERT_VALUE.strftime("%Y-%m-%d %H:%M:%S")                
        filename = str(self.serial_number) + str(CERT_VALUE)
        filename = re.sub(r'[^a-zA-Z0-9]', '', filename)
        start, end = self.TextBufferOfLog.get_bounds()
        console_log = self.TextBufferOfLog.get_text(start, end)
        
        if self.save_to_log('./certification/', filename, console_log) == 1:
            self.set_console_text("LOG failed.")    
            self.set_check_status_led(1)
        else:
            self.set_check_status_led()

        #gtk.threads_enter()                    
        gobject.idle_add(self.EntryOfSerialNumber.set_text, '')
        #gtk.threads_leave()
        print "thread plying stopped"
        
    def save_to_log(self, directory, filename, logcontent):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)        
            
            logfile = None
            logfile = open(directory + filename + ".log", 'w')
            logfile.write(logcontent)
        except:
            if logfile != None:
                logfile.close()
            return 1
        finally:
            return 0
            logfile.close()
                    
    def get_check_status(self):  
        #self.mutex_of_checkstatus.acquire()  
        status = self.check_status
        #self.mutex_of_checkstatus.release()    
        return status
    
    def set_check_status(self, status):
        #self.mutex_of_checkstatus.acquire()
        self.check_status &= 0x80000000
        self.check_status |= status
       # self.mutex_of_checkstatus.release()
    
    def get_ack_to_plying(self):
        #self.mutex_of_plyack.acquire()
        ack = self.ack_to_plying
        #self.mutex_of_plyack.release()
        return ack
    
    def set_ack_to_plying(self, ack):
        #self.mutex_of_plyack.acquire()
        self.ack_to_plying = ack
        #self.mutex_of_plyack.release()
        
    def clear_status(self):
        self.check_status = 0
        self.set_check_status_led(2)
         
    def set_check_status_led(self, status=None):
        if status == None:
            status = self.get_check_status()
        
        if status == 0:
            color = 'green'
        elif status == 1:
            color = 'red'
        elif status == 2:
            color = 'gray'            
        else:
            color = 'yellow'
        self.ButtonResultByColor.set_color(gtk.gdk.Color(color))
        
    def set_console_text(self, str=None):
        ###gtk.threads_enter()
        if str == "_CLEAR":
            #start, end = self.TextBufferOfLog.get_bounds()
            #gobject.idle_add(self.TextBufferOfLog.delete, start, end)
            self.on_ButtonSend_clicked(0, "_clear")
        elif str == "_CURRENTTIME":
            self.insert_into_console((datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n'))
        elif str == "_ERROR":
            self.set_check_status(1)
        elif str == '_SCAN':
            self.on_ButtonSend_clicked(0, '_scan')
        elif str == "_BARCODE":
            self.serial_number = self.EntryOfSerialNumber.get_text()
            if not self.serial_number.isdigit():
                self.serial_number = "1234567890"
            data_with_2line = ('_BARCODE ' + self.serial_number).split()
            self.set_batching_result(data_with_2line)
        elif str == '_MSP430':
            self.on_ButtonSend_clicked(0, '_msp430')
        else:
            str = str.decode(chardet.detect(str)['encoding'])  # decode() means decode the wanted format to unicode format.
            self.insert_into_console(str + "\n")
        ###gtk.threads_leave()
    
    def insert_into_console(self, str=None):
        if str != None:
            gobject.idle_add(self.TextBufferOfLog.insert_at_cursor, str)
            
    def set_uart_text(self, port, rates, cmd, check_mode):
        try:
            comport = self.ser[port]
        except KeyError:
            gobject.idle_add(self.set_console_text, "The COM port " + port + " is not existed.\n")
            self.set_check_status(2)
            return 1
        
        if comport[0] == None or not comport[0].isOpen():
            self.serial_connect(port, rates)
        elif comport[1] != rates:
            self.serial_close_all()
            self.serial_connect(port, rates)
        
#        if check_mode == "AUTO": # auto check
        if self.ThreadOfBatch == None or not self.ThreadOfBatch.is_alive():
            #self.cmds = [str]
            self.ThreadOfBatch = Thread(target=self.batching, args=(port, cmd, check_mode))
            self.ThreadOfBatch.start()
            time.sleep(0.1)
            self.ThreadOfBatch.join(1) 
            if self.ThreadOfBatch.is_alive():
                self.batch_is_timeout = 1
        else:
            print "thread batch is in use.."
#        else: # manually check
#            self.ser[port][0].write(cmd + "\n")
        return 0
    
    def set_tutorial(self, src):
        src = './tutorials/' + src
        if(os.path.isfile(src)):
            ext = (src.split('.')[1]).upper()
            if ext == "JPG" or ext == "BMP" or ext == "PNG":
                gobject.idle_add(self.ImageOfTutorial.set_from_file, src)
      #  self.ImageOfTutorial.set_from_file("xx.jpg")
    
    def set_instruction(self, words):
        words = words.decode(chardet.detect(words)['encoding'])
        words = words.split('\\n')
        color_list = {'BLACK', 'RED', 'BLUE'}
        font_size = 24
        font_color = 'black'
        display_words = ''
        if len(words) > 1:            
            for word in words:
                if 'FONTCOLOR=' in word:
                    fcolor = word.split('=')[1].upper()
                    if fcolor in color_list:
                        font_color = fcolor
                elif 'FONTSIZE=' in word:
                    fsize = word.split('=')[1]
                    if fsize.isdigit():
                        font_size = fsize
                else:
                    display_words += word + '\n'
        else:
            display_words += words[0]
        gobject.idle_add(self.LabelOfInstruction.set_text, display_words)
        gobject.idle_add(self.LabelOfInstruction.modify_fg, gtk.STATE_NORMAL, gtk.gdk.color_parse(font_color))
        gobject.idle_add(self.LabelOfInstruction.modify_font, pango.FontDescription("sans " + str(font_size)))
    
    def flash_msp430(self, hexfile):
        cmds = ['-eE', '-PV', '-r', '-i', 'ihex', hexfile]
        jtagfile = './msp430-jtag.py'
        if not os.path.isfile(jtagfile):
            jtagfile = './msp430-jtag.pyc'
        self.cmds = ['python', jtagfile, '--time', '-p']
        if os.name == 'posix':
            os.environ['LIBMSPGCC_PATH'] = '/usr/lib'
            self.cmds.append('/dev/ttyACM0')
        else:
            self.cmds.append('TIUSB')
            
        self.cmds += cmds
        
        if os.name == 'posix':
            command = ''
            for cmd in self.cmds:
                command += cmd
                command += ' '
            start_time = time.time()
            child = pexpect.spawn(command)
            result = ''
            while True:
                try:       
                    child.expect('\r')
                    result += child.before
                    #gtk.threads_enter()                    
                    self.insert_into_console(child.before)
                    #gtk.threads_leave()
                except:
                    #gtk.threads_enter()
                    self.insert_into_console("\nTime: " + str(time.time() - start_time) + 's\n')
                    #gtk.threads_leave()
                    break
                time.sleep(0.1)
            
        else:        
            proc = subprocess.Popen(self.cmds, 
                            shell=False, 
                            stderr=subprocess.PIPE)
            ###gtk.threads_enter()
            result = proc.communicate()[1]
            self.insert_into_console(result)
            ###gtk.threads_leave()

        if ('Erase check by file: OK' or 'Programming: OK' or 'Verify by file: OK') not in result:
            #gtk.threads_enter()
            self.insert_into_console("flash failed.\n")
            ###gtk.threads_leave()
            self.set_check_status(1)

        
    def ComboxOfUart_init(self):
        self.ser = {}   #{reference, instance, is_alive}
        ports = sorted(comports())
        
        while self.ComboBoxOfUart.get_active() != -1:
            self.ComboBoxOfUart.remove_text(self.ComboBoxOfUart.get_active())
        
        port_num = 0
        for port, desc, hwid in ports:
            if port.find('ttyACM') == -1:
                #self.ListStoreOfUart.append([port, '115200'])
                self.ListStoreOfUart.append([port, '9600'])
                self.ser[port] = None, 0          
                port_num += 1 
                
        if port_num == 0 :
            self.ComboBoxOfUart.insert_text(0, "NONE")
            
        self.ComboBoxOfUart.set_active(0)
        
    def serial_connect(self, port, rates):
        try: 
            self.ser[port] = serial.Serial(port, rates, timeout=1), rates
        except serial.serialutil.SerialException:
            self.ser[port] = None, 0
            #self.ser_is_alive = 0
            print "serial error"
        else:
            time.sleep(0.3) # under raspberry pi, we need to wait until thread receiving quits successfully.
            if self.ThreadOfReceiving == None or not self.ThreadOfReceiving.is_alive():
                self.ThreadOfReceiving = Thread(target=self.receiving, args=(port, rates,))                  
                self.ThreadOfReceiving.start()
                #self.thread.join()     # this will block current thread (Main)
                time.sleep(0.1) # to make sure the new thread is created successfully.    
    
    def serial_close_all(self):
        for port in self.ser:
            if self.ser[port][0] != None:   # and self.ser[port][0].isOpen():
                self.mutex.acquire()    # to avoid mis-judging in thread receiving - ser.inWaiting()
                self.ser[port][0].close()
                self.ser[port] = None, 0
                self.mutex.release()
                       
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("./glades/calibration.glade")
        builder.connect_signals(self)
        
        self.ButtonResultByColor = builder.get_object("ButtonResultByColor")
        self.ButtonYes = builder.get_object("ButtonYes")
        self.ButtonNo = builder.get_object("ButtonNo")
        self.ButtonPrinting = builder.get_object("ButtonPrinting")
        self.ButtonYes.child.modify_font(pango.FontDescription("sans 48"))
        self.ButtonNo.child.modify_font(pango.FontDescription("sans 48"))
        self.LabelOfInstruction = builder.get_object("LabelOfInstruction")
        self.LabelOfInstruction.modify_font(pango.FontDescription("sans 24"))
    
        self.ListStoreOfUart = builder.get_object("liststore2")
        self.ComboBoxOfUart = builder.get_object("ComboBoxOfUart")
        self.window = builder.get_object("window")
        
    
        self.TextBufferOfLog = builder.get_object("textbuffer1")
        self.EntryOfCommand = builder.get_object("EntryOfCommand")
        self.EntryOfSerialNumber = builder.get_object("EntryOfSerialNumber")
        self.serial_number = 777
        self.ScrolledWindowOfLog = builder.get_object("ScrolledWindowOfLog")
        self.FileChooserButton = builder.get_object("FileChooserButton")
        self.FileChooserButtonOfTestMode = builder.get_object("FileChooserButtonOfTestMode")
        self.FileFilterForView = builder.get_object("filefilter1")
        self.FileFilterForView.add_pattern("*.cali")
        self.FileFilterForView.add_pattern("*.bas")
        
        try: 
            default_script = './scripts/ntc.bas'
            with open("./cali.conf") as file:
                for line in file:
                    val_list = line.split("=") 
                    if val_list[0] == "DEFAULT_SCRIPT":
                        default_script = val_list[1].rstrip()
                        break
        except:
            print "cali.conf open failed."
        if os.path.isfile(default_script):
            self.FileChooserButtonOfTestMode.set_filename(default_script)
            self.FileChooserButtonOfTestMode.set_filename(default_script)
        self.ImageOfTutorial = builder.get_object("ImageOfTutorial") 
        self.FrameOfDebug = builder.get_object("FrameOfDebug")
        
        self.ListOfPrinterSettings = [None]
        # init for multiple threading        
        self.ply_need_start = 0
        self.ply_mode = 0   # 0: line by line 1: yacc mode
        self.ack_to_plying = 1  # 0 ack 1 not ack
        self.batch_is_timeout = 0
        self.check_status = 0   # 1: failed 
                                # 0: success 
                                # 0x8000000x: terminated
        self.ThreadOfReceiving = None    
        self.ThreadOfPly = None 
        self.ThreadOfBatch = None
        self.batching_result = {}
        self.mutex = threading.Lock()
        self.mutex_of_plyack = threading.Lock()
        #self.mutex_of_ply = threading.Lock() 
        self.condition = threading.Condition(threading.Lock())
        self.ComboxOfUart_init()
        
        self.window.show_all()

    def main(self):
        gobject.threads_init()
        gtk.gdk.threads_init()  # use GIL to switch the multi-threads
        
        # NEVER directly operate GTK related resources but use
        # 1) put threads_enter()/leave() to wrap gtk.main() and other gtk_operations in your threads. 
        # 2) use gobject.idle_add(function_of_gtk_operation, counter) in your threads. (Recommended) 
        gtk.threads_enter()      
        gtk.main()               
        gtk.threads_leave()
        
if __name__ == "__main__":
    cali = CaliTest()
    cali.main()
    
