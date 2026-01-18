import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,
                             QSlider, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QFont



class Rura:
    def __init__(self, punkty, grubosc=12):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.czy_plynie = False

    def draw(self, painter):
        if len(self.punkty) < 2: return
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]: path.lineTo(p)
        painter.setPen(QPen(QColor(60, 60, 60), self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)
        if self.czy_plynie:
            painter.setPen(QPen(QColor(0, 180, 255), self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(path)


class Zbiornik:
    def __init__(self, x, y, width=90, height=120, nazwa="", ma_grzalke=False):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.temperatura = 20.0
        self.temp_zadana = 20.0
        self.ma_grzalke = ma_grzalke
        self.grzanie_on = False

    def aktualizuj(self):
        if self.ma_grzalke and self.aktualna_ilosc > 2:
            if self.temperatura < self.temp_zadana:
                self.temperatura += 0.3
                self.grzanie_on = True
            else:
                self.grzanie_on = False

        if self.temperatura > 20.1:
            self.temperatura -= 0.05

        if self.aktualna_ilosc < 0: self.aktualna_ilosc = 0

    def draw(self, painter):
        poziom_h = (self.height - 4) * (self.aktualna_ilosc / self.pojemnosc)
        r = min(255, int((self.temperatura - 20) * 4))
        b = max(0, 255 - r)
        kolor_wody = QColor(r, 120, b, 200)

        if poziom_h > 0:
            painter.setBrush(kolor_wody)
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(self.x + 2), int(self.y + self.height - poziom_h - 2), int(self.width - 4),
                             int(poziom_h))

        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.x, self.y, self.width, self.height)

        if self.ma_grzalke:
            painter.setPen(QPen(Qt.red if self.grzanie_on else Qt.gray, 4))
            painter.drawLine(self.x + 15, self.y + self.height - 10, self.x + self.width - 15,
                             self.y + self.height - 10)

        painter.setPen(Qt.white)
        painter.setFont(QFont('Segoe UI', 8, QFont.Bold))
        painter.drawText(self.x, self.y - 25, self.nazwa)
        painter.setFont(QFont('Segoe UI', 8))
        painter.drawText(self.x, self.y - 10, f"{self.temperatura:.1f}C | {int(self.aktualna_ilosc)}L")



class WidokInstalacji(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for r in self.p.rury: r.draw(painter)
        for z in self.p.zbiorniki: z.draw(painter)
        color = Qt.green if self.p.pompa_aktywna else Qt.gray
        painter.setBrush(color)
        painter.drawEllipse(210, 255, 30, 30)
        painter.setPen(Qt.black)
        painter.drawText(220, 275, "P")


class WidokRaportu(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.p = parent
        layout = QVBoxLayout(self)
        self.tabela = QTableWidget(4, 3)
        self.tabela.setHorizontalHeaderLabels(["Urzadzenie", "Status", "Parametry"])
        self.tabela.setStyleSheet("background-color: #222; color: white; gridline-color: #444;")
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("TABELA STATUSOW I ALARMOW"))
        layout.addWidget(self.tabela)

    def odswiez(self):
        for i, z in enumerate(self.p.zbiorniki):
            self.tabela.setItem(i, 0, QTableWidgetItem(z.nazwa))
            stan = "ALARM" if z.aktualna_ilosc > 95 else ("PRACA" if z.aktualna_ilosc > 0 else "PUSTY")
            self.tabela.setItem(i, 1, QTableWidgetItem(stan))
            self.tabela.setItem(i, 2, QTableWidgetItem(f"{z.aktualna_ilosc:.1f}L | {z.temperatura:.1f}C"))



class AplikacjaSCADA(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System SCADA v3.0")
        self.setFixedSize(1000, 750)
        self.setStyleSheet("background-color: #1a1a1a; color: #eee;")

        self.inicjalizuj_proces()
        self.init_ui()
        self.switch_screen(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.cykl_procesu)
        self.timer.start(100)

    def inicjalizuj_proces(self):
        self.z_glowny = Zbiornik(50, 200, nazwa="Zasilanie")
        self.z_a = Zbiornik(350, 50, nazwa="Reaktor A", ma_grzalke=True)
        self.z_b = Zbiornik(350, 350, nazwa="Reaktor B", ma_grzalke=True)
        self.z_koniec = Zbiornik(650, 200, nazwa="Magazyn")
        self.zbiorniki = [self.z_glowny, self.z_a, self.z_b, self.z_koniec]

        self.pompa_aktywna = False
        self.rury = [
            Rura([(140, 270), (210, 270)]),
            Rura([(240, 270), (280, 270), (280, 110), (350, 110)]),
            Rura([(280, 270), (280, 410), (350, 410)]),
            Rura([(440, 110), (550, 110), (550, 270), (650, 270)]),
            Rura([(440, 410), (550, 410), (550, 270)])
        ]

    def init_ui(self):
        layout = QVBoxLayout(self)
        nav = QHBoxLayout()
        self.btn_wiz = QPushButton("WIZUALIZACJA")
        self.btn_rap = QPushButton("RAPORTY")
        self.buttons = [self.btn_wiz, self.btn_rap]
        for i, b in enumerate(self.buttons):
            b.clicked.connect(lambda checked, idx=i: self.switch_screen(idx))
            nav.addWidget(b)
        layout.addLayout(nav)

        self.stack = QStackedWidget()
        self.ekran_wiz = WidokInstalacji(self)
        self.ekran_rap = WidokRaportu(self)
        self.stack.addWidget(self.ekran_wiz)
        self.stack.addWidget(self.ekran_rap)
        layout.addWidget(self.stack)

        controls = QHBoxLayout()
        grp_p1 = QGroupBox("Zasilanie")
        l1 = QVBoxLayout()
        self.lbl_val_level = QLabel("Poziom zadany: 0L")
        self.sld_level = QSlider(Qt.Horizontal)
        self.sld_level.setRange(0, 100)
        self.sld_level.valueChanged.connect(self.dopelnij_zasilanie)  # Zmieniona nazwa
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.clicked.connect(self.reset_systemu)
        l1.addWidget(self.lbl_val_level);
        l1.addWidget(self.sld_level);
        l1.addWidget(self.btn_reset)
        grp_p1.setLayout(l1)

        grp_p2 = QGroupBox("Temperatura")
        l2 = QVBoxLayout()
        self.lbl_t_a = QLabel("Zadana A: 20C")
        self.sld_t_a = QSlider(Qt.Horizontal);
        self.sld_t_a.setRange(20, 90)
        self.sld_t_a.valueChanged.connect(lambda v: [setattr(self.z_a, 'temp_zadana', v), self.update_labels()])
        self.lbl_t_b = QLabel("Zadana B: 20C")
        self.sld_t_b = QSlider(Qt.Horizontal);
        self.sld_t_b.setRange(20, 90)
        self.sld_t_b.valueChanged.connect(lambda v: [setattr(self.z_b, 'temp_zadana', v), self.update_labels()])
        l2.addWidget(self.lbl_t_a);
        l2.addWidget(self.sld_t_a)
        l2.addWidget(self.lbl_t_b);
        l2.addWidget(self.sld_t_b)
        grp_p2.setLayout(l2)

        controls.addWidget(grp_p1);
        controls.addWidget(grp_p2)
        layout.addLayout(controls)

    def dopelnij_zasilanie(self):
        self.z_glowny.aktualna_ilosc = float(self.sld_level.value())
        self.update_labels()

    def update_labels(self):
        self.lbl_val_level.setText(f"Poziom zadany: {self.sld_level.value()} L")
        self.lbl_t_a.setText(f"Zadana A: {self.sld_t_a.value()}C")
        self.lbl_t_b.setText(f"Zadana B: {self.sld_t_b.value()}C")

    def switch_screen(self, index):
        self.stack.setCurrentIndex(index)
        s_act = "background-color: #0055ff; color: white; font-weight: bold; padding: 10px;"
        s_inact = "background-color: #333; color: #888; padding: 10px;"
        for i, btn in enumerate(self.buttons):
            btn.setStyleSheet(s_act if i == index else s_inact)

    def reset_systemu(self):
        for z in self.zbiorniki:
            z.aktualna_ilosc = 0
            z.temperatura = 20
        self.sld_level.setValue(0)
        self.sld_t_a.setValue(20)
        self.sld_t_b.setValue(20)
        self.update_labels()

    def cykl_procesu(self):
        spd = 0.8
        pobrano = 0
        if self.z_glowny.aktualna_ilosc > 0.1:
            self.pompa_aktywna = True
            self.rury[0].czy_plynie = True
            if self.z_a.aktualna_ilosc < 100:
                self.z_a.aktualna_ilosc += spd / 2;
                pobrano += spd / 2;
                self.rury[1].czy_plynie = True
            else:
                self.rury[1].czy_plynie = False
            if self.z_b.aktualna_ilosc < 100:
                self.z_b.aktualna_ilosc += spd / 2;
                pobrano += spd / 2;
                self.rury[2].czy_plynie = True
            else:
                self.rury[2].czy_plynie = False
            self.z_glowny.aktualna_ilosc -= pobrano
        else:
            self.pompa_aktywna = False
            for i in range(3): self.rury[i].czy_plynie = False

        for r_src, r_idx in [(self.z_a, 3), (self.z_b, 4)]:
            if r_src.temperatura > 45 and r_src.aktualna_ilosc > 0 and self.z_koniec.aktualna_ilosc < 100:
                il = spd / 3
                v_o, t_o = self.z_koniec.aktualna_ilosc, self.z_koniec.temperatura
                if (v_o + il) > 0:
                    self.z_koniec.temperatura = (v_o * t_o + il * r_src.temperatura) / (v_o + il)
                r_src.aktualna_ilosc -= il
                self.z_koniec.aktualna_ilosc += il
                self.rury[r_idx].czy_plynie = True
            else:
                self.rury[r_idx].czy_plynie = False

        for z in self.zbiorniki: z.aktualizuj()
        if self.stack.currentIndex() == 1: self.ekran_rap.odswiez()
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AplikacjaSCADA()
    window.show()
    sys.exit(app.exec_())