# Nov 8 2026 (Dom: the 4 PM Dispatch build failed): a dial at exactly 0% or 100%, or a range with no spread, asked reportlab
# for a zero-length arc, which divides by zero and kills the whole build. A zero-length arc draws nothing, so every Python
# step of the build skips it. Loaded automatically through PYTHONPATH (set in dispatch_run.sh).
try:
    from reportlab.pdfgen import canvas as _cv
    from reportlab.pdfgen import pathobject as _po
    if not getattr(_cv.Canvas.arc, "_dk_safe", False):
        _a0 = _cv.Canvas.arc
        def _arc(self, x1, y1, x2, y2, startAng=0, extent=90):
            if abs(extent) < 1e-6: return
            return _a0(self, x1, y1, x2, y2, startAng, extent)
        _arc._dk_safe = True; _cv.Canvas.arc = _arc
    if not getattr(_po.PDFPathObject.arc, "_dk_safe", False):
        _p0 = _po.PDFPathObject.arc
        def _parc(self, x1, y1, x2, y2, startAng=0, extent=90):
            if abs(extent) < 1e-6: return
            return _p0(self, x1, y1, x2, y2, startAng, extent)
        _parc._dk_safe = True; _po.PDFPathObject.arc = _parc
except Exception:
    pass
