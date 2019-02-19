# Copyright (C) 2018-2019  Garrett Herschleb
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

import logging

import fix

logger=logging.getLogger(__name__)

class AVUI(QGraphicsView):
    """ Aviation UI, specialized for interface with only hard buttons and rotary encoders,
        no keyboard or mouse
    """
    def __init__(self, enc_key, enc_sel_key, parent=None,
                width_multiplier=1.0, background_color=Qt.gray,
                focus_color=Qt.green, popup=True):
        super(AVUI, self).__init__(parent)
        self.parent = parent
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.focus_level = 0
        self.focus_index = 0
        self.focus_highlight = None
        self.focus_color = focus_color
        self.width_multiplier = width_multiplier
        self.background_color = background_color
        self.enc = fix.db.get_item(enc_key)
        self.selbtn = fix.db.get_item(enc_sel_key)
        self.popup = popup
        if self.popup:
            self.hide()

    def set_widgets(self, widget_list):
        x = 0
        self.focus_targets = widget_list
        lpen = QPen(QColor(Qt.black))
        lpen.setWidth(5)
        for w in widget_list:
            self.scene.addWidget (w)
            w.move(x,0)
            x += w.width()
            self.scene.addLine (x,0, x,self.h, lpen)


    def resizeEvent(self, event):
        self.h = self.height()
        self.w = self.width()
        self.scene = QGraphicsScene(0,0, self.w*self.width_multiplier, self.h)
        self.scene.addRect (0,0, self.w*self.width_multiplier, self.h,
                        QPen(QColor(Qt.black)), QBrush(QColor(self.background_color)))

        self.setScene(self.scene)
        self.centerOn (0, self.h/2)

    def focus(self):
        if self.popup:
            self.show()
        self.focus_level = 0 if len(self.focus_targets) > 1 else 1
        self.focus_index = 0
        self.last_rotary = self.enc.value
        self.enc.valueChanged[int].connect(self.rotary)
        self.selbtn.valueChanged[bool].connect(self.select)
        self.draw_focus (True)

    def defocus(self):
        self.draw_focus (False)
        self.enc.valueChanged[int].disconnect(self.rotary)
        self.selbtn.valueChanged[bool].disconnect(self.select)
        if self.popup:
            self.hide()

    def draw_focus(self, yes):
        if self.focus_highlight is not None:
            self.scene.removeItem (self.focus_highlight)
            self.focus_highlight = None
        if yes:
            param = self.focus_targets[self.focus_index]
            if self.focus_level == 0:
                # Draw a highlighted box around the current parameter / focus target
                rect = QRectF(param.frameGeometry())
            else:
                rect = QRectF(param.draw_focus (yes))
                rect.moveLeft (rect.x() + param.x())
            hpen = QPen(QColor(self.focus_color))
            hpen.setWidth(3)
            hbrush = QBrush()
            self.focus_highlight = self.scene.addRect (rect, hpen, hbrush)
            self.centerOn (self.focus_highlight)

    def rotary(self, event):
        diff = self.enc.value - self.last_rotary 
        if self.focus_level == 0:
            self.focus_index += diff
            if self.focus_index < 0:
                self.focus_index = 0
            elif self.focus_index >= len(self.focus_targets):
                self.focus_index = len(self.focus_targets)-1
        else:
            param = self.focus_targets[self.focus_index]
            param.changeby(diff)
        self.draw_focus(True)
        self.last_rotary = self.enc.value

    def select(self, event):
        if self.selbtn.value:
            param = self.focus_targets[self.focus_index]
            if self.focus_level == 0:
                self.focus_level += 1
                param.focus_first()
            else:
                if not param.focus_next():
                    self.focus_level = 0 if len(self.focus_targets) > 1 else 1
            self.draw_focus(True)

