import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *
from worksql import *


class Window(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        loadUi(r'Database\interface.ui', self)

        self.setWindowTitle('Закупки')
        self.get_info()

        # Изменение Типа, Наименования отдела и оборудования
        self.comboBoxNameDep.currentTextChanged.connect(self.on_NameDep_changed)
        self.comboBoxTypeDep.currentTextChanged.connect(self.on_TypeDep_changed)
        self.comboBoxCall.currentTextChanged.connect(self.change_table_first)
        self.comboBoxCall.currentTextChanged.connect(self.change_table_Procur)

        # Ввод руководителя, кабинета
        self.lineEditBoss.returnPressed.connect(self.Boss_changed)
        self.lineEditCab.returnPressed.connect(self.Cab_changed)
        self.lineEditCab.returnPressed.connect(self.change_table_Plan)

        # кнопки
        self.pushButtonAddProc.clicked.connect(self.AddProc)
        self.pushButtonDelProc.clicked.connect(self.DelProc)
        self.pushButtonCleanProcur.clicked.connect(self.CleanProcur)

        self.pushButtonAddDevelop.clicked.connect(self.AddDevelop)
        self.pushButtonDelDevelop.clicked.connect(self.DelDevelop)
        self.pushButtonCleanDevelop.clicked.connect(self.CleanDevelop)

        self.pushButtonAddDep.clicked.connect(self.AddDep)
        self.pushButtonDelDep.clicked.connect(self.DelDep)
        self.pushButtonCleanDep.clicked.connect(self.CleanDep)

        # таблицы
        self.change_table_first()
        self.change_table_Procur()
        self.change_table_Plan()
        self.change_table_Deps()

    def get_info(self):
        '''получает информацию из базы данных и добавляет список подразделений, их типы, а также оборудование'''
        self.comboBoxTypeDep.clear()
        self.comboBoxNameDep.clear()
        self.comboBoxCall.clear()
        self.Dep_info = main_sql('Departments', 'получить')
        self.Procur = main_sql('Procurement', 'получить')
        self.comboBoxNameDep.addItem('Наименование структурного подразделения')
        self.comboBoxNameDep.addItems({v[0] for v in self.Dep_info})
        self.comboBoxTypeDep.addItem('Тип СП')
        self.comboBoxTypeDep.addItems({v[1] for v in self.Dep_info})
        self.comboBoxCall.addItem('Оборудование')
        self.comboBoxCall.addItems(main_sql('Equipment', 'получить'))

    def AddDep(self):
        '''Добавить новое структурное подразделение'''
        Name_dep = self.lineEditDep.text()
        Type_dep = self.lineEditType.text()
        Boss = self.lineEditBossDep.text()
        Cab = self.lineEditCabDep.text()
        main_sql('Departments', 'добавить', Name_dep, Type_dep, Boss, Cab)
        self.change_table_Deps()
        self.get_info()
        for i in [self.lineEditDep, self.lineEditType, self.lineEditBossDep, self.lineEditCabDep]:
            i.clear()

    def DelDep(self):
        '''Удалить структурное подразделение'''
        Name_dep = self.lineEditDep.text()
        if not Name_dep:
            Name_dep = self.comboBoxNameDep.currentText()
        main_sql('Departments', 'удалить', 'Name_dep', Name_dep)
        self.change_table_Deps()
        self.get_info()
        self.lineEditDep.clear()

    def CleanDep(self):
        '''Удалить из базы данных все структурное подразделения'''
        main_sql('Departments', 'очистить таблицу')
        self.change_table_Deps()
        self.get_info()

    def AddDevelop(self):
        '''Добавить пункт программы развития'''
        Point = self.lineEditPoint.text()
        Eq = self.lineEditEq.text()
        Extra = self.lineEditExtraforEq.text()
        amt = self.spinBoxDevProg.text()
        Budget = self.lineEditBudget.text()
        main_sql('Development_program', 'добавить', Point, Eq, Extra, amt, int(Budget)//int(amt), Budget)
        self.change_table_Plan()
        self.get_info()
        for i in [self.lineEditPoint, self.lineEditEq, self.lineEditExtraforEq, self.lineEditBudget]:
            i.clear()

    def DelDevelop(self):
        '''Удалить пункт программы развития'''
        Point = self.lineEditPoint.text()
        main_sql('Development_program', 'удалить', 'Point', Point)
        self.change_table_Plan()
        self.get_info()
        self.lineEditPoint.clear()
        main_sql('Таблица', 'проверить ключ')

    def CleanDevelop(self):
        '''Очистить таблицу программы развития'''
        main_sql('Development_program', 'очистить таблицу')
        self.change_table_Plan()
        self.get_info()
        main_sql('Таблица', 'проверить ключ')

    def CleanProcur(self):
        '''Удалить все заявки на закупку'''
        main_sql('Procurement', 'очистить таблицу')
        self.change_table_Procur()
        self.get_info()
        main_sql('Таблица', 'проверить ключ')

    def DelProc(self):
        '''Удалить заявки на закупку, которые соответствуют условиям'''
        val_Dep = str(self.comboBoxNameDep.currentText())
        val_Call = str(self.comboBoxCall.currentText())
        if val_Dep != 'Наименование структурного подразделения' and val_Call != 'Оборудование':
            info = main_sql('Procurement', 'удалить', 'Name_dep', val_Dep, 'Equipment', val_Call)
        elif val_Dep != 'Наименование структурного подразделения':
            info = main_sql('Procurement', 'удалить', 'Name_dep', val_Dep)
        elif val_Call != 'Оборудование':
            info = main_sql('Procurement', 'удалить', 'Equipment', val_Call)
        self.change_table_Procur()
        self.get_info()
        main_sql('Таблица', 'проверить ключ')

    def AddProc(self):
        '''Добавить заявку на закупку'''
        val_Dep = str(self.comboBoxNameDep.currentText())
        val_Call = str(self.lineEditProcurEq.text())
        if not val_Call:
            val_Call = str(self.comboBoxCall.currentText())
        vall_Count = int(self.spinBoxCountProcur.value())
        vall_Extra = str(self.textEditExtraProcur. toPlainText())
        # if not vall_Extra:
        #     vall_Extra = ''
        vall_Sat = int(self.spinBoxCountProcur.value())
        main_sql('Procurement', 'добавить', val_Dep, val_Call, vall_Extra, vall_Count, vall_Sat)
        self.change_table_Procur()
        self.get_info()
        for i in [self.lineEditProcurEq, self.textEditExtraProcur]:
            i.clear()

    def change_table_Deps(self):
        '''Таблица структурных подразделений'''
        self.HorizontalHeaderLabelsDep = ['Наименование структурного\nподразделения', 'Тип структурного\nподразделения',
                                          'Руководитель', 'Кабинет']
        self.tableWidgetDeps.setColumnCount(4)
        self.tableWidgetDeps.setHorizontalHeaderLabels(self.HorizontalHeaderLabelsDep)
        header = self.tableWidgetDeps.horizontalHeader()
        for i in range(4):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        val_Dep = str(self.comboBoxNameDep.currentText())
        val_Call = str(self.comboBoxCall.currentText())
        row = 0
        self.tableWidgetDeps.setRowCount(0)
        info = main_sql('Departments', 'получить')
        for row, row_data in enumerate(info):
            self.tableWidgetDeps.insertRow(row)
            for col, data in enumerate(row_data):
                it = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidgetDeps.setItem(row, col, it)

    def change_table_first(self):
        '''Выборка на соответствие программы развития и заявок'''
        self.HorizontalHeaderLabels = ['Оборудование', 'Пункт\nпрограммы\nразвития', 'Структурное\nподразделение',
                                       'Запрошено', 'Удовлетворено', 'Заложено\nв программу\nразвития', 'Бюджет']
        self.tableWidgetDepDevprog.setColumnCount(7)
        self.tableWidgetDepDevprog.setHorizontalHeaderLabels(self.HorizontalHeaderLabels)
        header = self.tableWidgetDepDevprog.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        val_Dep = str(self.comboBoxNameDep.currentText())
        val_Call = str(self.comboBoxCall.currentText())
        row = 0
        self.tableWidgetDepDevprog.setRowCount(0)
        if val_Dep == 'Наименование структурного подразделения' and val_Call == 'Оборудование':
            info = main_sql('Таблица', 'Таблица')
        elif val_Dep == 'Наименование структурного подразделения':
            '''Передает название оборудования'''
            info = main_sql('Таблица', 'Таблица', Equipment=val_Call)
        elif val_Call == 'Оборудование':
            '''Передает название отдела'''
            info = main_sql('Таблица', 'Таблица', Name_dep=val_Dep)
        else:
            '''Передает оборудование и отдел'''
            info = main_sql('Таблица', 'Таблица', Equipment=val_Call, Name_dep=val_Dep)
        last_id = -1
        start_row = 0
        for row, row_data in enumerate(info):
            self.tableWidgetDepDevprog.insertRow(row)
            current_id = row_data[0]
            for col, data in enumerate(row_data):
                it = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidgetDepDevprog.setItem(row, col, it)
            if last_id != current_id and last_id != -1:
                self.apply_span(start_row, row - start_row)
                start_row = row
            last_id = current_id
        if start_row != row:
            self.apply_span(start_row, self.tableWidgetDepDevprog.rowCount() - start_row)

    def apply_span(self, row, nrow):
        '''Объединение ячеек с одинаковым значением в определенных колонках'''
        if nrow <= 1:
            return
        for c in (0, 1, 5, 6):
            self.tableWidgetDepDevprog.setSpan(row, c, nrow, 1)
            for r in range(row+1, row+nrow):
                t = self.tableWidgetDepDevprog.takeItem(r, c)
                del t

    def change_table_Procur(self):
        '''Таблица заявок на закупки'''
        self.HorizontalHeaderLabelsProcur = ['Структурное\nподразделение', 'Оборудование', 'Дополнительно',
                                             'Запрошено', 'Удовлетворено']
        self.tableWidgetProcur.setColumnCount(5)
        self.tableWidgetProcur.setHorizontalHeaderLabels(self.HorizontalHeaderLabelsProcur)
        header = self.tableWidgetProcur.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        val_Dep = str(self.comboBoxNameDep.currentText())
        val_Call = str(self.comboBoxCall.currentText())
        row = 0
        self.tableWidgetProcur.setRowCount(0)
        if val_Dep == 'Наименование структурного подразделения' and val_Call == 'Оборудование':
            info = main_sql('Procurement', 'получить')
        elif val_Dep == 'Наименование структурного подразделения':
            '''Передает название оборудования'''
            info = main_sql('Procurement', 'получить', Equipment=val_Call)
        elif val_Call == 'Оборудование':
            '''Передает название отдела'''
            info = main_sql('Procurement', 'получить', Name_Dep=val_Dep)
        else:
            '''Передает оборудование и отдел'''
            info = main_sql('Procurement', 'получить', Name_Dep=val_Dep, Equipment=val_Call)
        for row, row_data in enumerate(info):
            self.tableWidgetProcur.insertRow(row)
            row_data = row_data[1:]
            for col, data in enumerate(row_data):
                it = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidgetProcur.setItem(row, col, it)

    def change_table_Plan(self):
        '''Таблица программы развития'''
        self.HorizontalHeaderLabelsProgram = ['Пункт', 'Оборудование', 'Дополнительно',
                                              'Количество', 'Стоимость', 'Бюджет']
        self.tableWidgetProgram.setColumnCount(6)
        self.tableWidgetProgram.setHorizontalHeaderLabels(self.HorizontalHeaderLabelsProgram)
        header = self.tableWidgetProgram.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        val_Call = str(self.comboBoxCall.currentText())
        row = 0
        self.tableWidgetProgram.setRowCount(0)
        if val_Call != 'Оборудование':
            '''Передает название оборудования'''
            info = main_sql('Development_program', 'получить', Equipment=val_Call)
        else:
            '''Передает оборудование и отдел'''
            info = main_sql('Development_program', 'получить')
        for row, row_data in enumerate(info):
            self.tableWidgetProgram.insertRow(row)
            for col, data in enumerate(row_data):
                it = QtWidgets.QTableWidgetItem(str(data))
                self.tableWidgetProgram.setItem(row, col, it)

    def Cab_changed(self):
        self.comboBoxNameDep.blockSignals(True)
        value = str(self.lineEditCab.text())
        for v in self.Dep_info:
            if value in v[3]:
                TypeDep = self.comboBoxTypeDep.findText(v[1])
                self.comboBoxTypeDep.setCurrentIndex(TypeDep)
                Name = self.comboBoxNameDep.findText(v[0])
                self.comboBoxNameDep.setCurrentIndex(Name)
                self.lineEditBoss.setText(v[2])
        self.comboBoxNameDep.blockSignals(False)

    def Boss_changed(self):
        '''Поиск подразделения через ввод руководителя'''
        self.comboBoxNameDep.blockSignals(True)
        value = str(self.lineEditBoss.text())
        for v in self.Dep_info:
            if v[2] == value:
                TypeDep = self.comboBoxTypeDep.findText(v[1])
                self.comboBoxTypeDep.setCurrentIndex(TypeDep)
                Name = self.comboBoxNameDep.findText(v[0])
                self.comboBoxNameDep.setCurrentIndex(Name)
                self.lineEditCab.setText(v[3])
        self.comboBoxNameDep.blockSignals(False)

    def on_NameDep_changed(self):
        '''Выбор структурного подразделения'''
        self.comboBoxNameDep.blockSignals(True)
        value = str(self.comboBoxNameDep.currentText())
        if value == 'Наименование структурного подразделения':
            self.comboBoxTypeDep.setCurrentIndex(0)
            self.lineEditBoss.setText('Руководитель')
            self.lineEditCab.setText('Кабинет')
        else:
            for v in self.Dep_info:
                if v[0] == value:
                    TypeDep = self.comboBoxTypeDep.findText(v[1])
                    self.comboBoxTypeDep.setCurrentIndex(TypeDep)
                    self.lineEditCab.setText(v[3])
                    self.lineEditBoss.setText(v[2])
        ind = self.comboBoxNameDep.findText(value)
        self.comboBoxNameDep.setCurrentIndex(ind)
        self.change_table_first()
        self.change_table_Procur()
        self.comboBoxNameDep.blockSignals(False)

    def on_TypeDep_changed(self):
        '''Выбор структурного подразделения'''
        self.comboBoxTypeDep.blockSignals(True)
        value = str(self.comboBoxTypeDep.currentText())
        self.comboBoxNameDep.clear()
        self.comboBoxNameDep.addItem('Наименование структурного подразделения')
        if value == 'Тип СП':
            self.comboBoxNameDep.addItems([v[0] for v in self.Dep_info])
            self.comboBoxNameDep.setCurrentIndex(0)
            self.lineEditBoss.setText('Руководитель')
            self.lineEditCab.setText('Кабинет')
        else:
            for v in self.Dep_info:
                if v[1] == value:
                    self.comboBoxNameDep.addItem(v[0])
        ind = self.comboBoxTypeDep.findText(value)
        self.comboBoxTypeDep.setCurrentIndex(ind)
        self.comboBoxTypeDep.blockSignals(False)

    def ButtonClickDrop(self):
        '''Сброс всех заданных параметров'''
        self.comboBoxTypeDep.setCurrentIndex(0)
        self.comboBoxCall.setCurrentIndex(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Window()
    window.show()
    app.exec()
