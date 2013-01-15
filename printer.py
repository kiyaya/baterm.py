#-*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import cairo, pango

class GtkPrinter:
    
    #def end_printer(self, operation=None, context=None, user_param1=None):
    #    print "end printer"
        
    def __init__(self, printer_settings, tester, sn):
        self.printer = gtk.PrintOperation()
        self.settings = printer_settings
        self.tester = tester
        self.sn = sn
                
    def run(self, mode="setup"):    
        if mode == "setup":
            result = self.printer.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, None)
            if result == gtk.PRINT_OPERATION_RESULT_APPLY:
                self.settings = self.printer.get_print_settings()
        else:
            self.printer.set_n_pages(1)
            self.printer.connect("draw-page", self.draw_certification) 
            #self.printer.connect("end-print", self.end_printer)

            if self.settings == None:
                result = self.printer.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, None)
                if result == gtk.PRINT_OPERATION_RESULT_APPLY:
                    self.settings = self.printer.get_print_settings()
            else:
                self.printer.set_print_settings(self.settings)   
                self.printer.run(gtk.PRINT_OPERATION_ACTION_PRINT, None)

        return self.settings


    def draw_certification(self, operation=None, context=None, page_nr=None):
        CERT_LEFT_CORNER_X = context.get_width() / 20
        CERT_LEFT_CORNER_Y = context.get_height() / 30
        CERT_FONT_SIZE_OF_TITLE = 0.043 * context.get_width()
        CERT_FONT_SIZE_OF_ITEM = 0.8 * CERT_FONT_SIZE_OF_TITLE
        CERT_FONT_SIZE_OF_ITEM_DATA = 0.8 * CERT_FONT_SIZE_OF_ITEM
        CERT_LINE_NUMBER = 0
        
        self.cairo_context = context.get_cairo_context()
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_ITEM_DATA)
        # draw a rectangle framework
        self.cairo_context.set_source_rgb(0, 0, 0)
        self.cairo_context.rectangle(CERT_LEFT_CORNER_X, 
                     CERT_LEFT_CORNER_Y, 
                     context.get_width() - 2 * CERT_LEFT_CORNER_X, 
                     context.get_height() - 2 * CERT_LEFT_CORNER_Y)
        self.cairo_context.stroke()

        # draw the title
        CERT_LINE_NUMBER += 3
        CERT_TITLE = "CERTIFICATE OF ANALYSIS"
        self.cairo_context.set_source_rgb(0, 0, 0)
        self.cairo_context.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_TITLE)
        x_bearing, y_bearing, width, height = self.cairo_context.text_extents(CERT_TITLE)[:4]
        self.cairo_context.move_to(context.get_width() / 2 + 0.5 - width / 2 - x_bearing, CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER + 0.5 - height / 2 - y_bearing)
        self.cairo_context.show_text(CERT_TITLE)
        self.cairo_context.select_font_face("", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        
        # draw the model name
        CERT_LINE_NUMBER += 2
        CERT_VALUE = "LAVIDA 777"
        CERT_TITLE = "Model Name:"
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_ITEM)  
        x_bearing, y_bearing, width, height = self.cairo_context.text_extents(CERT_TITLE)[:4]   
        self.cairo_context.move_to(context.get_width() / 2 - width - CERT_LEFT_CORNER_X, CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER)   
        self.cairo_context.show_text(CERT_TITLE)
        x, y = self.cairo_context.get_current_point()
        self.print_with_frame(start_x = context.get_width() / 2, start_y = y, content = CERT_VALUE)
        # draw the serial number
        CERT_LINE_NUMBER += 1
        CERT_VALUE = self.sn
        CERT_TITLE = "Serial Number:"
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_ITEM)  
        x_bearing, y_bearing, width, height = self.cairo_context.text_extents(CERT_TITLE)[:4]   
        self.cairo_context.move_to(context.get_width() / 2 - width - CERT_LEFT_CORNER_X, CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER)   
        self.cairo_context.show_text(CERT_TITLE)
        x, y = self.cairo_context.get_current_point()
        x = context.get_width() / 2
        self.print_with_frame(start_x = x, start_y = y, content = CERT_VALUE)
        
        # draw the date
        CERT_LINE_NUMBER += 1
        import datetime
        CERT_VALUE = datetime.datetime.now()
        CERT_VALUE = CERT_VALUE.strftime("%Y-%m-%d %H:%M:%S")
        CERT_TITLE = "Date of the analyse:"
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_ITEM)    
        x_bearing, y_bearing, width, height = self.cairo_context.text_extents(CERT_TITLE)[:4]  
        self.cairo_context.move_to(context.get_width() / 2 - width - CERT_LEFT_CORNER_X, CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER)    
        self.cairo_context.show_text(CERT_TITLE)
        x, y = self.cairo_context.get_current_point()
        x = context.get_width() / 2
        self.print_with_frame(start_x = x, start_y = y, content = CERT_VALUE)
        
        # draw the voltage table
        CERT_LINE_NUMBER += 2
        CERT_VOLTAGE  = (   ("Voltage",     "±1mV"),
                            ("-5000mV",     "Pass"),
                            ("-4000mV",     "Pass"),
                            ("-3000mV",     "Pass"),
                            ("-2000mV",     "Pass"),
                            ("-1000mV",     "Pass"),
                            ("0mV",         "Pass"),
                            ("+1000mV",     "Pass"),
                            ("+2000mV",     "Pass"),      
                            ("+3000mV",     "Pass"),     
                            ("+4000mV",     "Pass"),     
                            ("+5000mV",     "Pass") )        
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_ITEM_DATA)
        self.print_table_2(start_x = context.get_width() / 2 - context.get_width() / 3 - CERT_LEFT_CORNER_X / 2, 
                           start_y = CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER, 
                           table_list = CERT_VOLTAGE, 
                           table_width = context.get_width() / 3)

        # draw the vertical line
        self.cairo_context.move_to(context.get_width() / 2, CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER - self.get_height_of_char("X"))
        self.cairo_context.line_to(context.get_width() / 2, 
                                   CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER + self.get_height_of_char("X") * 1.5 * (len(CERT_VOLTAGE) - 1) )
        self.cairo_context.stroke()
        
        # draw the temperature table
        CERT_TEMPERATURE = (    ("Temp", "±0.1deg"),
                                ("-40deg",     "Pass"),
                                ("-30deg",     "Pass"),
                                ("-20deg",     "Pass"),
                                ("-10deg",     "Pass"),
                                ("0deg",       "Pass"),
                                ("10deg",      "Pass"),
                                ("+20deg",     "Pass"),
                                ("+30deg",     "Pass"),      
                                ("+40deg",     "Pass") )    
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_ITEM_DATA)
        self.print_table_2(start_x = context.get_width() / 2 + CERT_LEFT_CORNER_X / 2, 
                           start_y = CERT_LEFT_CORNER_Y * CERT_LINE_NUMBER, 
                           table_list = CERT_TEMPERATURE, 
                           table_width = context.get_width() / 3)
         
                
        # draw the tester
        CERT_NAME = "Tester: "
        CERT_NAME_VALUE = self.tester
        self.cairo_context.move_to(CERT_LEFT_CORNER_X * 2, context.get_height() - 2 * CERT_LEFT_CORNER_Y)
        self.cairo_context.set_font_size(CERT_FONT_SIZE_OF_ITEM)        
        self.cairo_context.show_text(CERT_NAME)     
        x, y = self.cairo_context.get_current_point()   
        self.print_with_underline(start_x = x, start_y = y, content = CERT_NAME_VALUE)
        
    def get_width_of_char(self, chars="X"):
        x_bearing, y_bearing, width_of_char, height = self.cairo_context.text_extents(chars)[:4]
        return width_of_char
    def get_height_of_char(self, chars="X"):
        x_bearing, y_bearing, width_of_char, height = self.cairo_context.text_extents(chars)[:4]
        return height
            
    def print_at_align(self, start_x, start_y, content, width_of_area, alignment):
        x_bearing, y_bearing, width, height = self.cairo_context.text_extents(content)[:4]
        if alignment == "right":
            x = start_x + width_of_area - width - self.get_width_of_char("XX")
        else:   # defualt: center
            x = start_x + (width_of_area - width) / 2
        y = start_y        
        self.cairo_context.move_to(x, y)
        self.cairo_context.show_text(content)
    
    def print_table_2(self, start_x, start_y, table_list, table_width):
        if len(table_list) > 0 :           
            col_width = table_width / len(table_list[0]) 
            # print title
            self.cairo_context.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            self.print_at_align(start_x, start_y, table_list[0][0], col_width, "center")
            self.print_at_align(start_x + table_width / 2, start_y, table_list[0][1], col_width, "center")
            # print rows
            
            if len(table_list) > 1:
                self.cairo_context.select_font_face("", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                i = 0
                for rows in table_list:
                    if i > 0:   # print the data
                        j = 0
                        align = "right"
                        for col in rows:
                            if j == 1:
                                align = "center"
                            self.print_at_align(start_x + j * col_width, 
                                                start_y + i * self.get_height_of_char("X") * 2, 
                                                content = col, 
                                                width_of_area = col_width, 
                                                alignment=align)
                            j += 1
                    i += 1
            self.cairo_context.select_font_face("", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    def print_with_frame(self, start_x, start_y, content):
        x_bearing, y_bearing, width, height = self.cairo_context.text_extents(content)[:4]
        self.cairo_context.rectangle(start_x, 
                                     start_y - self.get_height_of_char("X") * 1.3, 
                                     width + self.get_width_of_char("XX"), 
                                     self.get_height_of_char("X") * 1.6)
        self.cairo_context.stroke()        
        self.cairo_context.move_to(start_x + self.get_width_of_char("X"), start_y)
        self.cairo_context.show_text(content)
    
    def print_with_underline(self, start_x, start_y, content):
        x_bearing, y_bearing, width, height = self.cairo_context.text_extents(content)[:4]
        self.cairo_context.move_to(start_x, start_y + self.get_height_of_char("X") / 4)
        self.cairo_context.line_to(start_x + width + self.get_width_of_char("XX"), start_y + self.get_height_of_char("X") / 4)
        self.cairo_context.stroke()
        self.cairo_context.move_to(start_x + self.get_width_of_char("XX") / 2, start_y)
        self.cairo_context.show_text(content)
    
    