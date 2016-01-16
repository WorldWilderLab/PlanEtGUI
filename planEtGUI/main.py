import os
import time
import ConfigParser
import wx
import wx.lib.scrolledpanel
import wxmplot
import csv
import numpy as np

import log

PLANET_BUTTON_LOGS = wx.NewId()
PLANET_BUTTON_GRAPHS = wx.NewId()
PLANET_BUTTON_SETTINGS = wx.NewId()
PLANET_BUTTON_HOME = wx.NewId()
PLANET_BUTTON_START_LOG = wx.NewId()
PLANET_BUTTON_APPLY_SETTINGS = wx.NewId()
PLANET_SEPARATOR_LINE_THICKNESS = 2
PLANET_BORDER = 20
PLANET_BACKGROUND_COLOR = (255, 255, 255)
PLANET_INPUT_BORDER_COLOR = (99, 165, 50)


class TextControl(wx.Panel):
    """
    A wx.TextCtrl object with a customizable border
    """

    def __init__(self, parent, text_size, border_size, color):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(color)
        self.ver_sizer = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl = wx.TextCtrl(self, -1, size=(text_size, -1), style=wx.NO_BORDER)
        self.ver_sizer.Add(self.text_ctrl, 0, wx.ALL, border_size)
        self.SetSizer(self.ver_sizer)
        self.Layout()

    def set_value(self, val):
        self.text_ctrl.SetValue(val)
        self.Layout()

    def get_value(self):
        return self.text_ctrl.GetValue()

    def clear(self):
        self.text_ctrl.Clear()


class FileItem:
    def __init__(self, title, date_created, path):
        self.title = title
        self.date_created = date_created
        self.path = path


class DropDownMenu(wx.Panel):
    def __init__(self, parent, path):
        wx.Panel.__init__(self, parent, size=wx.DefaultSize)
        self.SetBackgroundColour(PLANET_BACKGROUND_COLOR)
        self.ver_sizer = wx.BoxSizer(wx.VERTICAL)

        self.path = path

        empty_choices = []
        self.drop_down_menu = wx.Choice(self, size=wx.DefaultSize, choices=empty_choices)
        self.drop_down_menu.SetBackgroundColour(PLANET_BACKGROUND_COLOR)

        self.update_items()

        self.ver_sizer.Add(self.drop_down_menu, 0, wx.ALL, 0)
        self.SetSizer(self.ver_sizer)
        self.Layout()

    def update_items(self):
        self.drop_down_menu.Clear()
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if f.endswith('.csv'):
                    title = f[0:len(f) - 4]
                    date = 0
                    path = os.path.join(root, f)
                    item = FileItem(title, date, path)
                    self.drop_down_menu.Append(item.title, item)
        self.Layout()

    def set_path(self, path):
        self.path = path


class HomePanel(wx.Panel):
    """panel that shows on start up when no button is selected"""

    def __init__(self, parent):
        # TODO: create home panel
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(PLANET_BACKGROUND_COLOR)


