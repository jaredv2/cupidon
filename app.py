#!/usr/bin/env python3
"""
Cupidon — 2D Game Editor for Love2D
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fixed in this version:
  - Background color change no longer crashes (scene re-init avoided)
  - Icons scaled up properly in asset manager
  - All dock panels have real close buttons
  - Inspector opens in dock, not floating center
  - Drawing artifacts fixed: gizmo uses prepareGeometryChange correctly
  - Gizmo always visible on selected entity, all modes working
  - Scrub sensitivity configurable, default speed increased
  - Camera entity with follow_target (no Camera component, uses CameraFollow)
  - AABB collision system in Lua output
  - Collision outlines always shown in editor, enhanced in debug mode
"""
import sys, os, json, subprocess, uuid, math, shutil, copy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

print("[DEBUG] ── Cupidon starting ──")

# ═══════════════════════════════════════════════════════════════════════════════
# STYLESHEET
# ═══════════════════════════════════════════════════════════════════════════════
DARK_QSS = """
* { font-family: 'Segoe UI', 'Ubuntu', sans-serif; font-size: 12px; color: #d4d4d4; }
QMainWindow, QDialog { background: #1e1e1e; }
QMenuBar { background: #2d2d2d; border-bottom: 1px solid #3a3a3a; padding: 2px; }
QMenuBar::item { padding: 4px 10px; border-radius: 3px; }
QMenuBar::item:selected { background: #0e639c; color: white; }
QMenu { background: #252526; border: 1px solid #454545; padding: 4px; }
QMenu::item { padding: 6px 24px 6px 24px; border-radius: 3px; }
QMenu::item:selected { background: #094771; color: white; }
QMenu::separator { background: #3a3a3a; height: 1px; margin: 4px 8px; }
QToolBar { background: #2d2d2d; border: none; border-bottom: 1px solid #3a3a3a; spacing: 3px; padding: 4px 8px; }
QToolBar::separator { background: #3a3a3a; width: 1px; margin: 4px 3px; }
QToolButton { background: transparent; border: 1px solid transparent; border-radius: 4px;
              padding: 5px 10px; color: #d4d4d4; font-size: 13px; min-width: 28px; min-height: 28px; }
QToolButton:hover { background: #3a3a3a; border-color: #555; }
QToolButton:checked { background: #094771; border-color: #0e639c; color: white; }
QToolButton:pressed { background: #0d3a5c; }
QPushButton { background: #3a3a3a; border: 1px solid #555; border-radius: 4px;
              padding: 5px 14px; color: #d4d4d4; }
QPushButton:hover { background: #454545; border-color: #666; }
QPushButton:pressed { background: #2a2a2a; }
QPushButton:disabled { color: #555; background: #2a2a2a; }
QPushButton#run_btn { background: #1e4d1e; border-color: #2d7a2d; color: #7cdb7c; font-weight: bold; font-size: 13px; }
QPushButton#run_btn:hover { background: #265026; }
QPushButton#stop_btn { background: #4d1e1e; border-color: #7a2d2d; color: #db7c7c; font-weight: bold; }
QDockWidget { font-size: 12px; }
QDockWidget::title { background: #2d2d2d; color: #c8c8c8; padding: 6px 8px;
                     font-weight: bold; border-bottom: 1px solid #3a3a3a;
                     font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
QDockWidget::close-button { subcontrol-position: top right; subcontrol-origin: margin;
                             position: absolute; top: 4px; right: 4px;
                             width: 16px; height: 16px; }
QGroupBox { background: #252526; border: 1px solid #3a3a3a; border-radius: 4px; margin-top: 14px; padding: 8px 6px 6px 6px; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 2px 6px;
                   background: #094771; color: white; border-radius: 3px; font-size: 11px; font-weight: bold; }
QScrollArea { background: #1e1e1e; border: none; }
QScrollBar:vertical { background: #1e1e1e; width: 8px; border: none; }
QScrollBar::handle:vertical { background: #4a4a4a; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #666; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1e1e1e; height: 8px; border: none; }
QScrollBar::handle:horizontal { background: #4a4a4a; border-radius: 4px; min-width: 20px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QTreeWidget, QListWidget { background: #252526; border: 1px solid #3a3a3a; border-radius: 4px; outline: none; }
QTreeWidget::item, QListWidget::item { padding: 4px 4px; border-radius: 3px; }
QTreeWidget::item:hover, QListWidget::item:hover { background: #2a2d2e; }
QTreeWidget::item:selected, QListWidget::item:selected { background: #094771; color: white; }
QLineEdit, QTextEdit { background: #3c3c3c; border: 1px solid #555; border-radius: 4px;
                       padding: 3px 6px; selection-background-color: #094771; }
QLineEdit:focus, QTextEdit:focus { border-color: #0e639c; }
QSpinBox, QDoubleSpinBox { background: #3c3c3c; border: 1px solid #555; border-radius: 4px; padding: 2px 4px; }
QSpinBox::up-button, QDoubleSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::down-button
    { background: #4a4a4a; border: none; width: 16px; }
QComboBox { background: #3c3c3c; border: 1px solid #555; border-radius: 4px; padding: 3px 8px; }
QComboBox::drop-down { background: transparent; border: none; width: 20px; }
QComboBox QAbstractItemView { background: #252526; border: 1px solid #3a3a3a; selection-background-color: #094771; }
QCheckBox::indicator { width: 16px; height: 16px; background: #3c3c3c; border: 1px solid #555; border-radius: 3px; }
QCheckBox::indicator:checked { background: #0e639c; border-color: #0e639c; }
QTabWidget::pane { background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; }
QTabBar::tab { background: #2d2d2d; border: none; padding: 7px 18px;
               border-top-left-radius: 4px; border-top-right-radius: 4px; color: #888; }
QTabBar::tab:selected { background: #1e1e1e; color: #d4d4d4; border-bottom: 2px solid #0e639c; }
QTabBar::tab:hover { background: #3a3a3a; color: #d4d4d4; }
QStatusBar { background: #007acc; color: white; border: none; font-size: 11px; }
QStatusBar::item { border: none; }
QSplitter::handle { background: #3a3a3a; }
QHeaderView::section { background: #2d2d2d; border: none; border-bottom: 1px solid #3a3a3a;
                       padding: 4px 8px; font-weight: bold; font-size: 11px; }
"""

# ═══════════════════════════════════════════════════════════════════════════════
# ECS COMPONENT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════
# "Camera" removed as a component. Camera is now a special entity type.
COMPONENT_REGISTRY = {
    "Transform":        {"x": 0.0, "y": 0.0, "rotation": 0.0, "scale_x": 1.0, "scale_y": 1.0},
    "Sprite":           {"texture": "", "color": "#4488FF", "width": 64, "height": 64,
                         "flip_x": False, "flip_y": False, "opacity": 1.0, "layer": 0},
    "Rigidbody":        {"mass": 1.0, "gravity_scale": 1.0, "is_static": False,
                         "linear_damping": 0.1, "vx": 0.0, "vy": 0.0},
    "BoxCollider":      {"offset_x": 0.0, "offset_y": 0.0, "width": 64.0, "height": 64.0, "is_trigger": False},
    "CircleCollider":   {"offset_x": 0.0, "offset_y": 0.0, "radius": 32.0, "is_trigger": False},
    "PlayerController": {"speed": 200.0, "jump_force": 400.0,
                         "up_key": "w", "down_key": "s", "left_key": "a", "right_key": "d", "jump_key": "space"},
    "CameraFollow":     {"target": "", "zoom": 1.0, "smooth": True, "smooth_speed": 5.0,
                         "offset_x": 0.0, "offset_y": 0.0},
    "Animator":         {"current_anim": "", "frame_rate": 12, "loop": True},
    "AudioSource":      {"file": "", "volume": 1.0, "loop": False, "play_on_load": False},
    "Script":           {"file": "", "code": ""},
    "Light":            {"color": "#FFEEAA", "radius": 200.0, "intensity": 1.0},
    "ParticleEmitter":  {"rate": 20, "lifetime": 1.5, "speed": 100.0, "color": "#FF8800"},
}

FIELD_TYPES = {
    "x": "float", "y": "float", "rotation": "float", "scale_x": "float", "scale_y": "float",
    "width": "float", "height": "float", "radius": "float", "mass": "float",
    "gravity_scale": "float", "linear_damping": "float", "vx": "float", "vy": "float",
    "offset_x": "float", "offset_y": "float", "speed": "float", "jump_force": "float",
    "zoom": "float", "smooth_speed": "float", "frame_rate": "int", "volume": "float",
    "opacity": "float", "intensity": "float", "rate": "int", "lifetime": "float", "layer": "int",
    "is_trigger": "bool", "is_static": "bool", "flip_x": "bool", "flip_y": "bool",
    "loop": "bool", "play_on_load": "bool", "smooth": "bool",
    "texture": "str", "color": "color", "file": "str", "code": "text",
    "current_anim": "str",
    "target": "entity_ref",  # CameraFollow.target
    "up_key": "keybind", "down_key": "keybind", "left_key": "keybind",
    "right_key": "keybind", "jump_key": "keybind",
}

# ═══════════════════════════════════════════════════════════════════════════════
# ECS MODEL
# ═══════════════════════════════════════════════════════════════════════════════
class Entity:
    def __init__(self, name="Entity"):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.active = True
        self.is_camera = False   # special flag for camera entities
        self.components = {
            "Transform": copy.deepcopy(COMPONENT_REGISTRY["Transform"]),
            "Sprite":    copy.deepcopy(COMPONENT_REGISTRY["Sprite"]),
        }
        print(f"[DEBUG] Entity('{name}') id={self.id}")

    def add_component(self, name):
        if name not in self.components and name in COMPONENT_REGISTRY:
            self.components[name] = copy.deepcopy(COMPONENT_REGISTRY[name])
            print(f"[DEBUG] +Comp '{name}' → '{self.name}'")
            return True
        return False

    def remove_component(self, name):
        if name == "Transform":
            return False
        removed = self.components.pop(name, None) is not None
        print(f"[DEBUG] -Comp '{name}' from '{self.name}': {removed}")
        return removed

    def get(self, comp, field, default=None):
        return self.components.get(comp, {}).get(field, default)

    def set(self, comp, field, value):
        if comp in self.components:
            self.components[comp][field] = value

    def to_dict(self):
        return {"id": self.id, "name": self.name, "active": self.active,
                "is_camera": self.is_camera, "components": self.components}

    @classmethod
    def from_dict(cls, d):
        e = cls.__new__(cls)
        e.id = d["id"]
        e.name = d["name"]
        e.active = d.get("active", True)
        e.is_camera = d.get("is_camera", False)
        e.components = d.get("components", {})
        return e


class Scene:
    def __init__(self):
        self.entities = {}
        self.order = []
        self.settings = {
            "title": "My Game", "width": 800, "height": 600,
            "gravity_x": 0.0, "gravity_y": 300.0,
            "background_color": "#222233",
            "target_fps": 60, "vsync": True, "fullscreen": False,
        }
        print("[DEBUG] Scene()")

    def add_entity(self, name="Entity", x=100.0, y=100.0):
        e = Entity(name)
        e.set("Transform", "x", x)
        e.set("Transform", "y", y)
        self.entities[e.id] = e
        self.order.append(e.id)
        return e

    def remove_entity(self, eid):
        self.entities.pop(eid, None)
        if eid in self.order:
            self.order.remove(eid)

    def get(self, eid):
        return self.entities.get(eid)

    def ordered(self):
        return [self.entities[i] for i in self.order if i in self.entities]

    def to_dict(self):
        return {"settings": self.settings, "order": self.order,
                "entities": {eid: e.to_dict() for eid, e in self.entities.items()}}

    def from_dict(self, d):
        self.settings.update(d.get("settings", {}))
        self.order = d.get("order", [])
        self.entities = {eid: Entity.from_dict(ed) for eid, ed in d.get("entities", {}).items()}
        print(f"[DEBUG] Scene.from_dict: {len(self.entities)} entities")

# ═══════════════════════════════════════════════════════════════════════════════
# UNDO STACK
# ═══════════════════════════════════════════════════════════════════════════════
class UndoStack:
    def __init__(self, max_steps=100):
        self._undo = []
        self._redo = []
        self._max  = max_steps

    def push(self, scene_dict, desc=""):
        self._undo.append((copy.deepcopy(scene_dict), desc))
        self._redo.clear()
        if len(self._undo) > self._max:
            self._undo.pop(0)
        print(f"[DEBUG] Undo push '{desc}' (depth={len(self._undo)})")

    def undo(self, current_dict):
        if len(self._undo) < 2:
            return None
        self._redo.append((copy.deepcopy(current_dict), ""))
        snap, desc = self._undo.pop()
        print(f"[DEBUG] Undo: '{desc}'")
        return snap

    def redo(self, current_dict):
        if not self._redo:
            return None
        self._undo.append((copy.deepcopy(current_dict), ""))
        snap, _ = self._redo.pop()
        print("[DEBUG] Redo")
        return snap

    def can_undo(self): return len(self._undo) >= 2
    def can_redo(self): return bool(self._redo)

