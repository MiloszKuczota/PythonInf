import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class Rura:
    # __init__ – konstruktor rury, wywoływany przy tworzeniu obiektu
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):
        # Zamiana punktów na QPointF (QPainter pracuje na QPointF)
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        # Flaga informująca, czy w rurze płynie ciecz
        self.czy_plynie = False
        self.kolor_cieczy_zmieniony = QColor(255, 100, 0)  #kolor wody po podgrzaniu
        self.temperuje_ciecz = False  # czy rura ma grzałkę/ogrzewa ciecz

    # Metoda zmieniająca stan przepływu (ON / OFF)
    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    # Zwraca środek prostego odcinka rury do umieszczenia grzałki
    def punkt_srodkowy(self):
        if len(self.punkty) < 3:
            return None
        p1 = self.punkty[1]
        p2 = self.punkty[2]
        cx = (p1.x() + p2.x()) / 2
        cy = (p1.y() + p2.y()) / 2
        return cx, cy

    # Metoda rysująca rurę
    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        # 1. Rysowanie obudowy rury (zewnętrzna linia)
        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        # 2. Rysowanie cieczy wewnątrz rury, tylko jeśli płynie
        if self.czy_plynie:
        # jeśli grzałka, ciecz w rurze zmienia kolor
            kolor_cieczy_rury = self.kolor_cieczy_zmieniony if self.temperuje_ciecz else self.kolor_cieczy
            pen_ciecz = QPen(kolor_cieczy_rury, self.grubosc - 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)
            
class Grzalka:
    def __init__(self, rura, rozmiar=10):
        # Rura, na której ma być grzałka
        self.rura = rura
        self.rozmiar = rozmiar
        self.rura.temperuje_ciecz = True

    # Metoda rysująca grzałkę
    def draw(self, painter):
        punkt = self.rura.punkt_srodkowy()
        if not punkt:
            return

        cx, cy = punkt
        r1 = self.rozmiar
        r2 = self.rozmiar * 2

        pen = QPen(Qt.red, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Małe kółko
        painter.drawEllipse(
            int(cx - r1),
            int(cy - r1),
            int(2 * r1),
            int(2 * r1))
        # Duże kółko wokół
        painter.drawEllipse(int(cx - r2), int(cy - r2), int(2 * r2), int(2 * r2))

class Zbiornik:
    # Konstruktor zbiornika – ustawia pozycję, rozmiar i dane początkowe
    def __init__(self, x, y, width=100, height=140, nazwa="", kolor_cieczy=QColor(0, 120, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0
        #dla zmiany koloru cieczy
        self.kolor_cieczy = kolor_cieczy

    # Dodaje ciecz do zbiornika (z uwzględnieniem pojemności)
    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    # Usuwa ciecz ze zbiornika (nie może zejść poniżej zera)
    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    # Przelicza ilość cieczy na poziom (0–1)
    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    # Sprawdzenie czy zbiornik jest praktycznie pusty
    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    # Sprawdzenie czy zbiornik jest praktycznie pełny
    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1

    # Punkty przyłączeniowe rur (środek górnej i dolnej krawędzi zbiornika)
    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)

    # Rysowanie zbiornika
    def draw(self, painter):
        # 1. Rysowanie cieczy wewnątrz zbiornika
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.setBrush(self.kolor_cieczy) #kolor cieczy z konstruktora
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6), int(h_cieczy - 2))

        # 2. Rysowanie obrysu zbiornika
        pen = QPen(Qt.green, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))

        # 3. Rysowanie nazwy zbiornika
        painter.setPen(Qt.black)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

