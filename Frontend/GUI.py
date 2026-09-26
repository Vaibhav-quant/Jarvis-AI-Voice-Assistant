from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QLabel,
    QSizePolicy
)

from PyQt5.QtGui import (
    QIcon,
    QPainter,
    QMovie,
    QColor,
    QTextCharFormat,
    QFont,
    QPixmap,
    QTextBlockFormat
)

from PyQt5.QtCore import (
    Qt,
    QSize,
    QTimer
)

from dotenv import dotenv_values

import sys
import os


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

env_vars = dotenv_values(".env")

AssistantName = env_vars.get(
    "Assistantname",
    env_vars.get("AssistantName", "Jarvis")
)

current_dir = os.getcwd()

old_chat_messages = ""

TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


# --------------------------------------------------
# ANSWER MODIFIER
# --------------------------------------------------

def AnswerModifier(Answer):

    lines = Answer.split('\n')

    non_empty_lines = [
        line for line in lines
        if line.strip()
    ]

    modified_answer = '\n'.join(non_empty_lines)

    return modified_answer


# --------------------------------------------------
# QUERY MODIFIER
# --------------------------------------------------

def QueryModifier(Query):

    new_query = Query.lower().strip()

    if not new_query:
        return ""

    query_words = new_query.split()

    question_words = [
        "how",
        "what",
        "who",
        "where",
        "when",
        "why",
        "which",
        "whose",
        "whom",
        "can you",
        "what's",
        "where's",
        "how's"
    ]

    if any(word + " " in new_query for word in question_words):

        if query_words[-1][-1] in ['.', '?', '!']:

            new_query = new_query[:-1] + "?"

        else:

            new_query += "?"

    else:

        if query_words[-1][-1] in ['.', '?', '!']:

            new_query = new_query[:-1] + "."

        else:

            new_query += "."

    return new_query.capitalize()


# --------------------------------------------------
# MICROPHONE STATUS
# --------------------------------------------------