# ═══════════════════════════════════════════════════════════════════════════════
# KEYBIND DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
LOVE_KEYS = {
    Qt.Key_W:"w", Qt.Key_A:"a", Qt.Key_S:"s", Qt.Key_D:"d",
    Qt.Key_Q:"q", Qt.Key_E:"e", Qt.Key_R:"r", Qt.Key_F:"f",
    Qt.Key_Up:"up", Qt.Key_Down:"down", Qt.Key_Left:"left", Qt.Key_Right:"right",
    Qt.Key_Space:"space", Qt.Key_Return:"return", Qt.Key_Escape:"escape",
    Qt.Key_Shift:"lshift", Qt.Key_Control:"lctrl", Qt.Key_Alt:"lalt",
    **{getattr(Qt, f"Key_{i}"): str(i) for i in range(10)},
    **{getattr(Qt, f"Key_F{i}"): f"f{i}" for i in range(1, 13)},
}

class KeybindDialog(QDialog):
    def __init__(self, current="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Assign Keybind")
        self.setFixedSize(300, 150)
        self.result_key = current
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        self._lbl = QLabel(f"Current: <b>{current or 'none'}</b><br><br>"
                           "Press any key to assign…")
        self._lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._lbl)
        btns = QDialogButtonBox(QDialogButtonBox.Cancel)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, e):
        k = LOVE_KEYS.get(e.key())
        if k:
            self.result_key = k
            self._lbl.setText(f"Assigned: <b>{k}</b>  ✓")
            print(f"[DEBUG] Keybind → '{k}'")
            QTimer.singleShot(350, self.accept)
        else:
            self._lbl.setText("Key not mapped — try another")

# ═══════════════════════════════════════════════════════════════════════════════
# SCRUB LABEL  (drag-to-change number field)
# FIX: increased default speed from 0.3 to 1.5 for floats, 2.0 for ints
# ═══════════════════════════════════════════════════════════════════════════════
class ScrubLabel(QLabel):
    """
    Drag left/right to change a numeric value (like Blender/Unreal).
    - Default speed = 1.5 per pixel for float, 2.0 for int
    - Shift held = 0.1x fine mode
    - Double-click = text entry mode
    """
    value_changed = pyqtSignal(float)

    def __init__(self, field, value=0.0, ftype="float"):
        super().__init__()
        self._field = field
        self._ftype = ftype
        self._value = float(value)
        self._base_speed = 2.0 if ftype == "int" else 1.5
        self._drag   = False
        self._sx     = 0
        self._sv     = 0.0

        self._edit = QLineEdit(self)
        self._edit.hide()
        self._edit.returnPressed.connect(self._commit)
        self._edit.editingFinished.connect(self._commit)

        self.setCursor(QCursor(Qt.SizeHorCursor))
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(24)
        self.setStyleSheet("""
            ScrubLabel {
                background: #3c3c3c; border: 1px solid #555; border-radius: 4px;
                color: #56b6c2; font-weight: bold; padding: 2px 6px;
            }
            ScrubLabel:hover { background: #484848; border-color: #0e639c; }
        """)
        self._refresh()

    def _refresh(self):
        if self._ftype == "int":
            self.setText(f"{int(self._value)}")
        else:
            self.setText(f"{self._value:.2f}")

    def setValue(self, v):
        self._value = float(v)
        self._refresh()

    def value(self):
        return int(self._value) if self._ftype == "int" else self._value

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = True
            self._sx   = e.globalPos().x()
            self._sv   = self._value
            self.grabMouse()

    def mouseMoveEvent(self, e):
        if self._drag:
            # Shift = fine mode (10× slower)
            speed = self._base_speed * (0.1 if e.modifiers() & Qt.ShiftModifier else 1.0)
            dx = e.globalPos().x() - self._sx
            nv = self._sv + dx * speed
            if self._ftype == "int":
                nv = int(nv)
            self._value = nv
            self._refresh()
            self.value_changed.emit(float(nv))

    def mouseReleaseEvent(self, e):
        if self._drag:
            self._drag = False
            self.releaseMouse()
            print(f"[DEBUG] Scrub '{self._field}' → {self._value}")

    def mouseDoubleClickEvent(self, e):
        self._edit.setGeometry(0, 0, self.width(), self.height())
        self._edit.setText(str(self.value()) if self._ftype != "int" else str(int(self._value)))
        self._edit.show()
        self._edit.setFocus()
        self._edit.selectAll()

    def _commit(self):
        try:
            nv = float(self._edit.text())
            if self._ftype == "int":
                nv = int(nv)
            self._value = nv
            self.value_changed.emit(float(nv))
        except ValueError:
            pass
        self._edit.hide()
        self._refresh()

    def resizeEvent(self, e):
        self._edit.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(e)

# ═══════════════════════════════════════════════════════════════════════════════
# GIZMO
# FIX: use scene-level QGraphicsItem (not ItemGroup), proper bounding rect,
#      prepareGeometryChange before every move, no stale paint artifacts.
# ═══════════════════════════════════════════════════════════════════════════════
class Gizmo(QGraphicsObject):
    """
    A QGraphicsObject drawn on top of the selected entity.
    Uses scene coordinates directly — no parent item tricks.
    Modes: move | rotate | scale
    """
    NONE = 0; DX = 1; DY = 2; DXY = 3; ROT = 4; SX = 5; SY = 6; SXY = 7

    A = 75   # arrow length
    H = 8    # handle half-size
    R = 55   # rotation ring radius

    def __init__(self, canvas):
        super().__init__()
        self.canvas    = canvas
        self.entity_id = None
        self.mode      = "move"   # move | rotate | scale
        self._drag     = self.NONE
        self._ds       = QPointF(0, 0)   # drag start scene pos
        self._sv       = (0.0,) * 5     # start transform values

        self.setZValue(9000)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations, False)
        self.hide()
        print("[DEBUG] Gizmo init")

    # ── geometry ─────────────────────────────────────────────────
    def boundingRect(self):
        r = max(self.A, self.R) + 20
        return QRectF(-r, -r, r * 2, r * 2)

    def attach(self, entity):
        self.prepareGeometryChange()
        self.entity_id = entity.id
        self.setPos(entity.get("Transform", "x", 0),
                    entity.get("Transform", "y", 0))
        self.show()
        self.update()

    def detach(self):
        self.entity_id = None
        self.hide()

    def sync(self, entity):
        if entity and entity.id == self.entity_id:
            self.prepareGeometryChange()
            self.setPos(entity.get("Transform", "x", 0),
                        entity.get("Transform", "y", 0))
            self.update()

    # ── paint ────────────────────────────────────────────────────
    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.mode == "move":
            self._p_move(painter)
        elif self.mode == "rotate":
            self._p_rotate(painter)
        elif self.mode == "scale":
            self._p_scale(painter)
        # center dot always
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#222"), 1))
        painter.drawEllipse(QPointF(0, 0), 5, 5)

    def _p_move(self, p):
        A = self.A
        # X (red)
        p.setPen(QPen(QColor("#e06c75"), 2.5))
        p.setBrush(QBrush(QColor("#e06c75")))
        p.drawLine(QPointF(0, 0), QPointF(A, 0))
        p.drawPolygon(QPolygonF([QPointF(A, 0), QPointF(A-12, -5), QPointF(A-12, 5)]))
        # Y (green)
        p.setPen(QPen(QColor("#98c379"), 2.5))
        p.setBrush(QBrush(QColor("#98c379")))
        p.drawLine(QPointF(0, 0), QPointF(0, -A))
        p.drawPolygon(QPolygonF([QPointF(0, -A), QPointF(-5, -A+12), QPointF(5, -A+12)]))
        # XY square
        p.setPen(QPen(QColor("#e5c07b"), 1.5))
        p.setBrush(QBrush(QColor(229, 192, 123, 70)))
        p.drawRect(QRectF(8, -22, 18, 18))

    def _p_rotate(self, p):
        R = self.R
        p.setPen(QPen(QColor("#61afef"), 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(0, 0), R, R)
        p.setBrush(QBrush(QColor("#61afef")))
        p.setPen(QPen(QColor("#1e1e1e"), 1))
        for deg in [0, 90, 180, 270]:
            rad = math.radians(deg)
            cx = R * math.cos(rad)
            cy = -R * math.sin(rad)
            p.drawEllipse(QPointF(cx, cy), 6, 6)

    def _p_scale(self, p):
        A = self.A
        p.setPen(QPen(QColor("#e06c75"), 2))
        p.setBrush(QBrush(QColor("#e06c75")))
        p.drawLine(QPointF(0, 0), QPointF(A, 0))
        p.drawRect(QRectF(A-7, -7, 14, 14))
        p.setPen(QPen(QColor("#98c379"), 2))
        p.setBrush(QBrush(QColor("#98c379")))
        p.drawLine(QPointF(0, 0), QPointF(0, -A))
        p.drawRect(QRectF(-7, -A-7, 14, 14))
        p.setPen(QPen(QColor("#e5c07b"), 2))
        p.setBrush(QBrush(QColor("#e5c07b")))
        diag = A * 0.65
        p.drawLine(QPointF(0, 0), QPointF(diag, -diag))
        p.drawEllipse(QPointF(diag, -diag), 6, 6)

    # ── hit test ─────────────────────────────────────────────────
    def _hit(self, p):
        A = self.A; H = self.H; R = self.R
        x, y = p.x(), p.y()
        if self.mode == "move":
            if QRectF(8, -22, 18, 18).contains(p):  return self.DXY
            if abs(x) < 8 and abs(y) < 8:           return self.DXY
            if abs(x - A) < H*2 and abs(y) < H*2:   return self.DX
            if abs(x) < H*2 and abs(y + A) < H*2:   return self.DY
            if 0 < x < A and abs(y) < 7:             return self.DX
            if abs(x) < 7 and -A < y < 0:            return self.DY
        elif self.mode == "rotate":
            d = math.hypot(x, y)
            if R - 14 < d < R + 14:                  return self.ROT
        elif self.mode == "scale":
            if abs(x - A) < H*2 and abs(y) < H*2:   return self.SX
            if abs(x) < H*2 and abs(y + A) < H*2:   return self.SY
            diag = A * 0.65
            if math.hypot(x - diag, y + diag) < 12: return self.SXY
        return self.NONE

    def hoverMoveEvent(self, e):
        cursors = {
            self.NONE: Qt.ArrowCursor, self.DX: Qt.SizeHorCursor,
            self.DY: Qt.SizeVerCursor, self.DXY: Qt.SizeAllCursor,
            self.ROT: Qt.CrossCursor, self.SX: Qt.SizeHorCursor,
            self.SY: Qt.SizeVerCursor, self.SXY: Qt.SizeFDiagCursor,
        }
        self.setCursor(QCursor(cursors.get(self._hit(e.pos()), Qt.ArrowCursor)))
        super().hoverMoveEvent(e)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            super().mousePressEvent(e); return
        hit = self._hit(e.pos())
        entity = self.canvas.scene.get(self.entity_id)
        if hit != self.NONE and entity:
            self._drag = hit
            self._ds   = e.scenePos()
            self._sv   = (
                entity.get("Transform", "x", 0),
                entity.get("Transform", "y", 0),
                entity.get("Transform", "rotation", 0),
                entity.get("Transform", "scale_x", 1),
                entity.get("Transform", "scale_y", 1),
            )
            e.accept()
        else:
            super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._drag == self.NONE:
            super().mouseMoveEvent(e); return
        entity = self.canvas.scene.get(self.entity_id)
        if not entity:
            return
        delta = e.scenePos() - self._ds
        dx, dy = delta.x(), delta.y()
        sx, sy, sr, ssx, ssy = self._sv
        snap = self.canvas.snap_size if self.canvas.snap_enabled else 0

        def snp(v):
            return round(v / snap) * snap if snap else v

        if self.mode == "move":
            if self._drag == self.DX:
                entity.set("Transform", "x", round(snp(sx + dx), 2))
            elif self._drag == self.DY:
                entity.set("Transform", "y", round(snp(sy + dy), 2))
            elif self._drag == self.DXY:
                entity.set("Transform", "x", round(snp(sx + dx), 2))
                entity.set("Transform", "y", round(snp(sy + dy), 2))
        elif self.mode == "rotate":
            angle = math.degrees(math.atan2(-(sy - e.scenePos().y()),
                                             e.scenePos().x() - sx))
            entity.set("Transform", "rotation", round(angle, 1))
        elif self.mode == "scale":
            s = 0.005
            if self._drag == self.SX:
                entity.set("Transform", "scale_x", max(0.01, round(ssx + dx * s, 3)))
            elif self._drag == self.SY:
                entity.set("Transform", "scale_y", max(0.01, round(ssy - dy * s, 3)))
            elif self._drag == self.SXY:
                ns = max(0.01, ssx + dx * s)
                entity.set("Transform", "scale_x", round(ns, 3))
                entity.set("Transform", "scale_y", round(ns, 3))

        self.sync(entity)
        self.canvas.refresh_visual(entity.id)
        self.canvas.entity_moved.emit(entity.id)
        e.accept()

    def mouseReleaseEvent(self, e):
        if self._drag != self.NONE:
            self._drag = self.NONE
            self.canvas.gizmo_drop.emit()
            e.accept()
        else:
            super().mouseReleaseEvent(e)

# ═══════════════════════════════════════════════════════════════════════════════
# COLLIDER VISUAL
# Always shown in editor. Brightened in debug mode.
# ═══════════════════════════════════════════════════════════════════════════════
class ColliderVisual(QGraphicsObject):
    def __init__(self, entity, comp_type, canvas):
        super().__init__()
        self.entity_id = entity.id
        self._comp     = comp_type
        self.canvas    = canvas
        self._data     = {}
        self.setZValue(500)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self._update_from(entity)

    def _update_from(self, entity):
        self.prepareGeometryChange()
        comp = entity.components.get(self._comp, {})
        ex   = entity.get("Transform", "x", 0)
        ey   = entity.get("Transform", "y", 0)
        ox   = comp.get("offset_x", 0)
        oy   = comp.get("offset_y", 0)
        self.setPos(ex + ox, ey + oy)
        self._data = dict(comp)
        self.update()

    def boundingRect(self):
        if self._comp == "BoxCollider":
            w = self._data.get("width", 64); h = self._data.get("height", 64)
            return QRectF(-w/2 - 3, -h/2 - 3, w + 6, h + 6)
        else:
            r = self._data.get("radius", 32)
            return QRectF(-r - 3, -r - 3, (r + 3) * 2, (r + 3) * 2)

    def paint(self, painter, option, widget=None):
        trig = self._data.get("is_trigger", False)
        debug = getattr(self.canvas, "debug_mode", False)
        base_alpha = 50 if debug else 25
        col  = QColor("#56b6c2") if trig else QColor("#98c379")
        pen  = QPen(col, 2 if debug else 1.5, Qt.DashLine if not debug else Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), base_alpha)))
        if self._comp == "BoxCollider":
            w = self._data.get("width", 64); h = self._data.get("height", 64)
            painter.drawRect(QRectF(-w/2, -h/2, w, h))
        else:
            r = self._data.get("radius", 32)
            painter.drawEllipse(QPointF(0, 0), r, r)