class NumberWidget(QWidget):
    def __init__(self, title, num_var_digits, num_zero_digits, dbitem, parent=None, msd_limit=9):
        super(NumberWidget, self).__init__(parent)
        self.parent = parent
        self.dbitem = dbitem
        self.focus_index = 0
        self.var_digits = list()
        self.dials = list()
        font = QFont()
        font.setBold(True)
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.lock = False
        msd=True
        for i in range(num_var_digits):
            dial = QDial(self)
            dial.setMinimum(0)
            if msd:
                dial.setMaximum(msd_limit)
                msd = False
            else:
                dial.setMaximum(9)
            dial.setWrapping(True)
            dial.setFixedSize(15,15)
            dial.valueChanged.connect(self.dialChanged)
            self.dials.append(dial)
            self.layout.addWidget(dial, 2, i)
            digit = QLabel("0", parent=self)
            self.var_digits.append (digit)
            digit.setFont(font)
            self.layout.addWidget(digit, 1, i, Qt.AlignCenter)
            last_i = i

        self.num_zero_digits = num_zero_digits
        if num_zero_digits > 0:
            self.zero_digit = QLabel("0" * num_zero_digits)
            self.zero_digit.setFont(font)
            self.layout.addWidget(self.zero_digit, 1, last_i+1)
        else:
            self.zero_digit = None
        tlabel = QLabel(title)
        self.layout.addWidget(tlabel, 0, 0, 1, -1)
        self.setValue(self.dbitem.value)
        self.setLayout(self.layout)
        self.adjustSize()

    def setValue(self, v):
        self._value = v
        self.lock = True
        divisor = int(10**(len(self.var_digits) + self.num_zero_digits - 1))
        for dial,digit in zip(self.dials,self.var_digits):
            val = int(self._value / divisor) % 10
            t = str(val)
            dial.setValue(val)
            digit.setText(t)
            divisor /= 10
        self.lock = False

    def dialChanged(self, event):
        if not self.lock:
            multiplier = int(10**(len(self.var_digits) + self.num_zero_digits - 1))
            result = 0
            for dial,digit in zip(self.dials,self.var_digits):
                val = dial.value()
                result += multiplier * val
                digit.setText(str(val))
                multiplier /= 10
            self._value = result
            self.dbitem.value = self._value

    def draw_focus (self, yes):
        dial = self.dials[self.focus_index]
        digit = self.var_digits[self.focus_index]
        dial.setFocus()
        ret = dial.frameGeometry()
        ret |= digit.frameGeometry()
        return ret

    def changeby(self, diff):
        d = self.dials[self.focus_index]
        d.setValue((d.value() + diff) % 10)
    
    def focus_first(self):
        self.focus_index = 0
    
    def focus_next(self):
        if self.focus_index + 1 >= len(self.dials):
            return False
        else:
            self.focus_index += 1
            return True

class ChoiceWidget(QWidget):
    def __init__(self, title, choices, dbitem, parent=None, max_choice_rows=2, font_pixel_size=10):
        super(ChoiceWidget, self).__init__(parent)
        self.parent = parent
        self.dbitem = dbitem
        self.max_choice_rows = max_choice_rows
        self.font_pixel_size = font_pixel_size
        font = QFont()
        font.setPixelSize(font_pixel_size)
        self.setFont(font)
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.bg = QButtonGroup()
        self.buttons = list()
        row = 1
        col = 0

        for i,choice in enumerate(choices):
            button = QRadioButton(choice)
            if i == 0:
                button.setChecked(True)
            self.bg.addButton (button, i)
            self.layout.addWidget(button, row, col)
            self.buttons.append (button)
            row += 1
            if row >= self.max_choice_rows+1:
                row = 1
                col += 1
        self.bg.buttonClicked[int].connect(self.selChanged)

        tlabel = QLabel(title)
        lfont = QFont()
        lfont.setPixelSize(self.font_pixel_size)
        lfont.setBold(True)
        tlabel.setFont(lfont)
        self.layout.addWidget(tlabel, 0, 0, 1, -1)
        self.setLayout(self.layout)
        self.adjustSize()

    def selChanged(self, event):
        #print ("new sel = %d"%self.bg.checkedId())
        self.dbitem.value = self.bg.checkedId()

    def draw_focus (self, yes):
        ret = QRect()
        for b in self.buttons:
            ret |= b.frameGeometry()
        return ret

    def changeby(self, diff):
        newid = self.bg.checkedId()
        newid += diff
        if newid < 0:
            newid = 0
        elif newid >= len(self.buttons):
            newid = len(self.buttons) - 1
        self.buttons[newid].setChecked(True)
        #print ("new rotary sel %s = %d"%(self.dbitem.key, self.bg.checkedId()))
        self.dbitem.value = self.bg.checkedId()
    
    def focus_first(self):
        pass
    
    def focus_next(self):
        return False

