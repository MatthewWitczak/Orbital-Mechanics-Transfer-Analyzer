import sys, os
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QFormLayout, QMessageBox, QDialog, QDialogButtonBox, QFrame
)
from PyQt5.QtGui import QFont, QColor, QPalette, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

# Style
PASTEL_RED = "#ff6666"

def apply_glow(widget, hex_color=PASTEL_RED, blur=40):
    glow = QGraphicsDropShadowEffect(widget)
    glow.setBlurRadius(blur)
    glow.setOffset(0, 0)
    glow.setColor(QColor(hex_color))
    widget.setGraphicsEffect(glow)

# Parameters
class ParamDialog(QDialog):
    def __init__(self, font_family, mu, Re, r1, r2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parameters")
        self.setModal(True)
        self.setMinimumWidth(460)

        self.font_family = font_family

        label_font = QFont(self.font_family, 12)
        input_font = QFont(self.font_family, 12)

        self.le_mu = QLineEdit(str(mu))
        self.le_Re = QLineEdit(str(Re))
        self.le_r1 = QLineEdit(str(r1))
        self.le_r2 = QLineEdit(str(r2))

        for le in (self.le_mu, self.le_Re, self.le_r1, self.le_r2):
            le.setStyleSheet(
                "background-color: rgba(0,0,0,150); color: " + PASTEL_RED +
                "; border: 1px solid " + PASTEL_RED + "; padding: 6px;"
            )
            le.setFont(input_font)

        def mklabel(txt):
            l = QLabel(txt)
            l.setFont(label_font)
            l.setStyleSheet("color: rgba(255,102,102,200); background: transparent;")
            return l

        form = QFormLayout()
        form.addRow(mklabel("μ [m³/s²]"), self.le_mu)
        form.addRow(mklabel("R⊕ [km]"),   self.le_Re)
        form.addRow(mklabel("r₁ [km]"),   self.le_r1)
        form.addRow(mklabel("r₂ [km]"),   self.le_r2)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet(
            "QPushButton { background-color: rgba(0,0,0,150); border: 2px solid " + PASTEL_RED +
            "; color: " + PASTEL_RED + "; padding: 8px 12px; font-size: 14px; }"
            "QPushButton:hover { background-color: #1a0000; }"
        )

        root = QVBoxLayout()
        root.addLayout(form)
        root.addWidget(buttons, alignment=Qt.AlignRight)
        self.setLayout(root)

    def values(self):
        return self.le_mu.text(), self.le_Re.text(), self.le_r1.text(), self.le_r2.text()

# Presets
class PresetDialog(QDialog):
    def __init__(self, font_family, earth_mu, earth_Re, apply_cb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Presets")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.apply_cb = apply_cb

        title = QLabel("SELECT PRESET")
        title.setFont(QFont(font_family, 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: " + PASTEL_RED + ";")

        info = QLabel("Earth presets set μ and R⊕ to defaults.\nRadii = R⊕ + altitude for LEO/MEO/GEO.")
        info.setFont(QFont(font_family, 11))
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: rgba(255,102,102,200);")

        btn_style = (
            "QPushButton { background-color: rgba(0,0,0,150); border: 2px solid " + PASTEL_RED +
            "; color: " + PASTEL_RED + "; padding: 10px; font-size: 14px; }"
            "QPushButton:hover { background-color: #1a0000; }"
        )

        def r_from_alt(alt_km, Re_km): return Re_km + alt_km

        Re = earth_Re
        GEO_alt = 35786.0
        GEO_r   = r_from_alt(GEO_alt, Re)
        LEO200  = r_from_alt(200.0, Re)
        LEO400  = r_from_alt(400.0, Re)
        MEO20000= 20000.0

        presets = [
            ("Earth defaults + LEO(400 km) → GEO",   earth_mu, Re, LEO400, GEO_r),
            ("Earth defaults + LEO(200 km) → GEO",   earth_mu, Re, LEO200, GEO_r),
            ("Earth defaults + LEO(400 km) → MEO(20,000 km)", earth_mu, Re, LEO400, MEO20000),
            ("Earth defaults + GEO → LEO(400 km)",   earth_mu, Re, GEO_r, LEO400),
            ("Earth defaults + ISS(408 km) → GEO",   earth_mu, Re, r_from_alt(408.0, Re), GEO_r),
        ]

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addSpacing(6)

        for name, mu, re, r1, r2 in presets:
            b = QPushButton(name)
            b.setStyleSheet(btn_style)
            b.setFont(QFont(font_family, 12))
            def make_handler(mu0, re0, r10, r20):
                def handler():
                    self.apply_cb(mu0, re0, r10, r20)
                    self.accept()
                return handler
            b.clicked.connect(make_handler(mu, re, r1, r2))
            layout.addWidget(b)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_box.rejected.connect(self.reject)
        close_box.button(QDialogButtonBox.Close).setStyleSheet(
            "QPushButton { background-color: rgba(0,0,0,150); border: 2px solid " + PASTEL_RED +
            "; color: " + PASTEL_RED + "; padding: 8px 12px; font-size: 14px; }"
            "QPushButton:hover { background-color: #1a0000; }"
        )

        layout.addSpacing(8)
        layout.addWidget(close_box, alignment=Qt.AlignRight)
        self.setLayout(layout)

# About
class AboutDialog(QDialog):
    def __init__(self, font_family, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)
        self.setMinimumWidth(520)

        title = QLabel("PROJECT AUTHOR")
        title.setFont(QFont(font_family, 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: " + PASTEL_RED + ";")

        author = QLabel("Author: Eng. Mateusz Witczak")
        contact = QLabel("Contact: mati.witczak@icloud.com | mateusz.witczak.stud@pw.edu.pl")
        for w in (author, contact):
            w.setFont(QFont(font_family, 12))
            w.setStyleSheet("color: rgba(255,102,102,220);")

        # Project description
        desc = QLabel(
            "Designed and implemented an engineering tool for spacecraft trajectory analysis and maneuver planning. "
            "The application simulates orbital transfers, Δv requirements, and parameter evolution, supporting mission "
            "design and aerospace engineering workflows."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        desc.setFont(QFont(font_family, 12))
        desc.setStyleSheet("color: rgba(255,102,102,200);")

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        btns.accepted.connect(self.accept)
        btns.button(QDialogButtonBox.Close).setStyleSheet(
            "QPushButton { background-color: rgba(0,0,0,150); border: 2px solid " + PASTEL_RED +
            "; color: " + PASTEL_RED + "; padding: 8px 12px; font-size: 14px; }"
            "QPushButton:hover { background-color: #1a0000; }"
        )

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(author)
        layout.addWidget(contact)
        layout.addSpacing(10)
        layout.addWidget(desc)
        layout.addSpacing(12)
        layout.addWidget(btns, alignment=Qt.AlignRight)
        self.setLayout(layout)


# Clear
class OrbitCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(7.6, 5.6), dpi=100, facecolor='none')
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111, facecolor='none')
        self.setStyleSheet("background: transparent;")
        self._setup_style()
        self.reset_empty()

    def _setup_style(self):
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_xlabel('x [km]', color=PASTEL_RED, labelpad=10)
        self.ax.set_ylabel('y [km]', color=PASTEL_RED, labelpad=10)
        self.ax.tick_params(colors=PASTEL_RED, which='both', labelsize=11)
        for spine in self.ax.spines.values():
            spine.set_color(PASTEL_RED); spine.set_alpha(0.6); spine.set_linewidth(1.0)
        self.ax.grid(True, color=PASTEL_RED, alpha=0.15, linewidth=0.9)
        self.fig.subplots_adjust(right=0.83, left=0.09, top=0.95, bottom=0.10)

    def reset_empty(self):
        self.ax.clear()
        self._setup_style()
        self.draw()

    def draw_earth(self, Re_km):
        th = np.linspace(0, 2*np.pi, 360)
        x = Re_km*np.cos(th); y = Re_km*np.sin(th)
        self.ax.fill(x, y, facecolor=(1.0, 0.4, 0.4, 0.14),
                     edgecolor=PASTEL_RED, linewidth=2, alpha=0.9, label='Earth')

    def draw_circle_orbit(self, r_km, label='Orbit', color=None, lw=2.0):
        th = np.linspace(0, 2*np.pi, 720)
        x = r_km*np.cos(th); y = r_km*np.sin(th)
        col = color or '#ff9999'
        self.ax.plot(x, y, linewidth=lw, color=col, label=label)

    def draw_ellipse(self, a_km, e, label='Transfer', color='#ff4d4d', lw=2.2):
        th = np.linspace(0, 2*np.pi, 720)
        r = (a_km*(1 - e**2)) / (1 + e*np.cos(th))
        x = r*np.cos(th); y = r*np.sin(th)
        self.ax.plot(x, y, linestyle='--', linewidth=lw, color=color, label=label)

    def add_marker(self, x, y, size=60, edge=PASTEL_RED, face=(1.0, 0.4, 0.4, 0.25)):
        self.ax.scatter([x], [y], s=size, facecolor=face,
                        edgecolor=edge, linewidths=1.8, zorder=5)

    def add_dv_arrow(self, x, y, dx, dy, label_text, color="#ff4d4d"):
        self.ax.annotate("", xy=(x+dx, y+dy), xytext=(x, y),
                         arrowprops=dict(arrowstyle='-|>', color=color, lw=2.2, alpha=0.95),
                         zorder=6)
        self.ax.text(x+dx*1.05, y+dy*1.05, label_text,
                     color=color, fontsize=11, ha='left', va='bottom')

    def finalize(self, r1_km=None, r2_km=None, custom_handles=None):
        lim = 1.2*max([v for v in [r1_km, r2_km] if v is not None] + [7000])
        self.ax.set_xlim(-lim, lim); self.ax.set_ylim(-lim, lim)
        handles, labels = self.ax.get_legend_handles_labels()
        if custom_handles:
            handles += custom_handles
            labels += [h.get_label() for h in custom_handles]
        if handles:
            leg = self.ax.legend(handles, labels,
                                 loc='upper left', bbox_to_anchor=(1.02, 1.0),
                                 facecolor=(0, 0, 0, 0.6), edgecolor=PASTEL_RED,
                                 framealpha=0.6, borderaxespad=0.8)
            for text in leg.get_texts():
                text.set_color(PASTEL_RED)
        self.draw()

# UI
class StarWarsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_fonts()
        self.init_defaults()
        self.initUI()

    def init_fonts(self):
        self.sw_font_family = "Aurebesh"
        font_path = os.path.join(os.path.dirname(__file__), "Aurebesh.ttf")
        if os.path.exists(font_path):
            fid = QFontDatabase.addApplicationFont(font_path)
            if fid != -1:
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    self.sw_font_family = fams[0]
                else:
                    self.sw_font_family = "Arial"
            else:
                self.sw_font_family = "Arial"
        else:
            self.sw_font_family = "Arial"

    def init_defaults(self):
        self.mu = 3.986004418e14
        self.Re = 6371.0
        self.r1 = 7000.0
        self.r2 = 42164.0

    def initUI(self):
        self.setWindowTitle("Orbital Mechanics Transfer Analyzer")
        self.resize(1400, 860)

        # background
        bg_path = os.path.join(os.path.dirname(__file__), "stars_bg.jpg")
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(0, 0, 0))
        if os.path.exists(bg_path):
            pal.setBrush(QPalette.Window, QPixmap(bg_path))
        pal.setColor(QPalette.WindowText, QColor(PASTEL_RED))
        self.setPalette(pal)

        # Header
        title = QLabel("Orbital Mechanics Transfer Analyzer")
        title.setFont(QFont(self.sw_font_family, 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: " + PASTEL_RED + "; background: transparent;")
        apply_glow(title)

        sub = QLabel("ORBITAL MECHANICS • ASTRODYNAMICS • AEROSPACE ENGINEERING")
        sub.setFont(QFont(self.sw_font_family, 14))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: rgba(255,102,102,180); background: transparent;")
        apply_glow(sub)

        # Buttons
        btn_style = (
            "QPushButton { background-color: rgba(0,0,0,150); border: 2px solid " + PASTEL_RED +
            "; color: " + PASTEL_RED + "; padding: 12px 16px; font-size: 16px; }"
            "QPushButton:hover { background-color: #1a0000; }"
        )
        self.btn_params = QPushButton("PARAMETERS")
        self.btn_presets= QPushButton("PRESETS")
        self.btn_draw   = QPushButton("DRAW ORBIT")
        self.btn_hoh    = QPushButton("HOHMANN TRANSFER")
        self.btn_clr    = QPushButton("CLEAR")
        self.btn_about  = QPushButton("ABOUT")

        for b in (self.btn_params, self.btn_presets, self.btn_draw, self.btn_hoh, self.btn_clr, self.btn_about):
            b.setFont(QFont(self.sw_font_family, 13, QFont.Bold))
            b.setStyleSheet(btn_style)
            apply_glow(b)

        btn_col = QVBoxLayout()
        for b in (self.btn_params, self.btn_presets, self.btn_draw, self.btn_hoh, self.btn_clr, self.btn_about):
            btn_col.addWidget(b)

        # Results
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet(
            "QFrame { background-color: rgba(0,0,0,140); border: 2px solid " + PASTEL_RED + "; border-radius: 8px; }")
        results_layout = QVBoxLayout()
        results_title = QLabel("RESULTS")
        results_title.setFont(QFont(self.sw_font_family, 18, QFont.Bold))
        results_title.setAlignment(Qt.AlignCenter)
        results_title.setStyleSheet("color: " + PASTEL_RED + ";")
        apply_glow(results_title)

        self.res_dv1   = QLabel("Δv1 = — km/s")
        self.res_dv2   = QLabel("Δv2 = — km/s")
        self.res_dvtot = QLabel("Δv_tot = — km/s")
        self.res_time  = QLabel("t_trans = — h")
        for w in (self.res_dv1, self.res_dv2, self.res_dvtot, self.res_time):
            w.setFont(QFont(self.sw_font_family, 15))
            w.setAlignment(Qt.AlignCenter)
            w.setStyleSheet("color: rgba(255,102,102,220);")

        results_layout.addWidget(results_title)
        results_layout.addWidget(self.res_dv1)
        results_layout.addWidget(self.res_dv2)
        results_layout.addWidget(self.res_dvtot)
        results_layout.addWidget(self.res_time)

        self.results_frame.setLayout(results_layout)
        apply_glow(self.results_frame, blur=25)

        btn_col.addSpacing(10)
        btn_col.addWidget(self.results_frame)
        btn_col.addStretch(1)

        
        self.canvas = OrbitCanvas()

        # Layout
        header = QVBoxLayout(); header.addWidget(title); header.addWidget(sub)
        mid = QHBoxLayout(); mid.addLayout(btn_col, 0); mid.addWidget(self.canvas, 1)
        root = QVBoxLayout(); root.addLayout(header); root.addLayout(mid)
        self.setLayout(root)

        # Signals
        self.btn_params.clicked.connect(self.open_params)
        self.btn_presets.clicked.connect(self.open_presets)
        self.btn_draw.clicked.connect(self.on_draw_orbits)
        self.btn_hoh.clicked.connect(self.on_hohmann)
        self.btn_clr.clicked.connect(self.on_clear)
        self.btn_about.clicked.connect(self.open_about)

        self.on_clear()

    # Parameters
    def open_params(self):
        dlg = ParamDialog(self.sw_font_family, self.mu, self.Re, self.r1, self.r2, parent=self)
        if dlg.exec_() == QDialog.Accepted:
            mu_txt, Re_txt, r1_txt, r2_txt = dlg.values()
            try:
                mu = float(mu_txt); Re = float(Re_txt); r1 = float(r1_txt); r2 = float(r2_txt)
                if min(Re, r1, r2) <= 0: raise ValueError("All distances must be > 0.")
                if r1 <= Re or r2 <= Re: raise ValueError("Orbits must be above Earth radius.")
                self.mu, self.Re, self.r1, self.r2 = mu, Re, r1, r2
            except Exception as e:
                QMessageBox.warning(self, "Input error", "Check inputs.\n\nDetails: {}".format(e), QMessageBox.Ok)

    def open_presets(self):
        def apply_cb(mu, Re, r1, r2):
            self.mu, self.Re, self.r1, self.r2 = mu, Re, r1, r2
        dlg = PresetDialog(self.sw_font_family, 3.986004418e14, 6371.0, apply_cb, parent=self)
        dlg.exec_()

    def open_about(self):
        AboutDialog(self.sw_font_family, parent=self).exec_()

    # Drawing
    def on_draw_orbits(self):
        self.canvas.reset_empty()
        self.canvas.draw_earth(self.Re)
        self.canvas.draw_circle_orbit(self.r1, label="Orbit r1={:.0f} km".format(self.r1), color="#ff9999")
        self.canvas.draw_circle_orbit(self.r2, label="Orbit r2={:.0f} km".format(self.r2), color="#ff4d4d")
        self.canvas.finalize(self.r1, self.r2)
        self._reset_results_labels()

    def on_hohmann(self):
        try:
            mu_km = self.mu / (1000.0**3)
            r1, r2 = self.r1, self.r2
            a_trans = 0.5*(r1 + r2)
            e_trans = abs(r2 - r1) / (r1 + r2)
            v1 = np.sqrt(mu_km / r1); v2 = np.sqrt(mu_km / r2)
            v_peri = np.sqrt(mu_km*(2/r1 - 1/a_trans))
            v_apo  = np.sqrt(mu_km*(2/r2 - 1/a_trans))
            dv1 = abs(v_peri - v1); dv2 = abs(v2 - v_apo); dv_tot = dv1 + dv2
            T_trans = np.pi * np.sqrt((a_trans**3) / mu_km)
        except Exception as e:
            QMessageBox.warning(self, "Computation error", "Failed to compute transfer.\n\n{}".format(e), QMessageBox.Ok)
            return

        self.canvas.reset_empty()
        self.canvas.draw_earth(self.Re)
        self.canvas.draw_circle_orbit(self.r1, label="r1={:.0f} km".format(self.r1), color="#ff9999")
        self.canvas.draw_circle_orbit(self.r2, label="r2={:.0f} km".format(self.r2), color="#ff4d4d")
        self.canvas.draw_ellipse(a_trans, e_trans, label="Hohmann transfer", color="#ff4d4d")

        x1, y1 = r1, 0.0; x2, y2 = -r2, 0.0
        self.canvas.add_marker(x1, y1); self.canvas.add_marker(x2, y2)
        lim = 1.2*max(self.r1, self.r2); scale = 0.02 * lim
        L1 = scale * dv1; L2 = scale * dv2
        self.canvas.add_dv_arrow(x1, y1, 0.0, +L1, "Δv₁ = {:.3f} km/s".format(dv1))
        self.canvas.add_dv_arrow(x2, y2, 0.0, -L2, "Δv₂ = {:.3f} km/s".format(dv2))
        self.canvas.finalize(self.r1, self.r2, custom_handles=[Line2D([0],[0], color='#ff4d4d', lw=2, label='Δv vectors')])

        # Results
        self.res_dv1.setText("Δv1 = {:.3f} km/s".format(dv1))
        self.res_dv2.setText("Δv2 = {:.3f} km/s".format(dv2))
        self.res_dvtot.setText("Δv_tot = {:.3f} km/s".format(dv_tot))
        self.res_time.setText("t_trans = {:.2f} h".format(T_trans/3600.0))

    def on_clear(self):
        self.canvas.reset_empty()
        self._reset_results_labels()

    def _reset_results_labels(self):
        self.res_dv1.setText("Δv1 = — km/s")
        self.res_dv2.setText("Δv2 = — km/s")
        self.res_dvtot.setText("Δv_tot = — km/s")
        self.res_time.setText("t_trans = — h")

# Run
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = StarWarsUI()
    ui.show()
    sys.exit(app.exec_())