# ═══════════════════════════════════════════════════════════════════════════════
# CAMERA VISUAL (icon shown on canvas for camera entities)
# ═══════════════════════════════════════════════════════════════════════════════
class CameraVisual(QGraphicsObject):
    def __init__(self, entity, canvas):
        super().__init__()
        self.entity_id = entity.id
        self.canvas    = canvas
        self.setZValue(600)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setPos(entity.get("Transform", "x", 0),
                    entity.get("Transform", "y", 0))

    def boundingRect(self):
        return QRectF(-28, -18, 56, 36)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#e5c07b"), 2))
        painter.setBrush(QBrush(QColor(229, 192, 123, 80)))
        painter.drawRoundedRect(QRectF(-20, -12, 30, 24), 4, 4)
        painter.setBrush(QBrush(QColor(97, 175, 239, 150)))
        painter.drawEllipse(QPointF(9, 0), 9, 9)
        painter.setPen(QPen(QColor("#e5c07b"), 1.2, Qt.DotLine))
        painter.drawLine(QPointF(16, -6), QPointF(26, -16))
        painter.drawLine(QPointF(16,  6), QPointF(26,  16))
        painter.drawLine(QPointF(26, -16), QPointF(26, 16))
        # Label
        painter.setPen(QPen(QColor("#e5c07b")))
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(QPointF(-18, 24), "CAM")

    def sync(self, entity):
        self.prepareGeometryChange()
        self.setPos(entity.get("Transform", "x", 0),
                    entity.get("Transform", "y", 0))
        self.update()

