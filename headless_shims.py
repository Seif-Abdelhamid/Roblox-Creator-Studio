import os
import sys
import types


def _make_noop_module(name: str, attrs: dict | None = None):
    mod = types.ModuleType(name)
    if attrs:
        for k, v in attrs.items():
            setattr(mod, k, v)
    return mod


def activate_headless_shims():
    if str(os.environ.get("HEADLESS", "")).lower() not in {"1", "true", "yes"}:
        return

    # pygame shims
    if "pygame" not in sys.modules:
        class _Clock:
            def tick(self, _fps: int):
                return 0
        display = _make_noop_module("display", {
            "set_mode": lambda *a, **k: None,
            "set_caption": lambda *a, **k: None,
            "flip": lambda: None,
        })
        event = _make_noop_module("event", {
            "get": lambda: [],
        })
        time_mod = _make_noop_module("time", {
            "Clock": _Clock,
        })
        font_mod = _make_noop_module("font", {
            "Font": lambda *a, **k: None,
            "SysFont": lambda *a, **k: None,
        })
        constants = {
            "DOUBLEBUF": 0,
            "OPENGL": 0,
            "QUIT": 0,
            "KEYDOWN": 0,
            "K_ESCAPE": 27,
        }
        pygame_mod = _make_noop_module("pygame", {
            "init": lambda: None,
            "quit": lambda: None,
            "display": display,
            "event": event,
            "time": time_mod,
            "font": font_mod,
        } | constants)
        sys.modules["pygame"] = pygame_mod
        # locals
        sys.modules["pygame.locals"] = pygame_mod

    # OpenGL shims
    for name in ("OpenGL", "OpenGL.GL", "OpenGL.GLU"):
        if name not in sys.modules:
            sys.modules[name] = _make_noop_module(name)
    gl = sys.modules["OpenGL.GL"]
    glu = sys.modules["OpenGL.GLU"]
    noop = lambda *a, **k: None
    for fname in [
        "glEnable","glDisable","glClearColor","glMatrixMode","glLoadIdentity","glClear",
        "glBegin","glEnd","glColor3f","glVertex3f","glPushMatrix","glPopMatrix","glBlendFunc",
        "glViewport","glBindTexture","glTexParameteri","glTexImage2D","glGenTextures","glColor4f",
        "glGetDoublev","glGetIntegerv","glVertex2f","glTranslatef","glRotatef","glScalef",
        "glMaterialfv","glMaterialf","glLightfv","glLightModelfv","glFogi","glFogf","glFogfv","glColorMaterial"
    ]:
        setattr(gl, fname, noop)
    for cname in [
        "GL_DEPTH_TEST","GL_LIGHTING","GL_LIGHT0","GL_COLOR_MATERIAL","GL_COLOR_BUFFER_BIT","GL_DEPTH_BUFFER_BIT",
        "GL_QUADS","GL_BLEND","GL_CULL_FACE","GL_SRC_ALPHA","GL_ONE_MINUS_SRC_ALPHA","GL_TEXTURE_2D",
        "GL_TEXTURE_MIN_FILTER","GL_TEXTURE_MAG_FILTER","GL_LINEAR","GL_TEXTURE_WRAP_S","GL_TEXTURE_WRAP_T","GL_CLAMP_TO_EDGE",
        "GL_MODELVIEW_MATRIX","GL_PROJECTION_MATRIX","GL_VIEWPORT",
        "GL_LINES","GL_FRONT","GL_FRONT_AND_BACK","GL_AMBIENT_AND_DIFFUSE","GL_FOG","GL_FOG_MODE","GL_LINEAR",
        "GL_FOG_START","GL_FOG_END","GL_FOG_COLOR","GL_LIGHT_MODEL_AMBIENT","GL_DIFFUSE","GL_SPECULAR","GL_POSITION","GL_SHININESS"
    ]:
        setattr(gl, cname, 0)
    setattr(glu, "gluPerspective", noop)
    setattr(glu, "gluOrtho2D", noop)
    setattr(glu, "gluProject", lambda *a, **k: (0.0, 0.0, 0.0))

    # numpy shim
    if "numpy" not in sys.modules:
        np = _make_noop_module("numpy", {
            "array": lambda x, dtype=None: x,
            "float32": float,
            "zeros": lambda shape, dtype=None: [[0 for _ in range(shape[1])] for _ in range(shape[0])] if isinstance(shape, tuple) else [0]*shape,
            "dot": lambda a, b: a,
            "cross": lambda a, b: a,
            "linalg": _make_noop_module("linalg", {"norm": lambda v: 0.0}),
        })
        sys.modules["numpy"] = np

    # websocket shim
    if "websocket" not in sys.modules:
        class _WSApp:
            def __init__(self, *a, **k): pass
            def run_forever(self): pass
            def close(self): pass
        ws = _make_noop_module("websocket", {"WebSocketApp": _WSApp})
        sys.modules["websocket"] = ws

    # PIL shim
    if "PIL" not in sys.modules:
        class _Image:
            def open(self, *a, **k): return self
            def convert(self, *a, **k): return self
            @property
            def size(self): return (1,1)
            def tobytes(self): return b"\x00\x00\x00\x00"
        pil = _make_noop_module("PIL")
        image = _make_noop_module("PIL.Image", {"open": lambda *a, **k: _Image()})
        sys.modules["PIL"] = pil
        sys.modules["PIL.Image"] = image