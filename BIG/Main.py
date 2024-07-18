import sys
import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, \
    QSpinBox, QTextEdit
from PyQt5.QtCore import Qt
from icrawler.builtin import GoogleImageCrawler
import winreg


def get_desktop_path():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
    return desktop_path


DESKTOP_PATH = get_desktop_path()


class ImageDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Query input
        query_layout = QHBoxLayout()
        query_layout.addWidget(QLabel('Search Query:'))
        self.query_input = QLineEdit()
        query_layout.addWidget(self.query_input)
        layout.addLayout(query_layout)

        # Number of images
        num_images_layout = QHBoxLayout()
        num_images_layout.addWidget(QLabel('Number of Images:'))
        self.num_images_input = QSpinBox()
        self.num_images_input.setRange(1, 100)
        self.num_images_input.setValue(10)
        num_images_layout.addWidget(self.num_images_input)
        layout.addLayout(num_images_layout)

        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel('Color:'))
        self.color_combo = QComboBox()
        self.color_combo.addItems(
            ['Any', 'Color', 'Black and White', 'Transparent', 'Red', 'Orange', 'Yellow', 'Green', 'Teal', 'Blue',
             'Purple', 'Pink', 'White', 'Gray', 'Black', 'Brown'])
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)

        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('Type:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Any', 'Face', 'Photo', 'Clipart', 'Line Drawing', 'Animated'])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel('Size:'))
        self.size_combo = QComboBox()
        self.size_combo.addItems(['Any', 'Large', 'Medium', 'Icon', '>400*300', '>640*480', '>800*600', '>1024*768'])
        size_layout.addWidget(self.size_combo)
        layout.addLayout(size_layout)

        # License
        license_layout = QHBoxLayout()
        license_layout.addWidget(QLabel('License:'))
        self.license_combo = QComboBox()
        self.license_combo.addItems(['Any', 'Creative Commons', 'Public Domain'])
        license_layout.addWidget(self.license_combo)
        layout.addLayout(license_layout)

        # Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel('Format:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['Any', 'JPG', 'GIF', 'PNG', 'BMP', 'SVG', 'WebP', 'ICO', 'RAW'])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Time
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel('Time:'))
        self.time_combo = QComboBox()
        self.time_combo.addItems(['Any time', 'Past 24 hours', 'Past 7 days', 'Past month', 'Past year'])
        time_layout.addWidget(self.time_combo)
        layout.addLayout(time_layout)

        # Download button
        self.download_button = QPushButton('Download Images')
        self.download_button.clicked.connect(self.download_images)
        layout.addWidget(self.download_button)

        # Result display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # Add creator information
        creator_label = QLabel('Created by Sacha Brassel')
        creator_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(creator_label)

        self.setLayout(layout)
        self.setWindowTitle('Advanced Image Downloader - Created by Sacha Brassel')
        self.setGeometry(300, 300, 400, 550)

    def download_images(self):
        query = self.query_input.text()
        num_images = self.num_images_input.value()
        color = self.color_combo.currentText().lower().replace(' ', '').replace('any', '')
        image_type = self.type_combo.currentText().lower().replace(' ', '-').replace('any', '')
        size = self.size_combo.currentText().lower().replace('any', '')
        license = self.license_combo.currentText().lower().replace(' ', '').replace('any', '')
        format = self.format_combo.currentText().lower().replace('any', '')
        time = self.time_combo.currentText()

        download_dir = os.path.join(DESKTOP_PATH, f'downloaded_images_{query.replace(" ", "_")}')
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        os.makedirs(download_dir)

        filters = {}
        if color:
            filters['color'] = color
        if image_type:
            filters['type'] = image_type
        if size:
            filters['size'] = size
        if license:
            filters['license'] = license
        if format:
            filters['format'] = format
        if time != 'Any time':
            if time == 'Past 24 hours':
                filters['date'] = 'pastday'
            elif time == 'Past 7 days':
                filters['date'] = 'pastweek'
            else:
                # For 'Past month' and 'Past year', we won't set a date filter
                # as icrawler doesn't support these options directly
                pass

        google_crawler = GoogleImageCrawler(
            feeder_threads=1,
            parser_threads=1,
            downloader_threads=4,
            storage={'root_dir': download_dir},
            log_level=50
        )

        google_crawler.crawl(keyword=query, max_num=num_images, filters=filters)

        self.rename_images(download_dir, query)

        downloaded_count = len(
            [name for name in os.listdir(download_dir) if os.path.isfile(os.path.join(download_dir, name))])

        result = f"Downloaded {downloaded_count} images to {download_dir}."
        self.result_display.setText(result)

    def rename_images(self, download_dir, query):
        for i, filename in enumerate(os.listdir(download_dir)):
            file_extension = os.path.splitext(filename)[1]
            new_filename = f'{query.replace(" ", "_")}_{i:03d}{file_extension}'
            old_path = os.path.join(download_dir, filename)
            new_path = os.path.join(download_dir, new_filename)
            os.rename(old_path, new_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageDownloaderApp()
    ex.show()
    sys.exit(app.exec_())