class SelectMenuWidget(QGraphicsView):
    MENU_ACTION_TYPE_DBSEL_INDEX=0
    MENU_ACTION_TYPE_DBSEL_TEXT=1
    MENU_ACTION_TYPE_FUNCTION=2
    LEFT_MARGIN=5
    def __init__(self, title, choices, action_item, action_type, width, height,
                    parent=None, font_pixel_size=10):
        super(SelectMenuWidget, self).__init__()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.parent = parent
        self.font_pixel_size = font_pixel_size
        self.action_item = action_item
        self.action_type = action_type
        self.title = title
        self.choices = choices
        self.menu = None
        self.current_index = 0
        font = QFont()
        font.setPixelSize(font_pixel_size)
        self.setFont(font)
        self.resize(width, height)

    def resizeEvent(self, event):
        self.h = self.height()
        self.w = self.width()
        t = QGraphicsSimpleTextItem ("9")
        t.setFont(self.font())
        font_height = t.boundingRect().height()
        self.scene = QGraphicsScene(0,0, self.w, font_height * (len(self.choices)+1) + self.h)
        bgbrush = QBrush(QColor("#d0d0d0"))
        self.scene.addRect (0,0, self.scene.width(), self.scene.height(), QPen(QColor(Qt.black)), bgbrush)
        self.setScene(self.scene)
        hpen = QPen()
        hbrush = QBrush(QColor(Qt.white))
        rect = QRectF (0,self.h/2, self.w, font_height)
        self.focus_highlight = self.scene.addRect (rect, hpen, hbrush)
        y = self.h/2
        self.actions = list()

        for c in self.choices:
            self.actions.append (self.scene.addSimpleText (c))
            self.actions[-1].setY(y)
            self.actions[-1].setX(self.LEFT_MARGIN)
            y += font_height

        rect = QRectF (0,font_height/2, self.w, font_height)
        self.title_label_rect = self.scene.addRect (rect, hpen, bgbrush)
        self.title_label = self.scene.addSimpleText (self.title)
        self.title_label.setY(font_height/2)
        self.title_label.setX(self.LEFT_MARGIN)

        self.centerOn (self.focus_highlight)

    def setChoices(self, c):
        self.choices = c
        self.current_index = 0
        self.resizeEvent(0)

    def changeby(self, diff):
        newid = self.current_index
        newid += diff
        if newid < 0:
            newid = 0
        elif newid >= len(self.choices):
            newid = len(self.choices)-1
        self.current_index = newid
        h = self.actions[0].boundingRect().height()
        y = self.actions[self.current_index].y()
        self.focus_highlight.setRect (QRectF (0, y, self.w, h))
        self.title_label_rect.setRect (QRectF (0, y-self.h/2+h/2, self.w, h))
        self.title_label.setY(y-self.h/2+h/2)
        self.centerOn (self.focus_highlight)
    
    def menu_action(self):
        if self.action_type == self.MENU_ACTION_TYPE_DBSEL_INDEX:
            fix.db.get_item(self.action_item).value = self.current_index
        elif self.action_type == self.MENU_ACTION_TYPE_DBSEL_TEXT:
            fix.db.get_item(self.action_item).value = self.choices[self.current_index]
        elif self.action_type == self.MENU_ACTION_TYPE_FUNCTION:
            self.action_item (self.current_index, self.choices[self.current_index])

    def draw_focus (self, yes):
        return QRect(0,0,self.w, self.h)

    def focus_first(self):
        pass
    
    def focus_next(self):
        self.menu_action()
        return False

class FIXDisplay(QWidget):
    def __init__(self, title, dbitems, parent=None,
                    columns=3, font_pixel_size=10, description_overrides=None,
                    css_styles=None, item_css_styles=None):
        super(FIXDisplay, self).__init__(parent)
        self.parent = parent
        self.dbitems = dbitems
        self.columns = columns
        font = QFont()
        font.setBold(True)
        font.setPixelSize(font_pixel_size)
        self.layout = QGridLayout()
        row = 1
        column = 0
        columns_per_item=3
        self.value_displays = list()
        self.last_values = list()
        for index,dbi in enumerate(dbitems):
            item_widget = QWidget(parent=self)
            item_layout = QHBoxLayout()
            if description_overrides is not None and description_overrides[index] is not None:
                desc = QLabel (description_overrides[index], parent=item_widget)
            else:
                desc = QLabel (dbi.description, parent=item_widget)
            item_layout.addWidget(desc)

            self.last_values.append (dbi.value)
            value = QLabel(str(self.last_values[-1]), parent=item_widget)
            self.value_displays.append (value)
            value.setFont(font)
            item_layout.addWidget(value)

            un = QLabel (dbi.units, parent=item_widget)
            item_layout.addWidget(un)
            item_widget.setLayout(item_layout)
            if item_css_styles is not None:
                desc.setStyleSheet (item_css_styles)
                value.setStyleSheet (item_css_styles)
                un.setStyleSheet (item_css_styles)
            self.layout.addWidget (item_widget, row, column)

            column += 1
            if column >= columns:
                row += 1
                column = 0
            dbi.valueChanged[dbi.dtype].connect(self.fix_change)

        title_label = QLabel (title, parent=self)
        self.layout.addWidget(title_label, 0, 0, 1, -1, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
        if css_styles is not None:
            self.setStyleSheet (css_styles)
        self.adjustSize()
        
    def fix_change(self, event):
        for index,(dbi,last_val) in enumerate(zip(self.dbitems,self.last_values)):
            if dbi.value != last_val:
                self.last_values[index] = dbi.value
                self.value_displays[index].setText (str(self.last_values[index]))
