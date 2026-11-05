# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for TestLinkCRXMLGen
#
# Key choices that reduce VirusTotal flags:
#   upx=False      — UPX packing is a known AV trigger
#   console=False  — GUI-only, no console window
#   excludes       — strips unused large packages (numpy, PIL, …)

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'docx',
        'docx.oxml',
        'docx.oxml.ns',
        'docx.oxml.parser',
        'docx.oxml.table',
        'docx.oxml.text.paragraph',
        'docx.oxml.text.run',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'lxml.builder',
        'extract_isd',
        'build_xml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'PIL', 'Pillow',
        'cv2', 'pandas', 'sqlalchemy', 'django', 'flask',
        'IPython', 'jupyter', 'notebook', 'pytest',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TestLinkCRXMLGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # <-- keeps AV flags low
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # <-- no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