def SetMicrophoneStatus(Command):

    with open(
        rf"{TempDirPath}\Mic.data",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(Command)


def GetMicrophoneStatus():

    with open(
        rf"{TempDirPath}\Mic.data",
        "r",
        encoding="utf-8"
    ) as file:

        Status = file.read()

    return Status


# --------------------------------------------------
# ASSISTANT STATUS
# --------------------------------------------------

def SetAssistantStatus(Status):

    with open(
        rf"{TempDirPath}\Status.data",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(Status)


def GetAssistantStatus():

    with open(
        rf"{TempDirPath}\Status.data",
        "r",
        encoding="utf-8"
    ) as file:

        Status = file.read()

    return Status


# --------------------------------------------------
# MICROPHONE BUTTON
# --------------------------------------------------

def MicButtonInitialized():

    SetMicrophoneStatus("False")


def MicButtonClosed():

    SetMicrophoneStatus("True")


# --------------------------------------------------
# PATH HELPERS
# --------------------------------------------------

def GraphicsDirectoryPath(Filename):

    path = rf"{GraphicsDirPath}\{Filename}"

    return path


def TempDirectoryPath(Filename):

    path = rf"{TempDirPath}\{Filename}"

    return path


# --------------------------------------------------
# SHOW TEXT TO SCREEN
# --------------------------------------------------

def ShowTextToScreen(Text):

    with open(
        rf"{TempDirPath}\Responses.data",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(Text)


# ==================================================
# CHAT SECTION
# ==================================================

class ChatSection(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            -10,
            40,
            40,
            100
        )

        layout.setSpacing(-100)


        # ------------------------------
        # CHAT TEXT
        # ------------------------------

        self.chat_text_edit = QTextEdit()

        self.chat_text_edit.setReadOnly(True)

        self.chat_text_edit.setTextInteractionFlags(
            Qt.NoTextInteraction
        )

        self.chat_text_edit.setFrameStyle(
            QFrame.NoFrame
        )

        layout.addWidget(
            self.chat_text_edit
        )


        # ------------------------------
        # BACKGROUND
        # ------------------------------

        self.setStyleSheet(
            "background-color: black;"
        )

        layout.setSizeConstraint(
            QVBoxLayout.SetDefaultConstraint
        )

        layout.setStretch(
            1,
            1
        )

        self.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )
        )


        # ------------------------------
        # TEXT COLOR
        # ------------------------------

        text_color = QColor(Qt.white)

        text_color_text = QTextCharFormat()

        text_color_text.setForeground(
            text_color
        )

        self.chat_text_edit.setCurrentCharFormat(
            text_color_text
        )


        # ------------------------------
        # JARVIS GIF
        # ------------------------------

        self.gif_label = QLabel()

        self.gif_label.setStyleSheet(
            "border: none;"
        )

        gif_path = GraphicsDirectoryPath(
            "Jarvis.gif"
        )

        if os.path.exists(gif_path):

            movie = QMovie(gif_path)

            max_gif_size_W = 480
            max_gif_size_H = 270

            movie.setScaledSize(
                QSize(
                    max_gif_size_W,
                    max_gif_size_H
                )
            )

            self.gif_label.setAlignment(
                Qt.AlignRight | Qt.AlignBottom
            )

            self.gif_label.setMovie(
                movie
            )

            movie.start()


        layout.addWidget(
            self.gif_label
        )


        # ------------------------------
        # STATUS LABEL
        # ------------------------------

        self.label = QLabel("")

        self.label.setStyleSheet(
            """
            color: white;
            font-size: 16px;
            margin-right: 195px;
            border: none;
            margin-top: -30px;
            """
        )

        self.label.setAlignment(
            Qt.AlignRight
        )

        layout.addWidget(
            self.label
        )

        layout.setSpacing(-10)


        # ------------------------------
        # FONT
        # ------------------------------

        font = QFont()

        font.setPointSize(13)

        self.chat_text_edit.setFont(
            font
        )


        # ------------------------------
        # TIMER
        # ------------------------------

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.LoadMessages
        )

        self.timer.timeout.connect(
            self.SpeechRecogText
        )

        self.timer.start(100)


        # ------------------------------
        # SCROLL BAR
        # ------------------------------

        self.setStyleSheet(
            """
            QScrollBar:vertical {
                background: black;
                width: 10px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical {
                background: black;
                height: 10px;
            }

            QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }

            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            """
        )


    # --------------------------------------------------
    # LOAD MESSAGES
    # --------------------------------------------------

    def LoadMessages(self):

        global old_chat_messages

        try:

            with open(
                TempDirectoryPath(
                    "Responses.data"
                ),
                "r",
                encoding="utf-8"
            ) as file:

                messages = file.read()


            if not messages:

                return


            if str(old_chat_messages) == str(messages):

                return


            self.addMessage(
                message=messages,
                color="White"
            )

            old_chat_messages = messages

        except Exception:

            pass


    # --------------------------------------------------
    # SPEECH RECOGNITION STATUS
    # --------------------------------------------------

    def SpeechRecogText(self):

        try:

            with open(
                TempDirectoryPath(
                    "Status.data"
                ),
                "r",
                encoding="utf-8"
            ) as file:

                messages = file.read()

            self.label.setText(
                messages
            )

        except Exception:

            pass


    # --------------------------------------------------
    # ADD MESSAGE
    # --------------------------------------------------

    def addMessage(
        self,
        message,
        color
    ):

        cursor = self.chat_text_edit.textCursor()

        format = QTextCharFormat()

        formatm = QTextBlockFormat()

        formatm.setTopMargin(10)

        formatm.setBottomMargin(10)

        format.setForeground(
            QColor(color)
        )

        cursor.setBlockFormat(
            formatm
        )

        cursor.setCharFormat(
            format
        )

        cursor.insertText(
            message + "\n"
        )

        self.chat_text_edit.setTextCursor(
            cursor
        )


# ==================================================
# INITIAL SCREEN
# ==================================================

