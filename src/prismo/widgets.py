import functools

from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from qtpy.QtGui import QDoubleValidator

from . import devices


def init_widgets(ctrl):
    widgets = {}
    routes = {}

    for device in ctrl.devices:
        if isinstance(device, devices.Valves) or isinstance(device, device.Chip):
            path = f"widget/{device.name}"
            widgets[f"{device.name} controller"] = lambda r: ValveController(r.subpath(path))
            server = ValveControllerServer(device)
            routes = {**routes, **server.routes(path)}

    return widgets, routes


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
        layout.addWidget(QLabel("Bottom Right"), 2, 0)
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


class PositionSelector(QWidget):
    def __init__(self, relay, next_step):
        super().__init__()
        layout = QVBoxLayout(self)
        self.setMaximumHeight(150)

        self.rows = QVBoxLayout()
        layout.addLayout(self.rows)
        btns = QHBoxLayout()
        add_btn = QPushButton("Add")
        continue_btn = QPushButton("Continue")
        btns.addWidget(add_btn)
        btns.addWidget(continue_btn)
        layout.addLayout(btns)

        self.add_row()
        add_btn.clicked.connect(self.add_row)
        continue_btn.clicked.connect(self.next_step)

        self._relay = relay
        self._next_step = next_step

    def add_row(self):
        row = QHBoxLayout()
        self.rows.addLayout(row)
        x = QLineEdit()
        x.setValidator(QDoubleValidator())
        y = QLineEdit()
        y.setValidator(QDoubleValidator())
        set_btn = QPushButton("Set")
        set_btn.setMinimumWidth(50)
        delete_btn = QPushButton("Rem")
        delete_btn.setMinimumWidth(50)

        row.addWidget(x)
        row.addWidget(y)
        row.addWidget(set_btn)
        row.addWidget(delete_btn)

        delete_btn.clicked.connect(lambda: self.delete(row))
        set_btn.clicked.connect(lambda: self.set(row))

    def set(self, row):
        x = row.itemAt(0).widget()
        y = row.itemAt(1).widget()
        xy = self._relay.get("xy")
        x.setText(f"{xy[0]:.2f}")
        y.setText(f"{xy[1]:.2f}")

    def delete(self, row):
        self.rows.removeItem(row)

    def next_step(self):
        valid = True
        xys = []

        for i in range(self.rows.count()):
            row = self.rows.itemAt(i).layout()
            x = row.itemAt(0).widget()
            y = row.itemAt(1).widget()
            for w in [x, y]:
                if not w.text():
                    valid = False
                    w.setStyleSheet("border: 1px solid red;")
                else:
                    w.setStyleSheet("border: 0px;")

            if x.text() and y.text():
                xys.append((float(x.text()), float(y.text())))

        if valid:
            self.close()
            self._next_step(xys)


class ValveController(QWidget):
    def __init__(self, relay):
        super().__init__()
        self._relay = relay
        self._valves = self._relay.get("valves")
        self._valve_btns = {}
        self.setMaximumHeight(150)
        layout = QGridLayout(self)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_valves)
        self._timer.start(100)

        for i, (k, v) in enumerate(self._valves.items()):
            btn = QPushButton(str(k))
            btn.setStyleSheet(self.button_stylesheet(v))
            btn.setMinimumWidth(10)
            btn.clicked.connect(functools.partial(self.toggle_valve, k))
            layout.addWidget(btn, i // 8, i % 8)
            self._valve_btns[k] = btn

    def update_valves(self):
        self._valves = self._relay.get("valves")
        for k, v in self._valves.items():
            self._valve_btns[k].setStyleSheet(self.button_stylesheet(v))

    def toggle_valve(self, key):
        v = not self._valves[key]
        self._valves[key] = v
        self._relay.post("set_valve", key, v)
        self._valve_btns[key].setStyleSheet(self.button_stylesheet(v))

    def button_stylesheet(self, is_green):
        return (
            f"background-color: {'green' if is_green else 'red'};"
            "margin: 0.5px;"
            "border-radius: 0px;"
        )


class ValveControllerServer:
    def __init__(self, valves):
        self._valves = valves

    def routes(self, path):
        return {path + "/valves": self.get_valves, path + "/set_valve": self.set_valve}

    def get_valves(self):
        return self._valves.valves

    def set_valve(self, idx, value):
        self._valves[idx] = value