# ----- KLASA SYMULACJI -----
class SymulacjaKaskady(QWidget):
    # Główne okno aplikacji – zarządza całą symulacją
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Przelewanie cieczy w zbiornikach")
        self.setFixedSize(900, 600)
        self.setStyleSheet("background-color: #32;")

        # --- ZBIORNIKI ---
        self.z1 = Zbiornik(50, 50, nazwa="Zbiornik 1")
        self.z1.aktualna_ilosc = 100.0
        self.z1.aktualizuj_poziom()

        self.z15 = Zbiornik(650, 50, nazwa="Zbiornik 1.5")
        self.z15.aktualna_ilosc = 100.0
        self.z15.aktualizuj_poziom()

        self.z2 = Zbiornik(350, 200, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(350, 450, nazwa="Zbiornik 3", kolor_cieczy=QColor(255, 100, 0)) # woda po nagrzaniu symbolicznie

        self.zbiorniki = [self.z1, self.z2, self.z3, self.z15]

        # Rura 1: Z1 -> Z2
        p_start = self.z1.punkt_dol_srodek()
        p_koniec = self.z2.punkt_gora_srodek()
        mid_y = (p_start[1] + p_koniec[1]) / 2
        self.rura1 = Rura([p_start, (p_start[0], mid_y), (p_koniec[0], mid_y), p_koniec])

        # Rura 1.5: Z1.5 -> Z2
        p_start15 = self.z15.punkt_dol_srodek()
        p_koniec15 = self.z2.punkt_gora_srodek()
        mid_y15 = (p_start15[1] + p_koniec15[1]) / 2
        self.rura15 = Rura([p_start15, (p_start15[0], mid_y15), (p_koniec15[0], mid_y15), p_koniec15])

        # Rura 2: Z2 -> Z3

        p_start2 = self.z2.punkt_dol_srodek()
        p_koniec2 = self.z3.punkt_gora_srodek()
        mid_y2 = (p_start2[1] + p_koniec2[1]) / 2
        self.rura2 = Rura([p_start2, (p_start2[0], mid_y2), (p_koniec2[0], mid_y2), p_koniec2])

        self.rury = [self.rura1, self.rura2, self.rura15]

        #GRZAŁKA
        self.grzalka_rura2 = Grzalka(self.rura2)

        # TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika_przeplywu)

        # Przycisk start/stop symulacji
        self.btn = QPushButton("Start / Stop", self)
        self.btn.setGeometry(50, 550, 100, 30)
        self.btn.clicked.connect(self.przelacz_symulacje)

        self.running = False
        self.flow_speed = 0.8

    # Włącz/wyłącz symulację
    def przelacz_symulacje(self):
        if self.running:
            self.timer.stop()
            self.running = False
        else:
            self.timer.start(20)
            self.running = True

    #Logika przelewania cieczy
    def logika_przeplywu(self):
        #Z1 -> Z2
        plynie_1 = False
        if not self.z1.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z1.usun_ciecz(self.flow_speed)
            self.z2.dodaj_ciecz(ilosc)
            plynie_1 = True
        self.rura1.ustaw_przeplyw(plynie_1)

        # Przepływ Z15 -> Z2
        plynie_15 = False
        if not self.z15.czy_pusty() and not self.z2.czy_pelny():
            ilosc = self.z15.usun_ciecz(self.flow_speed)
            self.z2.dodaj_ciecz(ilosc)
            plynie_15 = True
        self.rura15.ustaw_przeplyw(plynie_15)

        # Przepływ Z2 -> Z3
        plynie_2 = False
        if self.z2.aktualna_ilosc > 5.0 and not self.z3.czy_pelny():
            ilosc = self.z2.usun_ciecz(self.flow_speed)
            self.z3.dodaj_ciecz(ilosc)
            plynie_2 = True
        self.rura2.ustaw_przeplyw(plynie_2)
        
        self.update()

    # Rysowanie całej sceny
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        #Najpierw rury
        for r in self.rury:
            r.draw(p)

        # grzałka na rurze 2
        self.grzalka_rura2.draw(p)

        # zbiorniki
        for z in self.zbiorniki:
            z.draw(p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    okno = SymulacjaKaskady()
    okno.show()
    sys.exit(app.exec_())