class InitialScreen(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        desktop = QApplication.desktop()

        screen_width = desktop.screenGeometry().width()

        screen_height = desktop.screenGeometry().height()


        # ------------------------------
        # MAIN LAYOUT
        # ------------------------------

        content_layout = QVBoxLayout()

        content_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )


        # ------------------------------
        # JARVIS GIF
        # ------------------------------

        gif_label = QLabel()

        gif_path = GraphicsDirectoryPath(
            "Jarvis.gif"
        )

        if os.path.exists(gif_path):

            movie = QMovie(
                gif_path
            )

            max_gif_size_H = int(
                screen_width / 16 * 9
            )

            movie.setScaledSize(
                QSize(
                    screen_width,
                    max_gif_size_H
                )
            )

            gif_label.setMovie(
                movie
            )

            movie.start()


        gif_label.setAlignment(
            Qt.AlignCenter
        )

        gif_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        # ------------------------------
        # MICROPHONE ICON
        # ------------------------------

        self.icon_label = QLabel()

        mic_path = GraphicsDirectoryPath(
            "Mic_on.png"
        )

        if os.path.exists(mic_path):

            pixmap = QPixmap(
                mic_path
            )

            new_pixmap = pixmap.scaled(
                60,
                60,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.icon_label.setPixmap(
                new_pixmap
            )


        self.icon_label.setFixedSize(
            150,
            150
        )

        self.icon_label.setAlignment(
            Qt.AlignCenter
        )


        # ------------------------------
        # TOGGLE STATE
        # ------------------------------

        self.toggled = True

        self.toggle_icon()

        self.icon_label.mousePressEvent = (
            self.toggle_icon
        )


        # ------------------------------
        # STATUS
        # ------------------------------

        self.label = QLabel("")

        self.label.setStyleSheet(
            """
            color: white;
            font-size: 16px;
            margin-bottom: 0;
            """
        )


        # ------------------------------
        # ADD WIDGETS
        # ------------------------------

        content_layout.addWidget(
            gif_label,
            alignment=Qt.AlignCenter
        )

        content_layout.addWidget(
            self.label,
            alignment=Qt.AlignCenter
        )

        content_layout.addWidget(
            self.icon_label,
            alignment=Qt.AlignCenter
        )


        content_layout.setContentsMargins(
            0,
            0,
            150,
            0
        )


        self.setLayout(
            content_layout
        )

        self.setFixedHeight(
            screen_height
        )

        self.setFixedWidth(
            screen_width
        )

        self.setStyleSheet(
            "background-color: black;"
        )


        # ------------------------------
        # TIMER
        # ------------------------------

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.SpeechRecogText
        )

        self.timer.start(100)


    # --------------------------------------------------
    # SPEECH STATUS
    # --------------------------------------------------

    def SpeechRecogText(self):

        try:

            with open(
                TempDirectoryPath(
                    "Status.data"
                ),
                "r",
                encoding="utf-8"
            ) as file:

                messages = file.read()

            self.label.setText(
                messages
            )

        except Exception:

            pass


    # --------------------------------------------------
    # LOAD ICON
    # --------------------------------------------------

    def load_icon(
        self,
        path,
        width=60,
        height=60
    ):

        if not os.path.exists(path):

            return

        pixmap = QPixmap(path)

        new_pixmap = pixmap.scaled(
            width,
            height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.icon_label.setPixmap(
            new_pixmap
        )


    # --------------------------------------------------
    # TOGGLE MICROPHONE
    # --------------------------------------------------

    def toggle_icon(
        self,
        event=None
    ):

        if self.toggled:

            self.load_icon(
                GraphicsDirectoryPath(
                    "Mic_on.png"
                ),
                60,
                60
            )

            MicButtonInitialized()

        else:

            self.load_icon(
                GraphicsDirectoryPath(
                    "Mic_off.png"
                ),
                60,
                60
            )

            MicButtonClosed()

        self.toggled = not self.toggled


# ==================================================
# MESSAGE SCREEN
# ==================================================

class MessageScreen(QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        desktop = QApplication.desktop()

        screen_width = desktop.screenGeometry().width()

        screen_height = desktop.screenGeometry().height()


        layout = QVBoxLayout()


        label = QLabel("")

        layout.addWidget(
            label
        )


        chat_section = ChatSection()

        layout.addWidget(
            chat_section
        )


        self.setLayout(
            layout
        )

        self.setStyleSheet(
            "background-color: black;"
        )

        self.setFixedHeight(
            screen_height
        )

        self.setFixedWidth(
            screen_width
        )


# ==================================================
# CUSTOM TOP BAR
# ==================================================

class CustomTopBar(QWidget):

    def __init__(
        self,
        parent,
        stacked_widget
    ):

        super().__init__(
            parent
        )

        self.stacked_widget = stacked_widget

        self.current_screen = None

        self.offset = None

        self.draggable = True

        self.init()


    # --------------------------------------------------
    # TOP BAR UI
    # --------------------------------------------------

    def init(self):

        self.setFixedHeight(
            50
        )

        layout = QHBoxLayout(
            self
        )

        layout.setAlignment(
            Qt.AlignRight
        )


        # ------------------------------
        # HOME
        # ------------------------------

        home_button = QPushButton()

        home_icon = QIcon(
            GraphicsDirectoryPath(
                "Home.png"
            )
        )

        home_button.setIcon(
            home_icon
        )

        home_button.setText(
            "  Home  "
        )

        home_button.setStyleSheet(
            """
            height: 40px;
            background-color: white;
            color: black;
            """
        )


        # ------------------------------
        # CHAT
        # ------------------------------

        message_button = QPushButton()

        message_icon = QIcon(
            GraphicsDirectoryPath(
                "Chats.png"
            )
        )

        message_button.setIcon(
            message_icon
        )

        message_button.setText(
            "  Chat  "
        )

        message_button.setStyleSheet(
            """
            height: 40px;
            background-color: white;
            color: black;
            """
        )


        # ------------------------------
        # MINIMIZE
        # ------------------------------

        minimize_button = QPushButton()

        minimize_icon = QIcon(
            GraphicsDirectoryPath(
                "Minimize2.png"
            )
        )

        minimize_button.setIcon(
            minimize_icon
        )

        minimize_button.setStyleSheet(
            "background-color: white;"
        )

        minimize_button.clicked.connect(
            self.minimizeWindow
        )


        # ------------------------------
        # MAXIMIZE
        # ------------------------------

        self.maximize_button = QPushButton()

        self.maximize_icon = QIcon(
            GraphicsDirectoryPath(
                "Maximize.png"
            )
        )

        self.restore_icon = QIcon(
            GraphicsDirectoryPath(
                "Minimize.png"
            )
        )

        self.maximize_button.setIcon(
            self.maximize_icon
        )

        self.maximize_button.setFlat(
            True
        )

        self.maximize_button.setStyleSheet(
            "background-color: white;"
        )

        self.maximize_button.clicked.connect(
            self.maximizeWindow
        )


        # ------------------------------
        # CLOSE
        # ------------------------------

        close_button = QPushButton()

        close_icon = QIcon(
            GraphicsDirectoryPath(
                "Close.png"
            )
        )

        close_button.setIcon(
            close_icon
        )

        close_button.setStyleSheet(
            "background-color: white;"
        )

        close_button.clicked.connect(
            self.closeWindow
        )


        # ------------------------------
        # TITLE
        # ------------------------------

        title_label = QLabel(
            f"{AssistantName.capitalize()} AI"
        )

        title_label.setStyleSheet(
            """
            color: black;
            font-size: 18px;
            background-color: white;
            """
        )


        # ------------------------------
        # NAVIGATION
        # ------------------------------

        home_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0)
        )

        message_button.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(1)
        )


        # ------------------------------
        # LAYOUT
        # ------------------------------

        layout.addWidget(
            title_label
        )

        layout.addStretch(1)

        layout.addWidget(
            home_button
        )

        layout.addWidget(
            message_button
        )

        layout.addWidget(
            minimize_button
        )

        layout.addWidget(
            self.maximize_button
        )

        layout.addWidget(
            close_button
        )


    # --------------------------------------------------
    # PAINT EVENT
    # --------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(
            self
        )

        painter.fillRect(
            self.rect(),
            Qt.white
        )

        super().paintEvent(
            event
        )


    # --------------------------------------------------
    # MINIMIZE
    # --------------------------------------------------

    def minimizeWindow(self):

        self.parent().showMinimized()


    # --------------------------------------------------
    # MAXIMIZE
    # --------------------------------------------------

    def maximizeWindow(self):

        if self.parent().isMaximized():

            self.parent().showNormal()

            self.maximize_button.setIcon(
                self.maximize_icon
            )

        else:

            self.parent().showMaximized()

            self.maximize_button.setIcon(
                self.restore_icon
            )


    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------

    def closeWindow(self):

        self.parent().close()


    # --------------------------------------------------
    # DRAG WINDOW
    # --------------------------------------------------

    def mousePressEvent(
        self,
        event
    ):

        if self.draggable:

            self.offset = (
                event.globalPos()
                - self.parent().pos()
            )


    def mouseMoveEvent(
        self,
        event
    ):

        if self.offset is not None:

            new_pos = (
                event.globalPos()
                - self.offset
            )

            self.parent().move(
                new_pos
            )


