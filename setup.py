from setuptools import setup, find_packages

setup(
    name='BBB-NMS-SAVE-FILE-MANIPULATOR',
    version='0.1.0-alpha',
    packages=find_packages(),
    install_requires=[
        'MouseInfo==0.1.3',
        'psutil==6.0.0',
        'PyAutoGUI==0.9.54',
        'PyGetWindow==0.0.9',
        'PyMsgBox==1.0.9',
        'pyperclip==1.9.0',
        'PyQt5==5.15.11',
        'PyQt5-Qt5==5.15.2',
        'PyQt5_sip==12.15.0',
        'PyRect==0.2.0',
        'PyScreeze==1.0.1',
        'pytweening==1.2.0',
        'yappi==1.6.0',
    ],
    entry_points={
        'console_scripts': [
            'bbb_nms_sfm = BBB_NMS_Save_File_Manipulator.BBB-NMS-Save-File-Manipulator:main',
        ],
    },
)
