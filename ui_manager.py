from PyQt5.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QTextEdit,QLabel,QRadioButton,QPushButton,QGroupBox
from PyQt5.QtGui import QFont,QIcon,QPixmap
from PyQt5.Qt import Qt,QSizePolicy,QSize

class UIManager:
    def create_layout(self,parent,type,alignment=None,stretch=1):
        # Create layout dynamically based on type
        layout = QVBoxLayout() if type == 'v' else QHBoxLayout() if type == 'h' else QGridLayout()
        if alignment:
            layout.setAlignment(alignment)
        parent.addLayout(layout,stretch)
        return layout

    def create_textfield(self,layout,title=None,placeholder=None,margins=None,read_only=None):
        # Create text field with optional title and placeholder
        local_layout = self.create_layout(layout,'v')
        title_object = self.create_label(local_layout, title, font='Arial', size=18, stretch=1)
        text_edit = QTextEdit()
        text_edit.setFont(QFont('Arial',12))
        text_edit.setStyleSheet("border:2px solid black")
        if margins:
            local_layout.setContentsMargins(*margins)
        if read_only:
            text_edit.setReadOnly(True)
            text_edit.setText(placeholder)
        elif placeholder:
            text_edit.setPlaceholderText(placeholder)
        local_layout.addWidget(title_object)
        local_layout.addWidget(text_edit)

        return text_edit

    def create_radio_selection(self,layout,buttons,is_icon=False,button_action=None,layout_direction='v',layout_stretch=1):
        # Create radio button selection with optional icons
        radio_layout = QHBoxLayout() if layout_direction == 'h' else QVBoxLayout()
        button_group = QGroupBox()
        button_group.setLayout(radio_layout)
        button_group.setStyleSheet('border:none')
        radio_layout.addStretch(1)
        for button in buttons:
            radio_button = QRadioButton(button) if not is_icon else QRadioButton()
            if is_icon:
                icon = QIcon(f'assets/{button}.png')
                radio_button.setIcon(icon)
                radio_button.setIconSize(QSize(40,40))
                radio_button.setToolTip(button)
            radio_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            radio_button.clicked.connect(button_action)
            if button == buttons[0]:
                radio_button.setChecked(True)
                if is_icon:
                    radio_button.setStyleSheet('padding-left:75px;')
            elif is_icon:
                radio_button.setStyleSheet('padding-right:75px;')
            radio_layout.addWidget(radio_button,1)
            radio_layout.addStretch(1)

        layout.addWidget(button_group,layout_stretch)


    def create_button(self,layout,text,size=(100,25),color=(255,255,0),action=None):
        # Create button with optional size, color, and action
        button = QPushButton(text)
        button.setFixedSize(*size)
        if color:
            button. setStyleSheet(f'background-color:rgb({color})')
        if action:
            button.clicked.connect(action)

        layout.addWidget(button,1)

    def create_label(self,layout,text,font='Arial',size=18,width=None,height=None,align=None,stretch=1):
        # Create label with optional font, size, width, height, alignment
        label = QLabel(text)
        label.setFont(QFont(font,size))
        if height:
            label.setFixedHeight(height)
        if width:
            label.setFixedWidth(width)
        if align:
            label.setAlignment(align)
        layout.addWidget(label,stretch)
        return label