# ==================================================
# MAIN WINDOW
# ==================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint
        )

        self.initUI()


    # --------------------------------------------------
    # INITIALIZE UI
    # --------------------------------------------------

    def initUI(self):

        desktop = QApplication.desktop()

        screen_width = (
            desktop.screenGeometry().width()
        )

        screen_height = (
            desktop.screenGeometry().height()
        )


        # ------------------------------
        # STACKED WIDGET
        # ------------------------------

        stacked_widget = QStackedWidget(
            self
        )

        initial_screen = InitialScreen()

        message_screen = MessageScreen()


        stacked_widget.addWidget(
            initial_screen
        )

        stacked_widget.addWidget(
            message_screen
        )


        # ------------------------------
        # WINDOW
        # ------------------------------

        self.setGeometry(
            0,
            0,
            screen_width,
            screen_height
        )

        self.setStyleSheet(
            "background-color: black;"
        )


        # ------------------------------
        # TOP BAR
        # ------------------------------

        top_bar = CustomTopBar(
            self,
            stacked_widget
        )

        self.setMenuWidget(
            top_bar
        )


        # ------------------------------
        # CENTRAL WIDGET
        # ------------------------------

        self.setCentralWidget(
            stacked_widget
        )


# ==================================================
# START GUI
# ==================================================

def GraphicalUserInterface():

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec_()
    )


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    GraphicalUserInterface()