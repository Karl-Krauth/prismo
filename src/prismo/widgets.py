from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)
from qtpy.QtGui import QDoubleValidator


class BoundarySelector(QWidget):
    def __init__(self, relay, next_step):
        super().__init__()
        self.setMaximumHeight(150)
        layout = QGridLayout(self)

        self.left_x = QLineEdit()
        self.left_x.setValidator(QDoubleValidator())
        self.left_y = QLineEdit()
        self.left_y.setValidator(QDoubleValidator())
        self.left_btn = QPushButton("Set")
        self.left_btn.setMinimumWidth(50)

        self.right_x = QLineEdit()
        self.right_x.setValidator(QDoubleValidator())
        self.right_y = QLineEdit()
        self.right_y.setValidator(QDoubleValidator())
        self.right_btn = QPushButton("Set")
        self.right_btn.setMinimumWidth(50)

        continue_btn = QPushButton("Continue")

        layout.addWidget(QLabel("x"), 0, 1, alignment=Qt.AlignHCenter)
        layout.addWidget(QLabel("y"), 0, 2, alignment=Qt.AlignHCenter)
        layout.addWidget(QLabel("Top Left"), 1, 0)
        layout.addWidget(self.left_x, 1, 1)
        layout.addWidget(self.left_y, 1, 2)
        layout.addWidget(self.left_btn, 1, 3)

        layout.addWidget(self.right_x, 2, 1)
        layout.addWidget(self.right_y, 2, 2)
        layout.addWidget(self.right_btn, 2, 3)

        layout.addWidget(continue_btn, 3, 0)

        layout.setColumnMinimumWidth(3, 60)
        layout.setHorizontalSpacing(10)

        self.left_btn.clicked.connect(self.set_left)
        self.right_btn.clicked.connect(self.set_right)
        continue_btn.clicked.connect(self.next_step)

        self._relay = relay
        self._next_step = next_step

    def set_left(self):
        xy = self._relay.get("xy")
        self.left_x.setText(f"{xy[0]:.2f}")
        self.left_y.setText(f"{xy[1]:.2f}")

    def set_right(self):
        xy = self._relay.get("xy")
        self.right_x.setText(f"{xy[0]:.2f}")
        self.right_y.setText(f"{xy[1]:.2f}")

    def next_step(self):
        if (
            self.left_x.text()
            and self.left_y.text()
            and self.right_x.text()
            and self.right_y.text()
        ):
            self.close()
            self._next_step(
                (float(self.left_x.text()), float(self.left_y.text())),
                (float(self.right_x.text()), float(self.right_y.text())),
            )
        else:
            for w in [self.left_x, self.left_y, self.right_x, self.right_y]:
                if not w.text():
                    w.setStyleSheet("border: 1px solid red;")
                else:
                    w.setStyleSheet("border: 0px;")


class ValveController(QWidget):
    def __init__(self, relay):
        super().__init__()
        self._relay = relay
        self._valves = self._relay.get("valves")
        self._valve_btns = {}
        # self.setMaximumHeight(150)
        layout = QGridLayout(self)

        for i, (k, v) in enumerate(self._valves.items()):
            btn = QPushButton(str(k))
            btn.setStyleSheet(f"background-color: {'green' if v else 'red'};")
            btn.setMinimumWidth(10)
            btn.clicked.connect(lambda: self.toggle_valve(k))
            layout.addWidget(btn, i % 8, i // 8)
            self._valve_btns[k] = btn

        layout.addWidget(QLabel("Bottom Right"), 2, 0)
        # layout.setColumnMinimumWidth(3, 60)
        # layout.setHorizontalSpacing(10)

    def update_valves(self):
        self._valves = self._relay.get("valves")
        for k, v in self._valves.items():
            self.valve_btns[k].setStyleSheet(f"background-color: {'green' if v else 'red'};")

    def toggle_valve(self, key):
        v = not self._valves[key]
        self._valves[key] = v
        self._relay.post("set_valve", key, v)
        self._valve_btns[key].setStyleSheet(f"background-color: {'green' if v else 'red'};")
