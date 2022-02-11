from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import QDialog,QMessageBox
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv

class Ui_OutputDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("outputwindow.ui", self)
        #Update time
        currentDate = QDate.currentDate().toString('ddd dd MMMM yyyy')
        currentTime = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(currentDate)
        self.Time_Label.setText(currentTime)
        self.image = None

    @pyqtSlot()
    def startVideo(self, cameraName):
        if len(cameraName) == 1:
        	self.capture = cv2.VideoCapture(int(cameraName))
        else:
        	self.capture = cv2.VideoCapture(cameraName)
        self.timer = QTimer(self)  # Create Timer

        path = 'ImagesAttendance'
        # check whether the specified path exists or not
        if not os.path.exists(path):
            os.mkdir(path)

        images = []
        self.class_names = []
        self.encode_list = []
        self.TimeList1 = []
        self.TimeList2 = []
        attendanceList = os.listdir(path) # ['Jennie.jpg', 'Kha Uyen.jpg', ....]

        for cl in attendanceList:
            # load current image
            currentImg = cv2.imread(f'{path}/{cl}')
            # insert current image to images list
            images.append(currentImg)
            # insert name to class_names list
            self.class_names.append(os.path.splitext(cl)[0])

        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # determine face's location
            boxes = face_recognition.face_locations(img)
            # encode face's location
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]
            self.encode_list.append(encodes_cur_frame)

        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(10)  # emit the timeout() signal

    def face_rec(self, frame, encode_list_known, class_names):
        """
        frame: frame from camera
        encode_list_known: known face encoding
        class_names: known face names
        """
        # csv
        def mark_attendance(name):
            """
            name: detected face known or unknown one
            """
            if self.ClockInButton.isChecked():
                self.ClockInButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                        if (name != 'unknown'):
                            buttonReply = QMessageBox.question(self, f'Welcome {name}', 'Are you Checking In?',
                                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            # when user click 'Yes'
                            if buttonReply == QMessageBox.Yes:
                                date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                                f.writelines(f'\n{name},{date_time_string},Check In')
                                self.ClockInButton.setChecked(False)

                                self.NameLabel.setText(name)
                                self.StatusLabel.setText('Checked In')
                                self.HoursLabel.setText('Measuring')
                                self.MinLabel.setText('')

                                self.Time1 = datetime.datetime.now()
                                self.ClockInButton.setEnabled(True)
                            # when user click 'No'
                            else:
                                self.ClockInButton.setEnabled(True)

            elif self.ClockOutButton.isChecked():
                self.ClockOutButton.setEnabled(False)
                with open('Attendance.csv', 'a') as f:
                        if (name != 'unknown'):
                            buttonReply = QMessageBox.question(self, f'Welcom {name}', 'Are you Checking Out?',
                                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if buttonReply == QMessageBox.Yes:
                                date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                                f.writelines(f'\n{name},{date_time_string},Check Out')
                                self.ClockOutButton.setChecked(False)

                                self.NameLabel.setText(name)
                                self.StatusLabel.setText('Checked Out')
                                self.Time2 = datetime.datetime.now()

                                self.ElapseList(name)
                                self.TimeList2.append(datetime.datetime.now())
                                CheckInTime = self.TimeList1[-1]
                                CheckOutTime = self.TimeList2[-1]
                                self.ElapseHours = (CheckOutTime - CheckInTime)
                                # Format float with no decimal places
                                self.MinLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60)%60) + 'm')
                                self.HoursLabel.setText("{:.0f}".format(abs(self.ElapseHours.total_seconds() / 60**2)) + 'h')
                                self.ClockOutButton.setEnabled(True)
                            else:
                                print('Not clicked.')
                                self.ClockOutButton.setEnabled(True)

        # face recognition
        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)

        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)

            if match[best_match_index]:
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            mark_attendance(name)
        return frame

    def ElapseList(self,name):
        with open('Attendance.csv', "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            Time1 = datetime.datetime.now()
            Time2 = datetime.datetime.now()
            for row in csv_reader:
                for field in row:
                    if field in row:
                        if field == 'Check In':
                            if row[0] == name:
                                # tạo đối tượng datetime từ một chuỗi cho trước
                                Time1 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S'))
                                self.TimeList1.append(Time1)
                        if field == 'Check Out':
                            if row[0] == name:
                                Time2 = (datetime.datetime.strptime(row[1], '%y/%m/%d %H:%M:%S'))
                                self.TimeList2.append(Time2)

    def update_frame(self):
        isTrue, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def displayImage(self, image, encode_list, class_names, window=1):
        """
        image: frame from camera
        encode_list: known face encoding list
        class_names: known face names
        window: number of window
        """
        image = cv2.resize(image, (640, 480))
        image = self.face_rec(image, encode_list, class_names)

        qformat = QImage.Format_Indexed8
        # function to convert image data format beacuse cv2.cvtColor works slowly
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat) # QImage(img, width, height, bytesPerLine, form)
        outImage = outImage.rgbSwapped() # rgbSwapped() function constructs a BGR image from a RGB image

        if window == 1:
            # convert into a QPixmap using the fromImage()
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            # When enabled and the label shows a pixmap, it will scale the pixmap to fill the available space.
            self.imgLabel.setScaledContents(True)
