from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)
        
        self.frequencySpinBox = QDoubleSpinBox(self.groupBox)
        self.frequencySpinBox.setObjectName(u"frequencySpinBox")
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.frequencySpinBox)
        
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)
        
        self.durationSpinBox = QDoubleSpinBox(self.groupBox)
        self.durationSpinBox.setObjectName(u"durationSpinBox")
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.durationSpinBox)
        
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)
        
        self.deviceComboBox = QComboBox(self.groupBox)
        self.deviceComboBox.setObjectName(u"deviceComboBox")
        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.deviceComboBox)
        
        self.verticalLayout.addWidget(self.groupBox)
        
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        
        self.horizontalLayout = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        
        self.playButton = QPushButton(self.groupBox_2)
        self.playButton.setObjectName(u"playButton")
        self.horizontalLayout.addWidget(self.playButton)
        
        self.stopButton = QPushButton(self.groupBox_2)
        self.stopButton.setObjectName(u"stopButton")
        self.horizontalLayout.addWidget(self.stopButton)
        
        self.verticalLayout.addWidget(self.groupBox_2)
        
        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        
        self.tabWidget = QTabWidget(self.groupBox_3)
        self.tabWidget.setObjectName(u"tabWidget")
        
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        
        self.waveformPlot = QWidget(self.tab)
        self.waveformPlot.setObjectName(u"waveformPlot")
        self.waveformPlot.setMinimumSize(0, 300)
        self.verticalLayout_3.addWidget(self.waveformPlot)
        
        self.tabWidget.addTab(self.tab, "")
        
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_4 = QVBoxLayout(self.tab_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        
        self.spectrumPlot = QWidget(self.tab_2)
        self.spectrumPlot.setObjectName(u"spectrumPlot")
        self.spectrumPlot.setMinimumSize(0, 300)
        self.verticalLayout_4.addWidget(self.spectrumPlot)
        
        self.tabWidget.addTab(self.tab_2, "")
        
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.verticalLayout.addWidget(self.groupBox_3)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Sound Hz Emiter", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Controls", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Frequency (Hz):", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Duration (s):", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Processing Device:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Actions", None))
        self.playButton.setText(QCoreApplication.translate("MainWindow", u"Play Tone", None))
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Visualization", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Waveform", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Spectrum", None))
