import os
import re

from PySide2.QtWidgets import QApplication, QMainWindow, QTextBrowser, QTreeWidget, QTreeWidgetItem, QVBoxLayout, \
    QWidget, QSplitter
from PySide2.QtCore import Qt, QUrl
from bs4 import BeautifulSoup

from dialogs.base import BaseDialog


class HelpApp(BaseDialog):
    def __init__(self, html_path, parent=None):
        super(HelpApp, self).__init__(parent)

        self.vlayout = QVBoxLayout()

        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderLabels(["Справка"])
        self.tree_widget.itemClicked.connect(self.tree_item_clicked)

        self.browser = QTextBrowser()

        self.splitter = self.create_splitter()

        self.vlayout.addWidget(self.splitter)

        self.setLayout(self.vlayout)

        self.html_path = html_path

        self.populate_tree()

        # Load the default HTML file
        # self.load_html_file("html/1.html")
        self.setWindowTitle('Справка')

        self.show()

    def create_splitter(self):
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(self.browser)
        return splitter

    def populate_tree(self):
        # Add root item
        # root_item.setText(0, "Table of Contents")
        last_h1 = None
        last_h2 = None
        last_h3 = None
        for html in sorted(os.listdir(self.html_path)):
            soup = BeautifulSoup(open(self.html_path + "/" + html, encoding='ISO-8859-1'), features="lxml")
            tags = soup.find_all(re.compile('^h[1-4]$'))
            for tag in tags:
                tag_text = tag.text.encode('ISO-8859-1').decode('utf-8')
                if tag.name == 'h1':
                    last_h1 = self.add_tree_item(None, tag_text, self.html_path + "/" + html)
                elif tag.name == 'h2':
                    last_h2 = self.add_tree_item(last_h1, tag_text, self.html_path + "/" + html)
                elif tag.name == 'h3':
                    last_h3 = self.add_tree_item(last_h2, tag_text, self.html_path + "/" + html)
                elif tag.name == 'h4':
                    self.add_tree_item(last_h3, tag_text, self.html_path + "/" + html)

    def add_tree_item(self, parent, title, file_path):
        if not parent:
            parent = self.tree_widget
        item = QTreeWidgetItem(parent)
        item.setText(0, title)
        item.setData(0, Qt.UserRole, file_path)  # Store file path as user data
        return item

    def tree_item_clicked(self, item):
        # Get the file path from user data
        file_path = item.data(0, Qt.UserRole)
        if file_path:
            self.load_html_file(file_path)

    def load_html_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        self.browser.setHtml(html_content)


if __name__ == "__main__":
    app = QApplication([])
    window = HelpApp('resources/docs')
    app.exec_()