# ═══════════════════════════════════════════════════════════════════════════════
# ENTITY VISUAL
# FIX: prepareGeometryChange() called before size changes, no stale outlines
# ═══════════════════════════════════════════════════════════════════════════════
class EntityVisual(QGraphicsObject):
    def __init__(self, entity, canvas):
        super().__init__()
        self.entity_id = entity.id
        self.canvas    = canvas
        self._w = 64; self._h = 64
        self._color   = QColor("#4488FF")
        self._name    = entity.name
        self._active  = entity.active
        self._is_cam  = entity.is_camera
        self._texture = None
        self._hovered = False

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self._apply(entity)

    def _apply(self, entity):
        """Read all visual properties from entity data."""
        self.prepareGeometryChange()
        self._name   = entity.name
        self._active = entity.active
        self._is_cam = entity.is_camera
        sp = entity.components.get("Sprite", {})
        self._w     = max(1, sp.get("width",  64))
        self._h     = max(1, sp.get("height", 64))
        self._color = QColor(sp.get("color", "#4488FF"))

        # Load texture
        tex = sp.get("texture", "")
        self._texture = None
        if tex:
            adir = getattr(self.canvas, "_assets_dir", "")
            for root in [adir, "."]:
                p = os.path.join(root, tex) if root else tex
                if os.path.isfile(p):
                    pm = QPixmap(p)
                    if not pm.isNull():
                        self._texture = pm.scaled(
                            int(self._w), int(self._h),
                            Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                    break

        t = entity.components.get("Transform", {})
        self.setPos(t.get("x", 0), t.get("y", 0))
        self.setRotation(t.get("rotation", 0))
        sx = t.get("scale_x", 1); sy = t.get("scale_y", 1)
        self.setTransform(QTransform().scale(sx, sy))

    def boundingRect(self):
        pad = 4
        return QRectF(-self._w/2 - pad, -self._h/2 - pad,
                      self._w + pad*2, self._h + pad*2)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        if self._is_cam:
            return  # camera visual handled by CameraVisual
        alpha = 255 if self._active else 90
        rect  = QRectF(-self._w/2, -self._h/2, self._w, self._h)

        if self._texture:
            painter.setOpacity(alpha / 255)
            painter.drawPixmap(int(-self._w/2), int(-self._h/2), self._texture)
            painter.setOpacity(1.0)
        else:
            c = QColor(self._color)
            c.setAlpha(alpha)
            painter.setBrush(QBrush(c))
            if self.isSelected():
                painter.setPen(QPen(QColor("#61afef"), 2))
            elif self._hovered:
                painter.setPen(QPen(QColor("#FFD700"), 2))
            else:
                painter.setPen(QPen(QColor("#cccccc"), 1))
            painter.drawRect(rect)

        if self.isSelected():
            painter.setPen(QPen(QColor("#61afef"), 1.5, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(QRectF(-self._w/2 - 3, -self._h/2 - 3,
                                    self._w + 6, self._h + 6))

        painter.setPen(QPen(QColor("#ffffff")))
        painter.setFont(QFont("Segoe UI", 7))
        painter.drawText(QPointF(-self._w/2 + 3, -self._h/2 + 11), self._name)

    def refresh(self, entity):
        self._apply(entity)
        self.update()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            pos = self.pos()
            e   = self.canvas.scene.get(self.entity_id)
            if e:
                e.set("Transform", "x", round(pos.x(), 2))
                e.set("Transform", "y", round(pos.y(), 2))
                self.canvas.entity_moved.emit(self.entity_id)
        return super().itemChange(change, value)

    def hoverEnterEvent(self, e):
        self._hovered = True;  self.update(); super().hoverEnterEvent(e)

    def hoverLeaveEvent(self, e):
        self._hovered = False; self.update(); super().hoverLeaveEvent(e)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.canvas.select_entity_signal.emit(self.entity_id)

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS
# ═══════════════════════════════════════════════════════════════════════════════
class Canvas(QGraphicsView):
    entity_moved         = pyqtSignal(str)
    select_entity_signal = pyqtSignal(str)
    gizmo_drop           = pyqtSignal()

    TOOL_SELECT = "select"
    TOOL_MOVE   = "move"
    TOOL_ROTATE = "rotate"
    TOOL_SCALE  = "scale"
    TOOL_HAND   = "hand"
    TOOL_ADD    = "add"

    def __init__(self, scene: Scene):
        self.gscene = QGraphicsScene()
        super().__init__(self.gscene)
        self.scene       = scene
        self.visuals     = {}   # eid -> EntityVisual
        self.colliders   = {}   # eid -> list[ColliderVisual]
        self.cam_visuals = {}   # eid -> CameraVisual
        self.tool        = self.TOOL_SELECT
        self.snap_enabled= False
        self.snap_size   = 16
        self.debug_mode  = False
        self._assets_dir = ""
        self._hint_item  = None

        w = scene.settings["width"]
        h = scene.settings["height"]
        self.gscene.setSceneRect(-500, -500, w + 1000, h + 1000)
        bg = QColor(scene.settings["background_color"])
        self.gscene.setBackgroundBrush(QBrush(bg))

        self.gizmo = Gizmo(self)
        self.gscene.addItem(self.gizmo)

        self._grid_items  = []
        self._border_items= []
        self._draw_grid()
        self._draw_border()

        self.gscene.selectionChanged.connect(self._on_sel_changed)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        print("[DEBUG] Canvas init")

    # ── background color ─────────────────────────────────────────
    def set_background(self, color_hex):
        """FIX: update only the background brush — do not re-init the scene."""
        self.gscene.setBackgroundBrush(QBrush(QColor(color_hex)))
        print(f"[DEBUG] Canvas bg → {color_hex}")

    # ── grid / border ─────────────────────────────────────────────
    def _draw_grid(self):
        for item in self._grid_items:
            self.gscene.removeItem(item)
        self._grid_items.clear()
        minor = QPen(QColor(70, 70, 80, 55), 0.5)
        major = QPen(QColor(90, 90, 100, 90), 1)
        for x in range(-2000, 2001, 16):
            pen = major if x % 128 == 0 else minor
            self._grid_items.append(self.gscene.addLine(x, -2000, x, 2000, pen))
        for y in range(-2000, 2001, 16):
            pen = major if y % 128 == 0 else minor
            self._grid_items.append(self.gscene.addLine(-2000, y, 2000, y, pen))
        for item in self._grid_items:
            item.setZValue(-100)

    def _draw_border(self):
        for item in self._border_items:
            self.gscene.removeItem(item)
        self._border_items.clear()
        w = self.scene.settings["width"]
        h = self.scene.settings["height"]
        r = self.gscene.addRect(0, 0, w, h, QPen(QColor("#0e639c"), 2),
                                QBrush(Qt.NoBrush))
        r.setZValue(-1)
        lbl = QGraphicsTextItem(
            f"  {self.scene.settings.get('title','Scene')}  ({w}×{h})")
        lbl.setDefaultTextColor(QColor("#0e639c"))
        lbl.setFont(QFont("Segoe UI", 9))
        lbl.setPos(0, -22)
        lbl.setZValue(-1)
        self.gscene.addItem(lbl)
        self._border_items.extend([r, lbl])

    # ── tools ─────────────────────────────────────────────────────
    def set_tool(self, tool):
        self.tool = tool
        self._hide_hint()
        if tool == self.TOOL_HAND:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor)
        elif tool == self.TOOL_ADD:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
            self._show_hint()
        elif tool == self.TOOL_SELECT:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.ArrowCursor)
            if self.gizmo.entity_id:
                self.gizmo.mode = tool
                self.gizmo.update()
        print(f"[DEBUG] tool → {tool}")

    def _show_hint(self):
        if self._hint_item:
            return
        lbl = QGraphicsTextItem("  Click to place entity  (Esc to cancel)")
        lbl.setDefaultTextColor(QColor("#e5c07b"))
        lbl.setFont(QFont("Segoe UI", 11))
        lbl.setPos(16, 16); lbl.setZValue(9999)
        self.gscene.addItem(lbl)
        self._hint_item = lbl

    def _hide_hint(self):
        if self._hint_item:
            self.gscene.removeItem(self._hint_item)
            self._hint_item = None

    def set_snap(self, enabled, size=16):
        self.snap_enabled = enabled
        self.snap_size    = size

    def set_debug(self, on):
        self.debug_mode = on
        # Refresh all collider visuals
        for eid, cv_list in self.colliders.items():
            for cv in cv_list:
                cv.update()
        print(f"[DEBUG] debug_mode={on}")

    # ── entity visuals ────────────────────────────────────────────
    def add_visual(self, entity):
        v = EntityVisual(entity, self)
        self.gscene.addItem(v)
        self.visuals[entity.id] = v
        self._rebuild_extras(entity)
        return v

    def remove_visual(self, eid):
        v = self.visuals.pop(eid, None)
        if v:
            self.gscene.removeItem(v)
        for c in self.colliders.pop(eid, []):
            self.gscene.removeItem(c)
        cv = self.cam_visuals.pop(eid, None)
        if cv:
            self.gscene.removeItem(cv)

    def refresh_visual(self, eid):
        v = self.visuals.get(eid)
        e = self.scene.get(eid)
        if v and e:
            v.refresh(e)
            self.gizmo.sync(e)
            self._rebuild_extras(e)

    def _rebuild_extras(self, entity):
        # Colliders — always show outlines in editor
        for c in self.colliders.pop(entity.id, []):
            self.gscene.removeItem(c)
        cv_list = []
        for ct in ("BoxCollider", "CircleCollider"):
            if ct in entity.components:
                cv = ColliderVisual(entity, ct, self)
                self.gscene.addItem(cv)
                cv_list.append(cv)
        self.colliders[entity.id] = cv_list

        # Camera visual
        old_cam = self.cam_visuals.pop(entity.id, None)
        if old_cam:
            self.gscene.removeItem(old_cam)
        if entity.is_camera:
            cam = CameraVisual(entity, self)
            self.gscene.addItem(cam)
            self.cam_visuals[entity.id] = cam

    def refresh_all(self):
        for v in self.visuals.values():
            self.gscene.removeItem(v)
        for cl in self.colliders.values():
            for c in cl:
                self.gscene.removeItem(c)
        for cv in self.cam_visuals.values():
            self.gscene.removeItem(cv)
        self.visuals.clear()
        self.colliders.clear()
        self.cam_visuals.clear()
        self._draw_border()
        for e in self.scene.ordered():
            self.add_visual(e)
        self.set_background(self.scene.settings["background_color"])
        print(f"[DEBUG] Canvas.refresh_all: {len(self.visuals)} visuals")

    def select_entity(self, eid):
        v = self.visuals.get(eid)
        if v:
            self.gscene.clearSelection()
            v.setSelected(True)
            e = self.scene.get(eid)
            if e:
                self.gizmo.mode = self.tool if self.tool in ("move","rotate","scale") else "move"
                self.gizmo.attach(e)

    def _on_sel_changed(self):
        sel = [i for i in self.gscene.selectedItems() if isinstance(i, EntityVisual)]
        if sel:
            eid = sel[0].entity_id
            e   = self.scene.get(eid)
            if e:
                self.gizmo.mode = self.tool if self.tool in ("move","rotate","scale") else "move"
                self.gizmo.attach(e)
                self.select_entity_signal.emit(eid)
        elif not self.gizmo._drag:
            self.gizmo.detach()

    # ── mouse / keyboard ─────────────────────────────────────────
    def mousePressEvent(self, e):
        if self.tool == self.TOOL_ADD and e.button() == Qt.LeftButton:
            sp  = self.mapToScene(e.pos())
            snp = lambda v: round(v / self.snap_size) * self.snap_size if self.snap_enabled else v
            ent = self.scene.add_entity(x=round(snp(sp.x()), 1),
                                        y=round(snp(sp.y()), 1))
            self.add_visual(ent)
            self._hide_hint()
            self.select_entity_signal.emit(ent.id)
            if hasattr(self, "_add_btn"):
                self._add_btn.setChecked(False)
            self.set_tool(self.TOOL_SELECT)
            return
        super().mousePressEvent(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape and self.tool == self.TOOL_ADD:
            self._hide_hint()
            self.set_tool(self.TOOL_SELECT)
            if hasattr(self, "_add_btn"):
                self._add_btn.setChecked(False)
        super().keyPressEvent(e)

    def wheelEvent(self, e):
        f = 1.15 if e.angleDelta().y() > 0 else 0.87
        self.scale(f, f)

# ═══════════════════════════════════════════════════════════════════════════════
# COMPONENT WIDGET
# ═══════════════════════════════════════════════════════════════════════════════
class ComponentWidget(QWidget):
    changed          = pyqtSignal(str, str, object)
    remove_requested = pyqtSignal(str)

    def __init__(self, comp_name, comp_data, scene=None):
        super().__init__()
        self.comp_name = comp_name
        self.comp_data = comp_data
        self._scene    = scene
        self._widgets  = {}
        self._collapsed= False
        self._build()

    def _build(self):
        self.setStyleSheet("background: #1e1e1e;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 2)
        outer.setSpacing(0)

        # Header bar
        hdr = QWidget()
        hdr.setStyleSheet("background:#2d2d2d; border-bottom:1px solid #3a3a3a;")
        hdr.setFixedHeight(28)
        hl  = QHBoxLayout(hdr)
        hl.setContentsMargins(8, 0, 6, 0)

        tog = QPushButton("▼")
        tog.setFixedSize(20, 20)
        tog.setStyleSheet("background:transparent;border:none;color:#aaa;font-size:10px;")
        tog.clicked.connect(self._toggle)
        hl.addWidget(tog)
        self._tog_btn = tog

        name_lbl = QLabel(self.comp_name)
        name_lbl.setStyleSheet("color:#e5c07b;font-weight:bold;font-size:11px;background:transparent;")
        hl.addWidget(name_lbl)
        hl.addStretch()

        if self.comp_name not in ("Transform",):
            rm = QPushButton("✕")
            rm.setFixedSize(20, 20)
            rm.setStyleSheet("background:transparent;border:none;color:#e06c75;font-size:11px;")
            rm.clicked.connect(lambda: self.remove_requested.emit(self.comp_name))
            hl.addWidget(rm)

        outer.addWidget(hdr)

        # Body
        self._body = QWidget()
        self._body.setStyleSheet("background:#1e1e1e;")
        grid = QGridLayout(self._body)
        grid.setContentsMargins(10, 6, 10, 8)
        grid.setSpacing(5)
        grid.setColumnStretch(1, 1)

        row = 0
        for field, val in self.comp_data.items():
            ftype = FIELD_TYPES.get(field, "str")
            lbl   = QLabel(field)
            lbl.setStyleSheet("color:#9da5b4;font-size:11px;background:transparent;")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid.addWidget(lbl, row, 0)

            w = self._make_widget(field, val, ftype)
            grid.addWidget(w, row, 1)
            self._widgets[field] = w
            row += 1

        outer.addWidget(self._body)

    def _make_widget(self, field, val, ftype):
        if ftype in ("float", "int"):
            w = ScrubLabel(field, val, ftype)
            w.value_changed.connect(lambda v, f=field: self._emit(f, v))
        elif ftype == "bool":
            w = QCheckBox()
            w.setChecked(bool(val))
            w.stateChanged.connect(lambda s, f=field: self._emit(f, bool(s)))
        elif ftype == "color":
            w = QPushButton(str(val))
            w.setFixedHeight(26)
            lc = QColor(val) if QColor(val).isValid() else QColor("#ffffff")
            w.setStyleSheet(f"background:{val};color:{'#000' if lc.lightness()>120 else '#fff'};border-radius:3px;")
            w.clicked.connect(lambda _, f=field, b=w: self._pick_color(f, b))
        elif ftype == "keybind":
            w = QPushButton(str(val) or "none")
            w.setFixedHeight(26)
            w.setStyleSheet("background:#3c3c3c;border:1px solid #555;border-radius:3px;font-weight:bold;color:#56b6c2;")
            w.clicked.connect(lambda _, f=field, b=w: self._pick_keybind(f, b))
        elif ftype == "entity_ref":
            w = QComboBox()
            w.addItem("(none)", "")
            if self._scene:
                for ent in self._scene.ordered():
                    w.addItem(ent.name, ent.id)
                    if ent.id == val:
                        w.setCurrentIndex(w.count() - 1)
            w.currentIndexChanged.connect(lambda _, f=field, cb=w: self._emit(f, cb.currentData() or ""))
        elif ftype == "text":
            w = QTextEdit()
            w.setPlainText(str(val))
            w.setMaximumHeight(72)
            w.textChanged.connect(lambda f=field, tw=w: self._emit(f, tw.toPlainText()))
        else:
            w = QLineEdit(str(val))
            w.textChanged.connect(lambda v, f=field: self._emit(f, v))
        return w

    def _toggle(self):
        self._collapsed = not self._collapsed
        self._body.setVisible(not self._collapsed)
        self._tog_btn.setText("►" if self._collapsed else "▼")

    def _emit(self, field, value):
        ftype = FIELD_TYPES.get(field, "str")
        if ftype == "float":  value = float(value)
        elif ftype == "int":  value = int(float(value))
        print(f"[DEBUG] Comp.{self.comp_name}.{field} = {value!r}")
        self.changed.emit(self.comp_name, field, value)

    def _pick_color(self, field, btn):
        cur = self.comp_data.get(field, "#ffffff")
        c   = QColorDialog.getColor(QColor(cur), self)
        if c.isValid():
            h = c.name()
            btn.setText(h)
            btn.setStyleSheet(f"background:{h};color:{'#000' if c.lightness()>120 else '#fff'};border-radius:3px;")
            self._emit(field, h)

    def _pick_keybind(self, field, btn):
        dlg = KeybindDialog(self.comp_data.get(field, ""), self)
        if dlg.exec_() == QDialog.Accepted:
            btn.setText(dlg.result_key)
            self._emit(field, dlg.result_key)

    def refresh(self, comp_data):
        for field, val in comp_data.items():
            w = self._widgets.get(field)
            if w is None: continue
            ftype = FIELD_TYPES.get(field, "str")
            if isinstance(w, ScrubLabel):
                w.blockSignals(True); w.setValue(float(val)); w.blockSignals(False)
            elif isinstance(w, QCheckBox):
                w.blockSignals(True); w.setChecked(bool(val)); w.blockSignals(False)
            elif isinstance(w, QPushButton) and ftype == "color":
                w.setText(str(val)); w.setStyleSheet(f"background:{val};border-radius:3px;")
            elif isinstance(w, QLineEdit):
                w.blockSignals(True); w.setText(str(val)); w.blockSignals(False)

# ═══════════════════════════════════════════════════════════════════════════════
# INSPECTOR  (FIX: opens in dock, not floating)
# ═══════════════════════════════════════════════════════════════════════════════
class InspectorPanel(QScrollArea):
    entity_changed = pyqtSignal(str)

    def __init__(self, scene=None):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._entity  = None
        self._comps   = {}
        self._scene   = scene
        self._top_row = None
        self._add_btn = None

        self._root = QWidget()
        self._root.setStyleSheet("background:#1e1e1e;")
        self._vbox = QVBoxLayout(self._root)
        self._vbox.setContentsMargins(0, 0, 0, 8)
        self._vbox.setSpacing(1)

        self._placeholder = QLabel("Select an entity\nto inspect its components.")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setStyleSheet("color:#454545;font-size:13px;padding:40px;")
        self._vbox.addWidget(self._placeholder)
        self._vbox.addStretch()
        self.setWidget(self._root)
        print("[DEBUG] InspectorPanel init")

    def load_entity(self, entity):
        """
        FIX: rebuild inspector in place inside the dock.
        Never call show() on a floating window.
        """
        self._entity = entity
        self._clear_all()
        self._placeholder.hide()

        # Name / active row
        top = QWidget(); top.setStyleSheet("background:#2d2d2d;")
        tl  = QHBoxLayout(top); tl.setContentsMargins(8, 6, 8, 6); tl.setSpacing(6)
        self._name_edit = QLineEdit(entity.name)
        self._name_edit.setStyleSheet("background:#3c3c3c;border:1px solid #555;"
                                      "border-radius:4px;font-weight:bold;font-size:13px;")
        self._name_edit.textChanged.connect(self._name_changed)
        tl.addWidget(self._name_edit, 1)
        self._active_cb = QCheckBox("Active")
        self._active_cb.setChecked(entity.active)
        self._active_cb.stateChanged.connect(lambda s: self._active_changed(bool(s)))
        tl.addWidget(self._active_cb)
        self._vbox.insertWidget(0, top)
        self._top_row = top

        # Component widgets
        idx = 1
        for cname, cdata in entity.components.items():
            cw = ComponentWidget(cname, cdata, self._scene)
            cw.changed.connect(self._comp_changed)
            cw.remove_requested.connect(self._remove_comp)
            self._vbox.insertWidget(idx, cw)
            self._comps[cname] = cw
            idx += 1

        # Add Component button
        ab = QPushButton("＋  Add Component")
        ab.setStyleSheet("background:#094771;border-radius:4px;padding:8px;margin:8px;")
        ab.clicked.connect(self._add_comp_menu)
        self._vbox.insertWidget(idx, ab)
        self._add_btn = ab
        print(f"[DEBUG] Inspector loaded '{entity.name}'")

    def _clear_all(self):
        if self._top_row:
            self._vbox.removeWidget(self._top_row)
            self._top_row.setParent(None)
            self._top_row = None
        for cw in self._comps.values():
            self._vbox.removeWidget(cw)
            cw.setParent(None)
        self._comps.clear()
        if self._add_btn:
            self._vbox.removeWidget(self._add_btn)
            self._add_btn.setParent(None)
            self._add_btn = None

    def clear(self):
        self._entity = None
        self._clear_all()
        self._placeholder.show()

    def _name_changed(self, v):
        if self._entity:
            self._entity.name = v
            self.entity_changed.emit(self._entity.id)

    def _active_changed(self, v):
        if self._entity:
            self._entity.active = v
            self.entity_changed.emit(self._entity.id)

    def _comp_changed(self, comp, field, value):
        if not self._entity: return
        self._entity.set(comp, field, value)
        self.entity_changed.emit(self._entity.id)

    def _remove_comp(self, name):
        if not self._entity: return
        self._entity.remove_component(name)
        cw = self._comps.pop(name, None)
        if cw:
            self._vbox.removeWidget(cw)
            cw.setParent(None)
        self.entity_changed.emit(self._entity.id)

    def _add_comp_menu(self):
        if not self._entity: return
        menu = QMenu(self)
        for name in COMPONENT_REGISTRY:
            if name not in self._entity.components:
                menu.addAction(name, lambda n=name: self._add_comp(n))
        if self._add_btn:
            menu.exec_(self._add_btn.mapToGlobal(QPoint(0, self._add_btn.height())))

    def _add_comp(self, name):
        if not self._entity: return
        if self._entity.add_component(name):
            self.load_entity(self._entity)
            self.entity_changed.emit(self._entity.id)

    def refresh_transform(self, entity):
        if self._entity and entity.id == self._entity.id:
            cw = self._comps.get("Transform")
            if cw:
                cw.refresh(entity.components.get("Transform", {}))

# ═══════════════════════════════════════════════════════════════════════════════
# HIERARCHY
# ═══════════════════════════════════════════════════════════════════════════════
class HierarchyPanel(QWidget):
    entity_selected   = pyqtSignal(str)
    entity_deleted    = pyqtSignal(str)
    entity_duplicated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#1e1e1e;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        hdr = QWidget(); hdr.setStyleSheet("background:#2d2d2d;border-bottom:1px solid #3a3a3a;")
        hl  = QHBoxLayout(hdr); hl.setContentsMargins(6, 4, 6, 4)
        self._search = QLineEdit(); self._search.setPlaceholderText("Filter entities…")
        self._search.textChanged.connect(self._filter)
        hl.addWidget(self._search)
        lay.addWidget(hdr)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._ctx)
        self._tree.currentItemChanged.connect(self._on_change)
        lay.addWidget(self._tree)
        print("[DEBUG] HierarchyPanel init")

    def refresh(self, scene: Scene):
        self._tree.blockSignals(True)
        cur_id = None
        if self._tree.currentItem():
            cur_id = self._tree.currentItem().data(0, Qt.UserRole)
        self._tree.clear()
        for e in scene.ordered():
            if e.is_camera:      icon = "📷"
            elif "PlayerController" in e.components: icon = "🎮"
            elif "Rigidbody" in e.components:        icon = "⚙"
            elif "BoxCollider" in e.components or "CircleCollider" in e.components: icon = "⬡"
            else:                                    icon = "◻"
            item = QTreeWidgetItem([f"  {icon}  {e.name}"])
            item.setData(0, Qt.UserRole, e.id)
            if not e.active:
                item.setForeground(0, QColor("#555"))
            self._tree.addTopLevelItem(item)
            if e.id == cur_id:
                self._tree.setCurrentItem(item)
        self._tree.blockSignals(False)

    def select(self, eid):
        self._tree.blockSignals(True)
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == eid:
                self._tree.setCurrentItem(item)
                break
        self._tree.blockSignals(False)

    def _on_change(self, cur, _):
        if cur:
            self.entity_selected.emit(cur.data(0, Qt.UserRole))

    def _filter(self, txt):
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            item.setHidden(txt.lower() not in item.text(0).lower())

    def _ctx(self, pos):
        cur = self._tree.currentItem()
        if not cur: return
        eid  = cur.data(0, Qt.UserRole)
        menu = QMenu(self)
        menu.addAction("Duplicate  (Ctrl+D)", lambda: self.entity_duplicated.emit(eid))
        menu.addSeparator()
        menu.addAction("Delete  (Del)", lambda: self.entity_deleted.emit(eid))
        menu.exec_(self._tree.viewport().mapToGlobal(pos))

# ═══════════════════════════════════════════════════════════════════════════════
# ASSET MANAGER  (FIX: larger icons 64px)
# ═══════════════════════════════════════════════════════════════════════════════
class AssetManagerPanel(QWidget):
    def __init__(self, project_dir=""):
        super().__init__()
        self.setStyleSheet("background:#1e1e1e;")
        self._project_dir = project_dir or os.path.join(os.path.expanduser("~"), "cupidon_projects", "default")
        self._assets_dir  = os.path.join(self._project_dir, "assets")
        os.makedirs(self._assets_dir, exist_ok=True)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)

        hdr = QWidget(); hdr.setStyleSheet("background:#2d2d2d;border-bottom:1px solid #3a3a3a;")
        hl  = QHBoxLayout(hdr); hl.setContentsMargins(8, 4, 8, 4); hl.setSpacing(6)
        hl.addWidget(QLabel("Project Assets"))
        hl.addStretch()
        ref = QPushButton("⟳"); ref.setFixedSize(26, 26); ref.clicked.connect(self.refresh)
        imp = QPushButton("Import…"); imp.setFixedHeight(26); imp.clicked.connect(self._import)
        hl.addWidget(ref); hl.addWidget(imp)
        lay.addWidget(hdr)

        self._tabs = QTabWidget()
        for cat in ["All", "Images", "Audio", "Scripts"]:
            lw = QListWidget()
            lw.setViewMode(QListWidget.IconMode)
            lw.setIconSize(QSize(64, 64))        # FIX: 64px icons (was 40px)
            lw.setGridSize(QSize(90, 90))
            lw.setResizeMode(QListWidget.Adjust)
            lw.setDragEnabled(True)
            lw.setContextMenuPolicy(Qt.CustomContextMenu)
            lw.customContextMenuRequested.connect(self._ctx)
            self._tabs.addTab(lw, cat)
        lay.addWidget(self._tabs)
        self.refresh()
        print(f"[DEBUG] AssetManager init {self._assets_dir}")

    def refresh(self):
        for i in range(4):
            self._tabs.widget(i).clear()
        if not os.path.isdir(self._assets_dir):
            return
        for fname in sorted(os.listdir(self._assets_dir)):
            fpath = os.path.join(self._assets_dir, fname)
            if not os.path.isfile(fpath):
                continue
            ext  = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            icon = self._make_icon(fpath, ext)
            for i, fn in enumerate([lambda: True,
                                     lambda: ext in ("png","jpg","jpeg","bmp","gif","webp"),
                                     lambda: ext in ("wav","ogg","mp3","flac"),
                                     lambda: ext in ("lua","json","txt")]):
                if fn():
                    item = QListWidgetItem(icon, fname[:12])
                    item.setData(Qt.UserRole, fpath)
                    item.setToolTip(fname)
                    self._tabs.widget(i).addItem(item)
        print(f"[DEBUG] Assets refreshed")

    def _make_icon(self, fpath, ext):
        if ext in ("png", "jpg", "jpeg", "bmp", "gif", "webp"):
            pm = QPixmap(fpath)
            if not pm.isNull():
                return QIcon(pm.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        colors = {"lua": "#61afef", "json": "#e5c07b",
                  "wav": "#c678dd", "ogg": "#c678dd", "mp3": "#c678dd"}
        col = colors.get(ext, "#555")
        pm  = QPixmap(64, 64); pm.fill(QColor(col))
        p   = QPainter(pm)
        p.setPen(Qt.white)
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.drawText(QRect(0, 0, 64, 64), Qt.AlignCenter, ext.upper() or "?")
        p.end()
        return QIcon(pm)

    def _import(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Import", "", "All Files (*)")
        for f in files:
            shutil.copy2(f, os.path.join(self._assets_dir, os.path.basename(f)))
            print(f"[DEBUG] Imported: {f}")
        self.refresh()

    def _ctx(self, pos):
        lw   = self.sender()
        item = lw.itemAt(pos) if lw else None
        if not item: return
        fpath = item.data(Qt.UserRole)
        menu  = QMenu(self)
        menu.addAction("Show in Files", lambda: subprocess.Popen(["xdg-open", os.path.dirname(fpath)]))
        menu.addAction("Delete", lambda: self._del(fpath))
        menu.exec_(lw.viewport().mapToGlobal(pos))

    def _del(self, fpath):
        if QMessageBox.question(self, "Delete", f"Delete {os.path.basename(fpath)}?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            os.remove(fpath); self.refresh()

    def set_project_dir(self, path):
        self._project_dir = path
        self._assets_dir  = os.path.join(path, "assets")
        os.makedirs(self._assets_dir, exist_ok=True)
        self.refresh()

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE SETTINGS DIALOG
# FIX: background color update calls canvas.set_background() only — no crash
# ═══════════════════════════════════════════════════════════════════════════════
class SceneSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scene Settings")
        self.setMinimumWidth(360)
        self._settings = dict(settings)
        lay = QFormLayout(self)
        lay.setLabelAlignment(Qt.AlignRight)
        lay.setSpacing(10)

        self._title = QLineEdit(settings["title"])
        lay.addRow("Title:", self._title)
        self._w = QSpinBox(); self._w.setRange(1, 4096); self._w.setValue(settings["width"])
        lay.addRow("Width:", self._w)
        self._h = QSpinBox(); self._h.setRange(1, 4096); self._h.setValue(settings["height"])
        lay.addRow("Height:", self._h)
        self._fps = QSpinBox(); self._fps.setRange(1, 240); self._fps.setValue(settings["target_fps"])
        lay.addRow("Target FPS:", self._fps)
        self._gx = QDoubleSpinBox(); self._gx.setRange(-9999, 9999); self._gx.setValue(settings["gravity_x"])
        lay.addRow("Gravity X:", self._gx)
        self._gy = QDoubleSpinBox(); self._gy.setRange(-9999, 9999); self._gy.setValue(settings["gravity_y"])
        lay.addRow("Gravity Y:", self._gy)

        self._bg_col = settings["background_color"]
        self._bg_btn = QPushButton(self._bg_col)
        self._bg_btn.setStyleSheet(f"background:{self._bg_col};")
        self._bg_btn.clicked.connect(self._pick_bg)
        lay.addRow("Background:", self._bg_btn)

        self._vsync = QCheckBox("VSync"); self._vsync.setChecked(settings.get("vsync", True))
        lay.addRow("", self._vsync)
        self._fs = QCheckBox("Fullscreen"); self._fs.setChecked(settings.get("fullscreen", False))
        lay.addRow("", self._fs)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addRow(btns)

    def _pick_bg(self):
        c = QColorDialog.getColor(QColor(self._bg_col), self)
        if c.isValid():
            self._bg_col = c.name()
            self._bg_btn.setText(self._bg_col)
            self._bg_btn.setStyleSheet(f"background:{self._bg_col};")

    def result_settings(self):
        return {
            "title": self._title.text(), "width": self._w.value(), "height": self._h.value(),
            "target_fps": self._fps.value(), "gravity_x": self._gx.value(), "gravity_y": self._gy.value(),
            "background_color": self._bg_col,
            "vsync": self._vsync.isChecked(), "fullscreen": self._fs.isChecked(),
        }

# ═══════════════════════════════════════════════════════════════════════════════
# LUA EXPORTER
# Includes: AABB collision system, camera follow, physics, player input
# ═══════════════════════════════════════════════════════════════════════════════
class LuaExporter:
    @staticmethod
    def export(scene: Scene) -> str:
        s = scene.settings
        ents = scene.ordered()
        print(f"[DEBUG] Lua export: {len(ents)} entities")
        L = [f"-- Cupidon Export — '{s['title']}'", ""]

        # love.load
        L += [
            "function love.load()",
            f"  love.window.setTitle(\"{s['title']}\")",
            f"  love.window.setMode({s['width']}, {s['height']}, {{",
            f"    vsync = {str(s.get('vsync',True)).lower()},",
            f"    fullscreen = {str(s.get('fullscreen',False)).lower()}",
            "  })",
            f"  love.graphics.setDefaultFilter('nearest', 'nearest')",
            f"  love.graphics.setBackgroundColor({LuaExporter._hex(s['background_color'])})",
            "",
            "  entities = {}",
            "  -- camera state",
            "  cam = {x=0, y=0, zoom=1, target='', smooth=true, speed=5, ox=0, oy=0}",
            "",
        ]

        for e in ents:
            if not e.active:
                L.append(f"  -- (inactive) {e.name}")
                continue
            safe = e.name.replace(" ","_").replace("-","_")
            t  = e.components.get("Transform", {})
            sp = e.components.get("Sprite", {})
            rb = e.components.get("Rigidbody", {})
            pc = e.components.get("PlayerController", {})
            cf = e.components.get("CameraFollow", {})
            bc = e.components.get("BoxCollider", {})
            cc = e.components.get("CircleCollider", {})
            asc= e.components.get("AudioSource", {})

            L.append(f"  -- {e.name}")
            L.append(f"  entities[\"{safe}\"] = {{")
            L.append(f"    id=\"{e.id}\", name=\"{e.name}\",")
            L.append(f"    x={t.get('x',0)}, y={t.get('y',0)},")
            L.append(f"    rot={t.get('rotation',0)},")
            L.append(f"    sx={t.get('scale_x',1)}, sy={t.get('scale_y',1)},")
            L.append(f"    w={sp.get('width',64)}, h={sp.get('height',64)},")
            L.append(f"    color={{{LuaExporter._hex(sp.get('color','#4488FF'))}}},")
            L.append(f"    opacity={sp.get('opacity',1.0)},")
            tex = sp.get("texture","")
            if tex: L.append(f"    img=love.graphics.newImage(\"assets/{tex}\"),")
            else:   L.append(f"    img=nil,")

            if rb:
                L.append(f"    vx=0, vy=0, mass={rb.get('mass',1)},")
                L.append(f"    gscale={rb.get('gravity_scale',1)},")
                L.append(f"    damp={rb.get('linear_damping',0.1)},")
                L.append(f"    is_static={'true' if rb.get('is_static') else 'false'},")
                L.append(f"    has_rb=true,")

            if bc:
                L.append(f"    col_type='box',")
                L.append(f"    col_w={bc.get('width',64)}, col_h={bc.get('height',64)},")
                L.append(f"    col_ox={bc.get('offset_x',0)}, col_oy={bc.get('offset_y',0)},")
                L.append(f"    is_trigger={'true' if bc.get('is_trigger') else 'false'},")
            elif cc:
                L.append(f"    col_type='circle',")
                L.append(f"    col_r={cc.get('radius',32)},")
                L.append(f"    col_ox={cc.get('offset_x',0)}, col_oy={cc.get('offset_y',0)},")
                L.append(f"    is_trigger={'true' if cc.get('is_trigger') else 'false'},")

            if pc:
                L.append(f"    speed={pc.get('speed',200)}, jump_force={pc.get('jump_force',400)},")
                L.append(f"    key_up='{pc.get('up_key','w')}', key_dn='{pc.get('down_key','s')}',")
                L.append(f"    key_lt='{pc.get('left_key','a')}', key_rt='{pc.get('right_key','d')}',")
                L.append(f"    key_jmp='{pc.get('jump_key','space')}',")
                L.append(f"    has_pc=true,")

            if cf:
                L.append(f"    has_cf=true,")
                tgt = cf.get("target","")
                if tgt:
                    tgt_ent = scene.get(tgt)
                    tgt_name = tgt_ent.name.replace(" ","_").replace("-","_") if tgt_ent else ""
                    L.append(f"    cf_target='{tgt_name}',")
                else:
                    L.append(f"    cf_target='',")
                L.append(f"    cf_zoom={cf.get('zoom',1)},")
                L.append(f"    cf_smooth={'true' if cf.get('smooth',True) else 'false'},")
                L.append(f"    cf_speed={cf.get('smooth_speed',5)},")
                L.append(f"    cf_ox={cf.get('offset_x',0)}, cf_oy={cf.get('offset_y',0)},")
                L.append(f"    is_camera=true,")

            if e.is_camera and not cf:
                L.append(f"    is_camera=true, cf_target='', cf_zoom=1,")

            if asc and asc.get("file"):
                stype = "static" if asc.get("file","").endswith(".wav") else "stream"
                L.append(f"    sfx=love.audio.newSource(\"assets/{asc['file']}\",\"{stype}\"),")
                L.append(f"    sfx_loop={'true' if asc.get('loop') else 'false'},")
                L.append(f"    sfx_auto={'true' if asc.get('play_on_load') else 'false'},")

            L.append(f"  }}")
            L.append("")

        # Auto-play audio
        L.append("  for _, e in pairs(entities) do")
        L.append("    if e.sfx then e.sfx:setLooping(e.sfx_loop or false) end")
        L.append("    if e.sfx and e.sfx_auto then e.sfx:play() end")
        L.append("  end")
        L.append("end\n")

        # ── love.update ──────────────────────────────────────────────────
        L += [
            "-- AABB collision resolution between two box entities",
            "local function resolve_aabb(a, b)",
            "  if not (a.col_type and b.col_type) then return end",
            "  local ax=a.x+(a.col_ox or 0), ay=a.y+(a.col_oy or 0)",
            "  local bx=b.x+(b.col_ox or 0), by=b.y+(b.col_oy or 0)",
            "  local aw=a.col_w or a.w, ah=a.col_h or a.h",
            "  local bw=b.col_w or b.w, bh=b.col_h or b.h",
            "  local dx=ax-bx, dy=ay-by",
            "  local ox=(aw/2+bw/2)-math.abs(dx)",
            "  local oy=(ah/2+bh/2)-math.abs(dy)",
            "  if ox<=0 or oy<=0 then return end",
            "  if a.is_trigger or b.is_trigger then",
            "    if a.on_trigger then a:on_trigger(b) end",
            "    if b.on_trigger then b:on_trigger(a) end",
            "    return",
            "  end",
            "  if ox<oy then",
            "    local s=dx<0 and -1 or 1",
            "    if not a.is_static then a.x=a.x+s*ox/2 end",
            "    if not b.is_static then b.x=b.x-s*ox/2 end",
            "    if a.vx then a.vx=0 end; if b.vx then b.vx=0 end",
            "  else",
            "    local s=dy<0 and -1 or 1",
            "    if not a.is_static then a.y=a.y+s*oy/2 end",
            "    if not b.is_static then b.y=b.y-s*oy/2 end",
            "    if dy>0 and a.vy then a.vy=0 end",
            "    if dy<0 and b.vy then b.vy=0 end",
            "  end",
            "end\n",
            "function love.update(dt)",
            f"  local gx, gy = {s['gravity_x']}, {s['gravity_y']}",
            "  -- build entity list for collision pass",
            "  local elist = {}",
            "  for _, e in pairs(entities) do table.insert(elist, e) end\n",
            "  for _, e in ipairs(elist) do",
            "    -- Physics",
            "    if e.has_rb and not e.is_static then",
            "      e.vx = e.vx + gx * (e.gscale or 1) * dt",
            "      e.vy = e.vy + gy * (e.gscale or 1) * dt",
            "      e.vx = e.vx * (1 - (e.damp or 0))",
            "    end",
            "    -- Player Controller",
            "    if e.has_pc then",
            "      local mvx, mvy = 0, 0",
            "      if love.keyboard.isDown(e.key_rt) then mvx = e.speed end",
            "      if love.keyboard.isDown(e.key_lt) then mvx = -e.speed end",
            "      if love.keyboard.isDown(e.key_up) then mvy = -e.speed end",
            "      if love.keyboard.isDown(e.key_dn) then mvy = e.speed end",
            "      if e.has_rb then e.vx = mvx else e.x = e.x + mvx * dt end",
            "      if e.has_rb and mvy < 0 and math.abs(e.vy) < 1 then e.vy = -e.jump_force end",
            "      if not e.has_rb then e.y = e.y + mvy * dt end",
            "    end",
            "    -- Apply velocity",
            "    if e.has_rb and not e.is_static then",
            "      e.x = e.x + e.vx * dt",
            "      e.y = e.y + e.vy * dt",
            "    end",
            "    -- Camera follow",
            "    if e.is_camera and e.cf_target and e.cf_target ~= '' then",
            "      local t = entities[e.cf_target]",
            "      if t then",
            f"        local tw = {s['width']}; local th = {s['height']}",
            "        local tx = t.x - tw/2/(e.cf_zoom or 1) + (e.cf_ox or 0)",
            "        local ty = t.y - th/2/(e.cf_zoom or 1) + (e.cf_oy or 0)",
            "        if e.cf_smooth then",
            "          e.x = e.x + (tx - e.x) * (e.cf_speed or 5) * dt",
            "          e.y = e.y + (ty - e.y) * (e.cf_speed or 5) * dt",
            "        else e.x = tx; e.y = ty end",
            "        cam.x = e.x; cam.y = e.y; cam.zoom = e.cf_zoom or 1",
            "      end",
            "    end",
            "  end\n",
            "  -- Collision pass (N² — fine for small games)",
            "  for i=1,#elist do",
            "    for j=i+1,#elist do",
            "      resolve_aabb(elist[i], elist[j])",
            "    end",
            "  end",
            "end\n",
        ]

        # ── love.draw ────────────────────────────────────────────────────
        L += [
            "function love.draw()",
            "  love.graphics.push()",
            "  love.graphics.scale(cam.zoom, cam.zoom)",
            "  love.graphics.translate(-cam.x, -cam.y)",
            "  for _, e in pairs(entities) do",
            "    if not e.is_camera then",
            "      love.graphics.push()",
            "      love.graphics.translate(e.x, e.y)",
            "      love.graphics.rotate(e.rot or 0)",
            "      love.graphics.scale(e.sx or 1, e.sy or 1)",
            "      love.graphics.setColor(e.color[1],e.color[2],e.color[3],e.opacity or 1)",
            "      if e.img then",
            "        local iw,ih=e.img:getDimensions()",
            "        love.graphics.draw(e.img,-iw/2,-ih/2)",
            "      else",
            "        love.graphics.rectangle('fill',-e.w/2,-e.h/2,e.w,e.h)",
            "      end",
            "      love.graphics.pop()",
            "    end",
            "  end",
            "  love.graphics.pop()",
            "  love.graphics.setColor(1,1,1,0.5)",
            "  love.graphics.print('ESC: quit', 6, 6)",
            "end\n",
            "function love.keypressed(key)",
            "  if key=='escape' then love.event.quit() end",
            "end",
        ]
        return "\n".join(L)

    @staticmethod
    def _hex(hx):
        c = QColor(hx) if QColor(hx).isValid() else QColor("#000000")
        return f"{c.redF():.3f}, {c.greenF():.3f}, {c.blueF():.3f}"

# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════
class ProjectManagerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cupidon — Project Manager")
        self.setMinimumSize(700, 500)
        self.selected_path = None
        self._db_file = os.path.join(os.path.expanduser("~"), ".cupidon_projects.json")
        self._projects = self._load()
        self._build()
        QTimer.singleShot(100, self._check_deps)
        print("[DEBUG] ProjectManager init")

    def _load(self):
        if os.path.isfile(self._db_file):
            try:
                with open(self._db_file) as f:
                    return json.load(f)
            except: pass
        return []

    def _save(self):
        with open(self._db_file, "w") as f:
            json.dump(self._projects, f, indent=2)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)

        # Banner
        banner = QWidget()
        banner.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                             "stop:0 #0d0d1a, stop:1 #0e3a5c);")
        banner.setFixedHeight(90)
        bl = QHBoxLayout(banner); bl.setContentsMargins(24, 0, 24, 0)
        left = QVBoxLayout()
        t1 = QLabel("Cupidon")
        t1.setStyleSheet("color:white;font-size:26px;font-weight:bold;")
        t2 = QLabel("2D Game Editor for Love2D")
        t2.setStyleSheet("color:#88aacc;font-size:12px;")
        left.addWidget(t1); left.addWidget(t2)
        bl.addLayout(left); bl.addStretch()
        lay.addWidget(banner)

        # Body
        body = QWidget(); body.setStyleSheet("background:#1e1e1e;")
        blay = QHBoxLayout(body); blay.setContentsMargins(16,16,16,16); blay.setSpacing(16)

        # Left: project list
        left_w = QWidget()
        ll = QVBoxLayout(left_w); ll.setContentsMargins(0,0,0,0); ll.setSpacing(6)
        ll.addWidget(QLabel("Recent Projects"))
        self._list = QListWidget()
        self._list.setStyleSheet("background:#252526;border:1px solid #3a3a3a;border-radius:4px;")
        self._list.setIconSize(QSize(32,32))
        self._list.itemDoubleClicked.connect(self._open_selected)
        ll.addWidget(self._list)
        blay.addWidget(left_w, 2)

        # Right: actions + deps
        right_w = QWidget()
        rl = QVBoxLayout(right_w); rl.setContentsMargins(0,0,0,0); rl.setSpacing(8)

        new_btn = QPushButton("＋  New Project")
        new_btn.setStyleSheet("background:#094771;color:white;padding:12px;border-radius:5px;font-size:13px;")
        new_btn.clicked.connect(self._new)
        rl.addWidget(new_btn)

        open_btn = QPushButton("📂  Open Folder")
        open_btn.setStyleSheet("padding:10px;")
        open_btn.clicked.connect(self._open_folder)
        rl.addWidget(open_btn)

        rl.addSpacing(8)

        open_sel = QPushButton("▶  Open Selected")
        open_sel.setStyleSheet("background:#1e4d1e;color:#7cdb7c;padding:10px;border-radius:5px;font-size:13px;")
        open_sel.clicked.connect(self._open_selected)
        rl.addWidget(open_sel)

        rm_btn = QPushButton("✕  Remove from List")
        rm_btn.setStyleSheet("background:#4d1e1e;color:#db7c7c;padding:8px;")
        rm_btn.clicked.connect(self._remove)
        rl.addWidget(rm_btn)

        rl.addStretch()

        self._deps_lbl = QLabel("Checking dependencies…")
        self._deps_lbl.setWordWrap(True)
        self._deps_lbl.setStyleSheet("color:#999;font-size:11px;background:#252526;"
                                     "border:1px solid #3a3a3a;border-radius:4px;padding:10px;")
        rl.addWidget(self._deps_lbl)

        blay.addWidget(right_w, 1)
        lay.addWidget(body)
        self._refresh_list()

    def _check_deps(self):
        lines = []
        try:
            r = subprocess.run(["love","--version"], capture_output=True, text=True, timeout=3)
            v = (r.stdout or r.stderr).strip()[:50]
            lines.append(f"✅  love2d: {v}")
        except FileNotFoundError:
            lines.append("❌  love2d: NOT FOUND\n   sudo apt install love")
        except:
            lines.append("⚠️  love2d: check failed")
        try:
            from PyQt5.QtCore import PYQT_VERSION_STR
            lines.append(f"✅  PyQt5: {PYQT_VERSION_STR}")
        except:
            lines.append("❌  PyQt5: NOT FOUND")
        self._deps_lbl.setText("\n".join(lines))

    def _refresh_list(self):
        self._list.clear()
        for p in reversed(self._projects):
            ok = os.path.isdir(p)
            item = QListWidgetItem(f"  {'📁' if ok else '⚠️'}  {os.path.basename(p)}\n        {p}")
            item.setData(Qt.UserRole, p)
            if not ok:
                item.setForeground(QColor("#555"))
            self._list.addItem(item)

    def _new(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if not ok or not name.strip(): return
        parent = QFileDialog.getExistingDirectory(self, "Choose location",
                 os.path.join(os.path.expanduser("~"), "cupidon_projects"))
        if not parent: return
        path = os.path.join(parent, name.strip())
        os.makedirs(os.path.join(path, "assets"), exist_ok=True)
        with open(os.path.join(path, "scene.json"), "w") as f:
            json.dump(Scene().to_dict(), f, indent=2)
        self._add(path)
        self.selected_path = path
        self.accept()

    def _open_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Open Project",
               os.path.expanduser("~"))
        if path:
            self._add(path)
            self.selected_path = path
            self.accept()

    def _open_selected(self):
        item = self._list.currentItem()
        if not item: return
        path = item.data(Qt.UserRole)
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Not Found", f"Folder not found:\n{path}")
            return
        self.selected_path = path
        self.accept()

    def _remove(self):
        item = self._list.currentItem()
        if item:
            self._projects = [p for p in self._projects if p != item.data(Qt.UserRole)]
            self._save(); self._refresh_list()

    def _add(self, path):
        self._projects = [p for p in self._projects if p != path]
        self._projects.append(path)
        self._save(); self._refresh_list()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EDITOR WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class EditorWindow(QMainWindow):
    def __init__(self, project_dir=""):
        super().__init__()
        self.scene        = Scene()
        self.undo_stack   = UndoStack()
        self.love_process = None
        self.current_file = None
        self._sel_id      = None
        self._project_dir = project_dir or os.path.join(os.path.expanduser("~"), "cupidon_projects", "default")

        os.makedirs(self._project_dir, exist_ok=True)
        os.makedirs(os.path.join(self._project_dir, "assets"), exist_ok=True)

        self.setWindowTitle(f"Cupidon — {os.path.basename(self._project_dir)}")
        self.setMinimumSize(1400, 800)

        # Order: panels first (creates canvas), then toolbar + menu
        self._build_panels()
        self.canvas._assets_dir = os.path.join(self._project_dir, "assets")
        self._build_toolbar()
        self._build_menu()
        self._build_statusbar()
        self._connect_all()

        sj = os.path.join(self._project_dir, "scene.json")
        if os.path.isfile(sj):
            self._do_load(sj)
        else:
            self._refresh_all()

        self.undo_stack.push(self.scene.to_dict(), "Initial")
        print("[DEBUG] EditorWindow ready")

    # ─── MENU ───────────────────────────────────────────────────────────────
    def _build_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("File")
        fm.addAction("New Scene\tCtrl+N",      self.new_scene)
        fm.addAction("Open Scene\tCtrl+O",     self.load_scene)
        fm.addAction("Save Scene\tCtrl+S",     self.save_scene)
        fm.addAction("Save As…",               self.save_scene_as)
        fm.addSeparator()
        fm.addAction("Set Project Folder…",    self._set_project)
        fm.addSeparator()
        fm.addAction("Export Lua…",            self.export_lua)
        fm.addSeparator()
        fm.addAction("Exit",                   self.close)

        em = mb.addMenu("Edit")
        em.addAction("Undo\tCtrl+Z",           self.undo)
        em.addAction("Redo\tCtrl+Y",           self.redo)
        em.addSeparator()
        em.addAction("Duplicate\tCtrl+D",      self._dup_selected)
        em.addAction("Delete\tDel",            self._del_selected)
        em.addSeparator()
        em.addAction("Scene Settings…",        self.open_scene_settings)

        vm = mb.addMenu("View")
        vm.addAction("Reset Camera\tCtrl+0",   self._reset_camera)
        vm.addAction("Add Camera Entity",      self._add_camera)
        self._snap_action = vm.addAction("Snap to Grid\tCtrl+G")
        self._snap_action.setCheckable(True)
        self._snap_action.triggered.connect(self._toggle_snap)
        self._debug_action = vm.addAction("Debug Mode\tCtrl+`")
        self._debug_action.setCheckable(True)
        self._debug_action.triggered.connect(self._toggle_debug)

        rm = mb.addMenu("Run")
        rm.addAction("▶  Run Game\tF5",        self.run_game)
        rm.addAction("■  Stop",                self.stop_game)

    # ─── TOOLBAR ────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)

        def btn(text, tip="", checkable=False, obj_name=""):
            b = QToolButton()
            b.setText(text); b.setToolTip(tip); b.setCheckable(checkable)
            if obj_name: b.setObjectName(obj_name)
            return b

        # File
        from PyQt5.QtWidgets import QAction

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("New Scene")
        new_action.triggered.connect(self.new_scene)
        tb.addAction(new_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save")
        save_action.triggered.connect(self.save_scene)
        tb.addAction(save_action)
        # Tool group
        self._tool_btns = {}
        tool_defs = [
            ("⬜", "Select  Q",  "select"),
            ("✥",  "Move  W",   "move"),
            ("↺",  "Rotate  E", "rotate"),
            ("⤢",  "Scale  R",  "scale"),
            ("✋", "Pan  H",    "hand"),
            ("＋", "Add Entity  A", "add"),
        ]
        ag = QActionGroup(self); ag.setExclusive(True)
        for icon, tip, tool in tool_defs:
            b = QToolButton()
            b.setText(icon); b.setToolTip(tip); b.setCheckable(True)
            b.setFixedSize(36, 36)
            b.clicked.connect(lambda chk, t=tool: self._set_tool(t))
            tb.addWidget(b)
            self._tool_btns[tool] = b
        self._tool_btns["select"].setChecked(True)
        self.canvas._add_btn = self._tool_btns["add"]
        tb.addSeparator()

        # Snap
        self._snap_btn = QToolButton(); self._snap_btn.setText("⊞ Snap")
        self._snap_btn.setCheckable(True); self._snap_btn.setToolTip("Snap to Grid (Ctrl+G)")
        self._snap_btn.toggled.connect(lambda on: (
            self.canvas.set_snap(on, self._snap_spin.value()),
            self._snap_action.setChecked(on),
            self._snap_lbl.setText("  SNAP  " if on else "")
        ))
        tb.addWidget(self._snap_btn)
        self._snap_spin = QSpinBox()
        self._snap_spin.setRange(1, 256); self._snap_spin.setValue(16)
        self._snap_spin.setFixedWidth(54); self._snap_spin.setToolTip("Grid size")
        self._snap_spin.valueChanged.connect(lambda v: self.canvas.set_snap(self._snap_btn.isChecked(), v))
        tb.addWidget(self._snap_spin)
        tb.addSeparator()

        # Debug
        self._debug_btn = QToolButton(); self._debug_btn.setText("🐛 Debug")
        self._debug_btn.setCheckable(True); self._debug_btn.setToolTip("Debug Mode (Ctrl+`)")
        self._debug_btn.toggled.connect(self._toggle_debug)
        tb.addWidget(self._debug_btn)
        tb.addSeparator()

        # Camera
        cam_b = QToolButton(); cam_b.setText("📷 Camera"); cam_b.setToolTip("Add Camera Entity")
        cam_b.clicked.connect(self._add_camera); tb.addWidget(cam_b)
        tb.addSeparator()

        # Run / Stop
        run_b = QPushButton("▶  RUN"); run_b.setObjectName("run_btn")
        run_b.setFixedHeight(32); run_b.clicked.connect(self.run_game)
        tb.addWidget(run_b)
        stp_b = QPushButton("■ Stop"); stp_b.setObjectName("stop_btn")
        stp_b.setFixedHeight(32); stp_b.clicked.connect(self.stop_game)
        tb.addWidget(stp_b)
        tb.addSeparator()

        # Undo
        undo_btn = btn("↩", "Undo Ctrl+Z")
        undo_btn.clicked.connect(self.undo)
        tb.addWidget(undo_btn)

        # Redo
        redo_btn = btn("↪", "Redo Ctrl+Y")
        redo_btn.clicked.connect(self.redo)
        tb.addWidget(redo_btn)

        print("[DEBUG] Toolbar built")

    # ─── PANELS ─────────────────────────────────────────────────────────────
    def _build_panels(self):
        self.canvas = Canvas(self.scene)
        self.setCentralWidget(self.canvas)

        # FIX: use setFeatures to enable close button properly
        def make_dock(title, widget, area, min_w=0):
            d = QDockWidget(title, self)
            d.setWidget(widget)
            d.setAllowedAreas(Qt.AllDockWidgetAreas)
            # Enable floatable, closable, movable
            d.setFeatures(QDockWidget.DockWidgetClosable |
                          QDockWidget.DockWidgetMovable  |
                          QDockWidget.DockWidgetFloatable)
            if min_w:
                widget.setMinimumWidth(min_w)
            self.addDockWidget(area, d)
            return d

        self.hierarchy  = HierarchyPanel()
        self.inspector  = InspectorPanel(self.scene)
        self.assets     = AssetManagerPanel(getattr(self, "_project_dir", ""))

        self._d_hier  = make_dock("Hierarchy",     self.hierarchy, Qt.LeftDockWidgetArea,  200)
        self._d_insp  = make_dock("Inspector",     self.inspector, Qt.RightDockWidgetArea, 280)
        self._d_asset = make_dock("Asset Manager", self.assets,    Qt.BottomDockWidgetArea)

        # Console
        self._console = QTextEdit()
        self._console.setReadOnly(True)
        self._console.setMaximumHeight(130)
        self._console.setStyleSheet("background:#0d1117;color:#4ec9b0;"
                                    "font-family:monospace;font-size:11px;border:none;")
        self._d_log = make_dock("Console", self._console, Qt.BottomDockWidgetArea)
        self.tabifyDockWidget(self._d_asset, self._d_log)
        print("[DEBUG] Panels built")

    def _build_statusbar(self):
        self.status = QStatusBar(); self.setStatusBar(self.status)
        self._mode_lbl = QLabel("  SELECT  ")
        self._mode_lbl.setStyleSheet("background:#16825d;color:white;padding:0 10px;")
        self.status.addPermanentWidget(self._mode_lbl)
        self._snap_lbl = QLabel("")
        self._snap_lbl.setStyleSheet("background:#5c4d00;color:#e5c07b;padding:0 8px;")
        self.status.addPermanentWidget(self._snap_lbl)
        self.status.showMessage("Ready — pick a tool, click canvas to interact.")

    # ─── SIGNALS ────────────────────────────────────────────────────────────
    def _connect_all(self):
        self.canvas.select_entity_signal.connect(self._on_select)
        self.canvas.entity_moved.connect(self._on_moved)
        self.canvas.gizmo_drop.connect(self._on_gizmo_drop)
        self.hierarchy.entity_selected.connect(self._on_hier_select)
        self.hierarchy.entity_deleted.connect(self._del_entity)
        self.hierarchy.entity_duplicated.connect(self._dup_entity)
        self.inspector.entity_changed.connect(self._on_insp_change)
        print("[DEBUG] Signals connected")

    # ─── TOOL ───────────────────────────────────────────────────────────────
    def _set_tool(self, tool):
        for t, b in self._tool_btns.items():
            b.setChecked(t == tool)
        self.canvas.set_tool(tool)
        names = {"select":"SELECT","move":"MOVE","rotate":"ROTATE",
                 "scale":"SCALE","hand":"PAN","add":"ADD"}
        self._mode_lbl.setText(f"  {names.get(tool, tool.upper())}  ")
        self.status.showMessage(f"Tool: {names.get(tool,'?')}")

    def _toggle_snap(self, on):
        self._snap_btn.setChecked(on)
        self._snap_action.setChecked(on)
        self.canvas.set_snap(on, self._snap_spin.value())
        self._snap_lbl.setText("  SNAP  " if on else "")

    def _toggle_debug(self, on):
        self._debug_btn.setChecked(on)
        self._debug_action.setChecked(on)
        self.canvas.set_debug(on)
        self.status.showMessage("Debug: collider outlines enhanced." if on else "Debug OFF.")
        self._log(f"Debug mode: {on}")

    # ─── SELECTION ──────────────────────────────────────────────────────────
    def _on_select(self, eid):
        self._sel_id = eid
        e = self.scene.get(eid)
        if e:
            self.inspector.load_entity(e)
            self.hierarchy.select(eid)
            self.status.showMessage(f"Selected: {e.name}  |  {', '.join(e.components)}")

    def _on_hier_select(self, eid):
        self._sel_id = eid
        e = self.scene.get(eid)
        if e:
            self.inspector.load_entity(e)
            self.canvas.select_entity(eid)
            self.status.showMessage(f"Selected: {e.name}")

    def _on_moved(self, eid):
        e = self.scene.get(eid)
        if e:
            self.inspector.refresh_transform(e)

    def _on_gizmo_drop(self):
        self.undo_stack.push(self.scene.to_dict(), "Transform")

    def _on_insp_change(self, eid):
        self.canvas.refresh_visual(eid)
        self._refresh_hierarchy()
        self.undo_stack.push(self.scene.to_dict(), "Inspector")

    # ─── ENTITY OPS ─────────────────────────────────────────────────────────
    def _add_camera(self):
        e = self.scene.add_entity("Camera",
            x=self.scene.settings["width"] / 2,
            y=self.scene.settings["height"] / 2)
        e.is_camera = True
        e.components.pop("Sprite", None)  # cameras have no sprite
        e.add_component("CameraFollow")
        self.canvas.add_visual(e)
        self._refresh_hierarchy()
        self._on_select(e.id)
        self.undo_stack.push(self.scene.to_dict(), "Add Camera")
        self._log("Camera entity added. Set CameraFollow.target in inspector.")
        print("[DEBUG] Camera entity added")

    def _del_entity(self, eid):
        e = self.scene.get(eid)
        name = e.name if e else eid
        self.scene.remove_entity(eid)
        self.canvas.remove_visual(eid)
        self.canvas.gizmo.detach()
        if self._sel_id == eid:
            self.inspector.clear()
            self._sel_id = None
        self._refresh_hierarchy()
        self.undo_stack.push(self.scene.to_dict(), f"Delete {name}")
        self.status.showMessage(f"Deleted '{name}'")

    def _del_selected(self):
        if self._sel_id:
            self._del_entity(self._sel_id)

    def _dup_entity(self, eid):
        e = self.scene.get(eid)
        if not e: return
        d = self.scene.add_entity(e.name + "_copy")
        d.components = copy.deepcopy(e.components)
        d.is_camera  = e.is_camera
        d.set("Transform", "x", e.get("Transform", "x", 0) + 32)
        d.set("Transform", "y", e.get("Transform", "y", 0) + 32)
        self.canvas.add_visual(d)
        self._refresh_hierarchy()
        self._on_select(d.id)
        self.undo_stack.push(self.scene.to_dict(), f"Duplicate {e.name}")

    def _dup_selected(self):
        if self._sel_id:
            self._dup_entity(self._sel_id)

    def _refresh_hierarchy(self):
        self.hierarchy.refresh(self.scene)

    def _refresh_all(self):
        self.canvas.refresh_all()
        self._refresh_hierarchy()

    # ─── UNDO / REDO ────────────────────────────────────────────────────────
    def undo(self):
        snap = self.undo_stack.undo(self.scene.to_dict())
        if snap:
            self.scene.from_dict(snap)
            self.canvas.scene = self.scene
            self._refresh_all()
            self.inspector.clear(); self._sel_id = None
            self.canvas.gizmo.detach()
            self.status.showMessage("Undo"); self._log("Undo")

    def redo(self):
        snap = self.undo_stack.redo(self.scene.to_dict())
        if snap:
            self.scene.from_dict(snap)
            self.canvas.scene = self.scene
            self._refresh_all()
            self.inspector.clear(); self._sel_id = None
            self.canvas.gizmo.detach()
            self.status.showMessage("Redo"); self._log("Redo")

    # ─── SCENE I/O ──────────────────────────────────────────────────────────
    def new_scene(self):
        if QMessageBox.question(self, "New Scene", "Clear current scene?",
           QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.scene = Scene()
            self.canvas.scene = self.scene
            self.canvas.gizmo.detach()
            self.inspector.clear(); self._sel_id = None
            self._refresh_all(); self.current_file = None
            self.undo_stack = UndoStack()
            self.undo_stack.push(self.scene.to_dict(), "Initial")
            self.setWindowTitle(f"Cupidon — {os.path.basename(self._project_dir)}")
            self._log("New scene")

    def save_scene(self):
        if not self.current_file:
            self.save_scene_as(); return
        self._do_save(self.current_file)

    def save_scene_as(self):
        p, _ = QFileDialog.getSaveFileName(self, "Save Scene",
               os.path.join(self._project_dir, "scene.json"), "JSON (*.json)")
        if p: self._do_save(p)

    def _do_save(self, path):
        with open(path, "w") as f:
            json.dump(self.scene.to_dict(), f, indent=2)
        self.current_file = path
        self.status.showMessage(f"Saved: {path}")
        self._log(f"Saved: {path}")
        print(f"[DEBUG] Saved {path}")

    def load_scene(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open Scene",
               self._project_dir, "JSON (*.json)")
        if p: self._do_load(p)

    def _do_load(self, path):
        try:
            with open(path) as f:
                data = json.load(f)
            self.scene.from_dict(data)
            self.canvas.scene = self.scene
            self.canvas.gizmo.detach()
            self.inspector.clear(); self._sel_id = None
            self._refresh_all()
            self.current_file = path
            self.undo_stack = UndoStack()
            self.undo_stack.push(self.scene.to_dict(), "Load")
            self.status.showMessage(f"Loaded: {path}")
            self._log(f"Loaded: {path}")
        except Exception as ex:
            QMessageBox.critical(self, "Load Error", str(ex))
            print(f"[DEBUG] Load error: {ex}")

    def _set_project(self):
        p = QFileDialog.getExistingDirectory(self, "Project Folder", self._project_dir)
        if p:
            self._project_dir = p
            self.canvas._assets_dir = os.path.join(p, "assets")
            self.assets.set_project_dir(p)
            os.makedirs(os.path.join(p, "assets"), exist_ok=True)
            self._log(f"Project: {p}")

    # ─── SCENE SETTINGS ─────────────────────────────────────────────────────
    def open_scene_settings(self):
        dlg = SceneSettingsDialog(self.scene.settings, self)
        if dlg.exec_() == QDialog.Accepted:
            new_s = dlg.result_settings()
            # FIX: apply background via set_background (no crash)
            self.scene.settings.update(new_s)
            self.canvas.set_background(new_s["background_color"])
            self.canvas._draw_border()
            self._log("Scene settings updated")
            self.undo_stack.push(self.scene.to_dict(), "Scene Settings")

    # ─── RUN ────────────────────────────────────────────────────────────────
    def run_game(self):
        print("[DEBUG] Run →")
        lua  = LuaExporter.export(self.scene)
        temp = os.path.join(self._project_dir, "_run")
        os.makedirs(temp, exist_ok=True)
        src  = os.path.join(self._project_dir, "assets")
        dst  = os.path.join(temp, "assets")
        if os.path.isdir(src):
            if os.path.exists(dst): shutil.rmtree(dst)
            shutil.copytree(src, dst)
        with open(os.path.join(temp, "main.lua"), "w") as f:
            f.write(lua)
        if self.love_process and self.love_process.poll() is None:
            self.love_process.terminate()
        try:
            self.love_process = subprocess.Popen(["love", temp])
            self.status.showMessage(f"Love2D running — PID {self.love_process.pid}")
            self._log(f"Launched Love2D PID {self.love_process.pid}")
        except FileNotFoundError:
            QMessageBox.critical(self, "love not found",
                "Install Love2D:\n  sudo apt install love")

    def stop_game(self):
        if self.love_process and self.love_process.poll() is None:
            self.love_process.terminate()
            self.status.showMessage("Stopped.")
            self._log("Love2D stopped")

    def export_lua(self):
        p, _ = QFileDialog.getSaveFileName(self, "Export Lua",
               os.path.join(self._project_dir, "main.lua"), "Lua (*.lua)")
        if p:
            with open(p, "w") as f:
                f.write(LuaExporter.export(self.scene))
            self._log(f"Exported: {p}")
            self.status.showMessage(f"Exported: {p}")

    def _reset_camera(self):
        self.canvas.resetTransform()
        self.canvas.centerOn(self.scene.settings["width"] / 2,
                             self.scene.settings["height"] / 2)

    # ─── LOG ────────────────────────────────────────────────────────────────
    def _log(self, msg):
        self._console.append(f"▸ {msg}")

    # ─── KEYBOARD ───────────────────────────────────────────────────────────
    def keyPressEvent(self, e):
        mod = e.modifiers()
        key = e.key()
        if mod & Qt.ControlModifier:
            if key == Qt.Key_Z:    self.undo(); return
            if key == Qt.Key_Y:    self.redo(); return
            if key == Qt.Key_S:    self.save_scene(); return
            if key == Qt.Key_D:    self._dup_selected(); return
            if key == Qt.Key_N:    self.new_scene(); return
            if key == Qt.Key_O:    self.load_scene(); return
            if key == Qt.Key_G:    self._snap_btn.toggle(); return
            if key == Qt.Key_0:    self._reset_camera(); return
        if key == Qt.Key_F5:       self.run_game(); return
        if key == Qt.Key_Delete:   self._del_selected(); return
        tool_keys = {
            Qt.Key_Q: "select", Qt.Key_W: "move",
            Qt.Key_E: "rotate", Qt.Key_R: "scale",
            Qt.Key_H: "hand",   Qt.Key_A: "add",
        }
        if key in tool_keys:
            self._set_tool(tool_keys[key])
        super().keyPressEvent(e)

    def closeEvent(self, e):
        self.stop_game(); e.accept()

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("[DEBUG] QApplication start")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_QSS)
    app.setFont(QFont("Segoe UI", 10))

    pm = ProjectManagerDialog()
    if pm.exec_() != QDialog.Accepted or not pm.selected_path:
        print("[DEBUG] Cancelled — exit")
        sys.exit(0)

    print(f"[DEBUG] Opening project: {pm.selected_path}")
    win = EditorWindow(pm.selected_path)
    win.show()
    sys.exit(app.exec_())