class LogsPanel(wx.lib.scrolledpanel.ScrolledPanel):
    """panel that add and shows all active or paused logs"""

    def __init__(self, parent, size):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.SetBackgroundColour(PLANET_BACKGROUND_COLOR)

        self.logs = []
        self.titles = None
        self.log_entries = []

        self.ver_sizer = wx.BoxSizer(wx.VERTICAL)
        self.hor_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # page title
        self.page_title = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/TITLE_start_new_log.png'))

        # page title separator
        self.page_title_separator = wx.Panel(self, size=(size[0], 10))
        self.page_title_separator.SetBackgroundColour(PLANET_BACKGROUND_COLOR)

        # add new log
        self.new_log_flex_grid = wx.FlexGridSizer(4, 3, 5, 5)
        self.font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.st_unique_id = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/unique_id_sub.png'))
        self.st_host = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/host_sub.png'))
        # st_title misses an image for it
        self.st_title = wx.StaticText(self, label='TITLE')
        self.st_title.SetFont(self.font)
        self.st_log_folder = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/log_folder_sub.png'))
        self.title = TextControl(self, 300, 1, PLANET_INPUT_BORDER_COLOR)
        self.unique_id = TextControl(self, 300, 1, PLANET_INPUT_BORDER_COLOR)
        self.host = TextControl(self, 300, 1, PLANET_INPUT_BORDER_COLOR)
        self.log_folder = TextControl(self, 300, 1, PLANET_INPUT_BORDER_COLOR)
        self.expl_font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.st_unique_id_expl = wx.StaticText(self, label='unique id creates blah blah blah')
        self.st_unique_id_expl.SetFont(self.expl_font)
        self.st_host_expl = wx.StaticText(self, label='make sure you type a right host')
        self.st_host_expl.SetFont(self.expl_font)
        self.st_title_expl = wx.StaticText(self, label='give a name to your plant')
        self.st_title_expl.SetFont(self.expl_font)
        self.st_log_folder_expl = wx.StaticText(self, label='choose a folder in which you want to store data')
        self.st_log_folder_expl.SetFont(self.expl_font)
        self.new_log_flex_grid.AddMany([(self.st_title, 0, wx.CENTER), self.title, (self.st_title_expl, 0, wx.CENTER),
                                        (self.st_unique_id, 0, wx.CENTER), self.unique_id, (self.st_unique_id_expl, 0, wx.CENTER),
                                        (self.st_host, 0, wx.CENTER), self.host, (self.st_host_expl, 0, wx.CENTER),
                                        (self.st_log_folder, 0, wx.CENTER), self.log_folder, (self.st_log_folder_expl, 0, wx.CENTER)])

        # start button
        self.bmp = wx.Image(basepath + '/data/bttn_start_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.selected_bmp = wx.Image(basepath + '/data/bttn_start_on_over.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.btn_start = wx.BitmapButton(self, PLANET_BUTTON_START_LOG, self.bmp, style=wx.NO_BORDER)
        self.btn_start.SetBitmapFocus(self.bmp)
        self.btn_start.SetBitmapSelected(self.selected_bmp)
        self.btn_start.SetBitmapHover(self.bmp)
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start_log, id=PLANET_BUTTON_START_LOG)

        # active logs title separator
        self.active_logs_title_separator = wx.Panel(self, size=(size[0], 10))
        self.active_logs_title_separator.SetBackgroundColour(PLANET_BACKGROUND_COLOR)

        # active logs title
        self.active_logs_title = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/TITLE_active_logs.png'))

        # active logs
        self.active_log_flex_grid = wx.FlexGridSizer(0, 9, 5, 15)
        self.active_log_flex_grid.AddGrowableCol(6, 1)

        # active log stop and pause button bitmaps
        self.log_button_bmps = [wx.Image(basepath + '/data/bttn_end_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                                wx.Image(basepath + '/data/bttn_pause_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                                wx.Image(basepath + '/data/bttn_pause_on_over.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()]

        # add all elements to the vertical sizer
        self.ver_sizer.Add(self.page_title, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM | wx.ALIGN_LEFT, PLANET_BORDER)
        self.ver_sizer.Add(self.page_title_separator, 0, wx.EXPAND)
        self.ver_sizer.Add(self.new_log_flex_grid, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, PLANET_BORDER)
        self.ver_sizer.Add(self.btn_start, 0, wx.ALIGN_RIGHT | wx.RIGHT, PLANET_BORDER)
        self.ver_sizer.Add(self.active_logs_title_separator, 0, wx.EXPAND)
        self.ver_sizer.Add(self.active_logs_title, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_LEFT, PLANET_BORDER)
        self.ver_sizer.Add(self.active_log_flex_grid, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, PLANET_BORDER)
        self.SetSizer(self.ver_sizer)

        # hide the active logs title
        self.active_logs_title.Hide()

        # self.Fit()
        self.Layout()
        self.SetupScrolling(scroll_x=False)

    def on_start_log(self, evt):
        topic = '/plant/' + str(self.unique_id.get_value()) + '/#'
        host = self.host.get_value()
        path = self.log_folder.get_value()
        title = self.title.get_value()

        new_log = log.Log(topic, host, path, title, wx.NewId(), wx.NewId())

        # TODO: somehow simplify by creating a function that creates all StaticText and Button objects
        if new_log.is_connected:
            new_log.log_start()
            if len(self.logs) < 1:
                # show the active logs title
                self.active_logs_title.Show()

                # add titles to active_log_flex_grid
                title_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD)
                self.titles = [wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/table_title.png')),
                               wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/table_topic.png')),
                               wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/table_host.png')),
                               wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/table_start_time.png')),
                               wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/table_start_date.png')),
                               wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/table_path.png'))]
                for i in range(len(self.titles)):
                    self.titles[i].SetFont(title_font)

                # add values to active_log_flex_grid
                grid_row = [wx.StaticText(self, label=title), wx.StaticText(self, label=topic),
                            wx.StaticText(self, label=host), wx.StaticText(self, label=self.get_time()),
                            wx.StaticText(self, label=self.get_date()), wx.StaticText(self, label=path),
                            wx.BitmapButton(self, new_log.id_pause, self.log_button_bmps[1], style=wx.NO_BORDER),
                            wx.BitmapButton(self, new_log.id_stop, self.log_button_bmps[0], style=wx.NO_BORDER)]
                grid_row[6].Bind(wx.EVT_BUTTON, self.on_pause_log, id=new_log.id_pause)
                grid_row[7].Bind(wx.EVT_BUTTON, self.on_stop_log, id=new_log.id_stop)
                self.log_entries.append(grid_row)
                self.active_log_flex_grid.AddMany([(self.titles[0], 0, wx.BOTTOM), (self.titles[1], 0, wx.BOTTOM),
                                                   (self.titles[2], 0, wx.BOTTOM), (self.titles[3], 0, wx.BOTTOM),
                                                   (self.titles[4], 0, wx.BOTTOM), (self.titles[5], 0, wx.BOTTOM)])
                self.active_log_flex_grid.AddStretchSpacer()
                self.active_log_flex_grid.AddStretchSpacer()
                self.active_log_flex_grid.AddStretchSpacer()
                self.active_log_flex_grid.AddMany([(grid_row[0], 0, wx.CENTER), (grid_row[1], 0, wx.CENTER),
                                                   (grid_row[2], 0, wx.CENTER), (grid_row[3], 0, wx.CENTER),
                                                   (grid_row[4], 0, wx.CENTER), (grid_row[5], 0, wx.CENTER)])
                self.active_log_flex_grid.AddStretchSpacer()
                self.active_log_flex_grid.AddMany([grid_row[6], grid_row[7]])
                self.logs.append(new_log)
            else:
                # add values to active_log_flex_grid
                grid_row = [wx.StaticText(self, label=title), wx.StaticText(self, label=topic),
                            wx.StaticText(self, label=host), wx.StaticText(self, label=self.get_time()),
                            wx.StaticText(self, label=self.get_date()), wx.StaticText(self, label=path),
                            wx.BitmapButton(self, new_log.id_pause, self.log_button_bmps[1], style=wx.NO_BORDER),
                            wx.BitmapButton(self, new_log.id_stop, self.log_button_bmps[0], style=wx.NO_BORDER)]
                grid_row[6].Bind(wx.EVT_BUTTON, self.on_pause_log, id=new_log.id_pause)
                grid_row[7].Bind(wx.EVT_BUTTON, self.on_stop_log, id=new_log.id_stop)
                self.log_entries.append(grid_row)
                self.active_log_flex_grid.AddMany([(grid_row[0], 0, wx.CENTER), (grid_row[1], 0, wx.CENTER),
                                                   (grid_row[2], 0, wx.CENTER), (grid_row[3], 0, wx.CENTER),
                                                   (grid_row[4], 0, wx.CENTER), (grid_row[5], 0, wx.CENTER)])
                self.active_log_flex_grid.AddStretchSpacer()
                self.active_log_flex_grid.AddMany([grid_row[6], grid_row[7]])
                self.logs.append(new_log)
        else:
            # TODO: better and more precise error handling is need here!
            if host == '' or topic == '/plant//probe/' or path == '' or title == '':
                wx.MessageBox('The form is incomplete!\nPlease fill all fields', 'Start Log',
                              wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox('Connection on ' + host + ' was refused\nPlease enter a valid IP address', 'Start Log',
                              wx.OK | wx.ICON_INFORMATION)

        # clear the TextCtrl objects
        self.title.clear()
        self.unique_id.clear()
        # self.probe.clear()
        self.host.clear()
        self.log_folder.clear()

        self.update()

        self.Layout()
        self.SetupScrolling(scroll_x=False)

    def on_pause_log(self, evt):
        lid = evt.GetId()
        # switch button image and pause log
        for i in range(len(self.log_entries)):
            if lid == self.log_entries[i][6].GetId():
                if self.logs[i].is_paused:
                    self.log_entries[i][6].SetBitmapLabel(self.log_button_bmps[1])
                    self.logs[i].log_start()
                    self.Layout()
                    self.SetupScrolling(scroll_x=False)
                    break
                else:
                    self.log_entries[i][6].SetBitmapLabel(self.log_button_bmps[2])
                    self.logs[i].log_pause()
                    self.Layout()
                    self.SetupScrolling(scroll_x=False)
                    break

    def on_stop_log(self, evt):
        lid = evt.GetId()

        for i in range(len(self.logs)):
            if lid == self.logs[i].id_stop:
                # stop the log
                self.logs[i].log_stop()

                # remove the log from the active log view
                cell = 9 * (i + 1)
                index = 8
                while index >= 0:
                    self.active_log_flex_grid.Remove(index+cell)
                    index -= 1

                # Destroy the text and button resources
                for j in range(len(self.log_entries[i])):
                    self.log_entries[i][j].Destroy()

                # delete the log
                del self.logs[i]
                del self.log_entries[i]

                # check if there any active logs left, if there aren't, remove the headers from the view
                if len(self.logs) < 1:
                    # hide active logs title
                    self.active_logs_title.Hide()

                    cell = 0
                    index = 8
                    while index >= 0:
                        self.active_log_flex_grid.Remove(index+cell)
                        if index < 6:
                            self.titles[index].Destroy()
                        index -= 1
                break
        self.Layout()
        self.SetupScrolling(scroll_x=False)

    def update(self):
        self.host.set_value(config_manager.get_default_host())
        self.log_folder.set_value(config_manager.get_default_path())
        self.Layout()

    @staticmethod
    def get_time():
        return time.strftime("%H:%M:%S", time.localtime())

    @staticmethod
    def get_date():
        return time.strftime("%d %b %Y", time.localtime())


class GraphsPanel(wx.Panel):
    """panel that allows you to browse all archived logs and make graphs out of them"""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(PLANET_BACKGROUND_COLOR)
        self.ver_sizer = wx.BoxSizer(wx.VERTICAL)
        self.hor_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # page title
        self.page_title = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/TITLE_plotandgraph.png'))

        # file dropdown menu
        self.drop_down_menu = DropDownMenu(self, config_manager.get_default_path())
        self.drop_down_menu.drop_down_menu.Bind(wx.EVT_CHOICE, self.on_select_plot)

        # plot button
        self.bmp = wx.Image(basepath + '/data/bttn_plot_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.selected_bmp = wx.Image(basepath + '/data/bttn_plot_on.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.btn_plot = wx.BitmapButton(self, PLANET_BUTTON_START_LOG, self.bmp, style=wx.NO_BORDER)
        self.btn_plot.SetBitmapFocus(self.bmp)
        self.btn_plot.SetBitmapSelected(self.selected_bmp)
        self.btn_plot.SetBitmapHover(self.bmp)
        self.btn_plot.Bind(wx.EVT_BUTTON, self.on_plot_log)

        # flex grid sizer for top menu
        self.top_flex_grid = wx.FlexGridSizer(1, 3, 5, 0)
        self.top_flex_grid.AddGrowableCol(0, 1)
        self.top_flex_grid.AddGrowableCol(2, 1)
        self.top_flex_grid.AddMany([(self.page_title, 0, wx.CENTER),
                                    (self.drop_down_menu, 0, wx.CENTER),
                                    (self.btn_plot, 0, wx.CENTER | wx.ALIGN_RIGHT)])

        # plot panel
        # TODO: check if by suppliying the plot object with a callbakc function we can get rid of the printing of coordinates to the console
        self.item = None
        self.x_data = None
        self.y_data = None
        self.trace_names = None
        self.plot = wxmplot.PlotPanel(self)
        self.plot.Hide()

        # select trace image
        self.sel_trace_img = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/please_select.png'))
        self.sel_trace_img.Hide()

        # trace listbox
        self.trace_listbox = wx.ListBox(self, size=(-1, -1), style=wx.LB_EXTENDED)
        self.trace_listbox.Hide()
        self.trace_listbox.Bind(wx.EVT_LISTBOX, self.on_trace_select)

        # add objects to horizontal sizer
        self.hor_sizer.Add(self.trace_listbox, 0, wx.EXPAND | wx.BOTTOM, PLANET_BORDER)
        self.hor_sizer.Add(self.plot, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, PLANET_BORDER)

        # add objects to vertical sizer
        self.ver_sizer.Add(self.top_flex_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, PLANET_BORDER)
        self.ver_sizer.Add(self.sel_trace_img, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_LEFT, PLANET_BORDER)
        self.ver_sizer.Add(self.hor_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, PLANET_BORDER)

        self.SetSizer(self.ver_sizer)
        self.Layout()

    @staticmethod
    def _open_log(path):
        """ opens a log file and returns a list of traces and trace names """

        with open(path, 'rb') as n:
            reader = csv.reader(n)
            x_data = []
            y_data = []
            topic_data = []
            for row in reader:
                if row[3].endswith('version') or row[3].endswith('ip') or row[3].endswith('status'):
                    pass
                else:
                    x_data.append(float(row[0]))
                    topic_data.append(row[3])
                    y_data.append(float(row[4]))

        unique_topics = set(topic_data)
        unique_topics = list(unique_topics)
        y_data_sorted = []
        x_data_sorted = []

        for topic in unique_topics:
            indices = [i for i, x in enumerate(topic_data) if x == topic]
            y_data_np = np.array(y_data)
            x_data_np = np.array(x_data)
            y_data_np = list(y_data_np[indices])
            x_data_np = list(x_data_np[indices])
            y_data_sorted.append(y_data_np)
            x_data_sorted.append(x_data_np)

        return x_data_sorted, y_data_sorted, unique_topics

    def _get_x_origin(self):
        """returns the x-origin of all data"""

        origin = min(self.x_data[0])

        for x in self.x_data:
            if min(x) < origin:
                origin = min(x)

        return origin

    def _plot_log(self, trace_ids):
        if len(self.x_data) > 0:
            self.plot.clear()
            x_origin = self._get_x_origin()
            for trace_id in trace_ids:
                x_array = np.array(self.x_data[trace_id])
                y_array = np.array(self.y_data[trace_id])
                if trace_ids.index(trace_id) == 0:
                    self.plot.plot(x_array - x_origin, y_array,
                                   title=self.item.title,
                                   bgcolor=(1, 1, 1),
                                   framecolor=(1, 1, 1))
                else:
                    self.plot.oplot(x_array - x_origin, y_array,
                                    title=self.item.title,
                                    bgcolor=(1, 1, 1),
                                    framecolor=(1, 1, 1))
        else:
            self.plot.clear()

        self.Layout()

    def on_trace_select(self, event):
        trace_ids =  self.trace_listbox.GetSelections()
        self._plot_log(trace_ids)

    def on_select_plot(self, event):
        self.item = self.drop_down_menu.drop_down_menu.GetClientData(self.drop_down_menu.drop_down_menu.GetSelection())

    def on_plot_log(self, event):
        self.x_data, self.y_data, self.trace_names = self._open_log(self.item.path)

        self.trace_listbox.Clear()
        for trace_name in self.trace_names:
            self.trace_listbox.Append(trace_name)

        self.trace_listbox.SetSelection(0)

        self._plot_log([0])

        self.trace_listbox.Show()
        self.sel_trace_img.Show()
        self.plot.Show()
        self.Layout()


class SettingsPanel(wx.Panel):
    """settings panel"""

    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(PLANET_BACKGROUND_COLOR)
        self.ver_sizer = wx.BoxSizer(wx.VERTICAL)
        # self.hor_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # page title
        self.page_title = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/title_settings.png'))

        # page title separator
        self.page_title_separator = wx.Panel(self, size=(size[0], 10))
        self.page_title_separator.SetBackgroundColour(PLANET_BACKGROUND_COLOR)

        # add settings options to flex grid
        self.settings_flex_grid = wx.FlexGridSizer(2, 2, 5, 5)
        self.title_font = wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.titles = [wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/default_host_sub.png')),
                       wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/default_folder_sub.png'))]
        self.text_ctrls = [TextControl(self, 300, 1, PLANET_INPUT_BORDER_COLOR),
                           TextControl(self, 300, 1, PLANET_INPUT_BORDER_COLOR)]
        for i in range(len(self.titles)):
            self.titles[i].SetFont(self.title_font)
            self.settings_flex_grid.AddMany([(self.titles[i]), (self.text_ctrls[i])])

        # apply button
        self.bmp = wx.Image(basepath + '/data/bttn_apply_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.selected_bmp = wx.Image(basepath + '/data/bttn_apply_on_over.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.btn_apply = wx.BitmapButton(self, PLANET_BUTTON_APPLY_SETTINGS, self.bmp, style=wx.NO_BORDER)
        self.btn_apply.SetBitmapFocus(self.bmp)
        self.btn_apply.SetBitmapSelected(self.selected_bmp)
        self.btn_apply.SetBitmapHover(self.bmp)

        self.btn_apply.Bind(wx.EVT_BUTTON, self.on_apply, id=PLANET_BUTTON_APPLY_SETTINGS)

        # apply confirmation
        self.apply_confirm_img = wx.StaticBitmap(self, bitmap=wx.Bitmap(basepath + '/data/apply_confirmation_info.png'))
        self.apply_confirm_img.Hide()

        # add objects to horizontal sizer
        self.flex_sizer = wx.FlexGridSizer(1, 2, 0, 0)
        self.flex_sizer.AddGrowableCol(0, 1)
        self.flex_sizer.AddGrowableCol(1, 1)
        self.flex_sizer.Add(self.settings_flex_grid, 0, wx.ALIGN_LEFT | wx.EXPAND)
        self.flex_sizer.Add(self.btn_apply, 0, wx.ALIGN_RIGHT)

        # add all object to the vertical sizer
        self.ver_sizer.Add(self.page_title, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM | wx.ALIGN_LEFT, PLANET_BORDER)
        self.ver_sizer.Add(self.page_title_separator, 0, wx.EXPAND)
        self.ver_sizer.Add(self.flex_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, PLANET_BORDER)
        self.ver_sizer.Add(self.apply_confirm_img, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, PLANET_BORDER)

        self.SetSizer(self.ver_sizer)
        self.Layout()

    def update(self):
        self.text_ctrls[0].set_value(config_manager.get_default_host())
        self.text_ctrls[1].set_value(config_manager.get_default_path())
        self.apply_confirm_img.Hide()
        self.Layout()

    def on_apply(self, evt):
        bid = evt.GetId()

        if bid == PLANET_BUTTON_APPLY_SETTINGS:
            config_manager.set_default_host(self.text_ctrls[0].get_value())
            config_manager.set_default_path(self.text_ctrls[1].get_value())

            self.apply_confirm_img.Show()
            self.Layout()


class MainFrame(wx.Frame):
    """entry window for planet gui"""

    def __init__(self, title, size, menu_height):
        wx.Frame.__init__(self, None, title=title, size=size)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        self.ver_sizer = wx.BoxSizer(wx.VERTICAL)
        self.pid = PLANET_BUTTON_HOME

        # the menu panel
        self.menu_panel = wx.Panel(self, size=(size[0], menu_height))
        self.menu_panel.SetBackgroundColour(PLANET_BACKGROUND_COLOR)
        self.hor_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # the logo
        self.logo = wx.StaticBitmap(self.menu_panel, bitmap=wx.Bitmap(basepath + '/data/planEt_logo.png'))
        self.hor_sizer.Add(self.logo, 1, wx.ALL | wx.ALIGN_LEFT, 15)

        # the buttons
        self.hor_menu_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmaps = [wx.Image(basepath + '/data/newlog_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                        wx.Image(basepath + '/data/newlog_on_over.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                        wx.Image(basepath + '/data/logsandgraphs_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                        wx.Image(basepath + '/data/logsandgraphs_on_over.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                        wx.Image(basepath + '/data/settings_off.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                        wx.Image(basepath + '/data/settings_on_over.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()]
        self.buttons = [wx.BitmapButton(self.menu_panel, PLANET_BUTTON_LOGS, self.bitmaps[0], style=wx.NO_BORDER),
                        wx.BitmapButton(self.menu_panel, PLANET_BUTTON_GRAPHS, self.bitmaps[2], style=wx.NO_BORDER),
                        wx.BitmapButton(self.menu_panel, PLANET_BUTTON_SETTINGS, self.bitmaps[4], style=wx.NO_BORDER)]
        self.buttons[0].Bind(wx.EVT_BUTTON, self.on_switch_panel, id=PLANET_BUTTON_LOGS)
        self.buttons[1].Bind(wx.EVT_BUTTON, self.on_switch_panel, id=PLANET_BUTTON_GRAPHS)
        self.buttons[2].Bind(wx.EVT_BUTTON, self.on_switch_panel, id=PLANET_BUTTON_SETTINGS)
        self.hor_menu_sizer.Add(self.buttons[0], 0, wx.RIGHT, PLANET_BORDER)
        self.hor_menu_sizer.Add(self.buttons[1], 0, wx.RIGHT, PLANET_BORDER)
        self.hor_menu_sizer.Add(self.buttons[2], 0, wx.RIGHT, PLANET_BORDER)
        self.hor_sizer.Add(self.hor_menu_sizer, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT | wx.CENTER, PLANET_BORDER)
        self.menu_panel.SetSizer(self.hor_sizer)

        # the home panel
        self.home_panel = HomePanel(self)

        # the logs panel
        self.logs_panel = LogsPanel(self, size)
        self.logs_panel.Hide()

        # the graphs panel
        self.graphs_panel = GraphsPanel(self)
        self.graphs_panel.Hide()

        # the settings panel
        self.settings_panel = SettingsPanel(self, size)
        self.settings_panel.Hide()

        # the separator line
        self.line = wx.Panel(self, size=(size[0], PLANET_SEPARATOR_LINE_THICKNESS))
        self.line.SetBackgroundColour((0, 0, 0))

        # add all panels to the vertical sizer
        self.ver_sizer.Add(self.menu_panel, 0, wx.EXPAND)
        self.ver_sizer.Add(self.line, 0, wx.EXPAND)
        self.ver_sizer.Add(self.home_panel, 1, wx.EXPAND)
        self.ver_sizer.Add(self.logs_panel, 1, wx.EXPAND)
        self.ver_sizer.Add(self.graphs_panel, 1, wx.EXPAND)
        self.ver_sizer.Add(self.settings_panel, 1, wx.EXPAND)
        self.SetSizer(self.ver_sizer)
        self.Layout()

    def on_switch_panel(self, evt):
        """callback function that switched between content panels
        :param evt: event
        """
        self.pid = evt.GetId()

        # change button state bitmaps and load panels
        if self.pid == PLANET_BUTTON_LOGS:
            self.buttons[0].SetBitmapLabel(self.bitmaps[1])
            self.buttons[1].SetBitmapLabel(self.bitmaps[2])
            self.buttons[2].SetBitmapLabel(self.bitmaps[4])
            self.home_panel.Hide()
            self.logs_panel.Show()
            self.graphs_panel.Hide()
            self.settings_panel.Hide()
            self.logs_panel.update()
            self.Layout()
        elif self.pid == PLANET_BUTTON_GRAPHS:
            self.buttons[0].SetBitmapLabel(self.bitmaps[0])
            self.buttons[1].SetBitmapLabel(self.bitmaps[3])
            self.buttons[2].SetBitmapLabel(self.bitmaps[4])
            self.home_panel.Hide()
            self.logs_panel.Hide()
            self.graphs_panel.Show()
            self.settings_panel.Hide()
            self.graphs_panel.drop_down_menu.update_items()
            self.Layout()
        elif self.pid == PLANET_BUTTON_SETTINGS:
            self.buttons[0].SetBitmapLabel(self.bitmaps[0])
            self.buttons[1].SetBitmapLabel(self.bitmaps[2])
            self.buttons[2].SetBitmapLabel(self.bitmaps[5])
            self.home_panel.Hide()
            self.logs_panel.Hide()
            self.graphs_panel.Hide()
            self.settings_panel.Show()
            self.settings_panel.update()
            self.Layout()
        elif self.pid == PLANET_BUTTON_HOME:
            self.buttons[0].SetBitmapLabel(self.bitmaps[0])
            self.buttons[1].SetBitmapLabel(self.bitmaps[2])
            self.buttons[2].SetBitmapLabel(self.bitmaps[4])
            self.home_panel.Show()
            self.logs_panel.Hide()
            self.graphs_panel.Hide()
            self.settings_panel.Hide()
            self.Layout()

    def on_close_window(self, evt):
        """callback function that is called when the window is closed
        :param evt: event
        """
        for log_file in self.logs_panel.logs:
            log_file.log_stop()
        self.Destroy()


class ConfigManager(ConfigParser.ConfigParser):
    """manages the configuration file"""

    def __init__(self, config_path):
        ConfigParser.ConfigParser.__init__(self, allow_no_value=True)
        self.config_path = config_path
        self.read(config_path)

    def set_default_host(self, host):
        self.set('DEFAULTS', 'host', str(host))
        self._write_config()

    def get_default_host(self):
        return self.get('DEFAULTS', 'host')

    def set_default_path(self, path):
        self.set('DEFAULTS', 'path', str(path))
        self._write_config()

    def get_default_path(self):
        return self.get('DEFAULTS', 'path')

    def _write_config(self):
        with open(self.config_path, 'w') as fp:
            self.write(fp)


if __name__ == '__main__':
    app = wx.App()

    # create variable for the basepath
    basepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    # start config manager
    config_manager = ConfigManager(basepath + '/data/settings.ini')

    # start the application
    main_frame = MainFrame(title='planEt', size=(1029, 650), menu_height=115)
    main_frame.Show()
    app.MainLoop()
