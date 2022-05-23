from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QDate, Qt, QModelIndex, QAbstractTableModel
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from datetime import date
import sys
import pandas as pd
import numpy as np


class DataModel(QAbstractTableModel):

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super(DataModel, self).__init__(parent)
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._dataframe)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._dataframe.columns)

        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])

        return None

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: Qt.ItemDataRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None


class ResultsWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(ResultsWindow, self).__init__(parent)
        self.ui = QUiLoader().load('results.ui')
        self.ui.show()

        self.ui.resultsTable.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)

        model = DataModel(res_df)
        self.ui.resultsTable.setModel(model)
        self.ui.resultsTable.setColumnWidth(0, 100)
        self.ui.resultsTable.setColumnWidth(1, 100)
        self.ui.resultsTable.horizontalHeader().setStretchLastSection(True)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = QUiLoader().load("main.ui")
        self.ui.show()

        today = QDate.fromString(date.today().strftime('%d/%m/%Y'),
                                 'dd/MM/yyyy')
        self.ui.endDate.setDate(today)

        self.ui.browseButton.clicked.connect(self.fileSelect)
        self.ui.calcButton.clicked.connect(self.calculate)

    def fileSelect(self):
        filepath, filter = QFileDialog.getOpenFileName(
            parent=self, caption='Select CSV File', filter='*.csv')

        self.ui.browseLabel.setText(filepath)

    def calculate(self):
        self.ui.browseLabel.setStyleSheet(None)

        if (self.ui.browseLabel.text() == ''):
            QMessageBox.critical(self, 'Error', 'No CSV file selected')
            self.ui.browseLabel.setFocus()
            self.ui.browseLabel.setStyleSheet('background-color: red')
            return

        filepath = self.ui.browseLabel.text()

        # Column names
        headers = [
            'Date', 'Time', 'Event', 'Asset', 'Qty', 'Currency', 'Value',
            'Rate', 'AUDFee', '$AUD', 'FeeAmt', 'FeeAsset', 'GST', 'ExGST',
            'DepTo', 'WithTo', 'WithFee', 'Reference', 'TransID', 'UUID'
        ]

        # Import the data
        df = pd.read_csv(filepath, names=headers)

        # Prepare the data
        df.drop(df[df['Event'] != 'reward'].index, inplace=True)
        df.drop([
            'Time', 'Currency', 'Value', 'Rate', 'AUDFee', 'FeeAmt',
            'FeeAsset', 'GST', 'ExGST', 'DepTo', 'WithTo', 'WithFee',
            'Reference', 'TransID', 'UUID'
        ],
                axis=1,
                inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

        # pd.options.display.float_format = '{:,.8f}'.format
        df['Qty'] = df['Qty'].astype(float)
        df['$AUD'] = df['$AUD'].astype(float)

        # Get date data
        min_date = str(self.ui.startDate.text())
        max_date = str(self.ui.endDate.text())
        min_date_pd = pd.to_datetime(min_date, format='%d/%m/%Y')
        max_date_pd = pd.to_datetime(max_date, format='%d/%m/%Y')

        # Drop dates not within range
        df = df[(df['Date'] >= min_date_pd) & (df['Date'] <= max_date_pd)]

        global res_df
        res_df = df.groupby(['Asset'])[['Qty', '$AUD']].sum()

        res_df['$AUD / Share'] = np.where(res_df['$AUD'] <= 0, res_df['$AUD'],
                                          res_df['$AUD'] / res_df['Qty'])

        res_df['Qty'] = res_df['Qty'].apply(lambda x: '{:,.8f}'.format(x))
        res_df['$AUD'] = res_df['$AUD'].apply(lambda x: '$ {:,.2f}'.format(x))
        res_df['$AUD / Share'] = res_df['$AUD / Share'].apply(
            lambda x: '$ {:,.8f}'.format(x))

        print(res_df)

        self.resultsWindow = ResultsWindow(self)
        self.resultsWindow.ui.show()


def main():
    global res_df
    res_df = pd.DataFrame()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec()


if __name__ == '__main__':
    main()