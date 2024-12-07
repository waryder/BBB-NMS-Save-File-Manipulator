from setuptools import setup, find_packages

setup(
    name='BBB-NMS-SAVE-FILE-MANIPULATOR',
    version='0.3.0-alpha',
    description='Save file manipulator for No Man\'s Sky',
    author='Bill Ryder (BigBuffaloBill)',
    url='https://github.com/waryder/BBB-NMS-Save-File-Manipulator',
    include_package_data=True,
    packages=find_packages(),  # This will automatically find 'BBB_NMS_Save_File_Manipulator' as a package
    install_requires=[
        'altgraph==0.17.4',
        'MouseInfo==0.1.3',
        'packaging==24.2',
        'pefile==2023.2.7',
        'psutil==6.0.0',
        'PyAutoGUI==0.9.54',
        'PyGetWindow==0.0.9',
        'pyinstaller==6.11.0',
        'pyinstaller-hooks-contrib==2024.9',
        'Pympler==1.1',
        'PyMsgBox==1.0.9',
        'pyperclip==1.9.0',
        'PyQt5==5.15.11',
        'PyQt5-Qt5==5.15.2',
        'PyQt5_sip==12.15.0',
        'PyRect==0.2.0',
        'PyScreeze==1.0.1',
        'pytweening==1.2.0',
        'pywin32==308',
        'pywin32-ctypes==0.2.3',
        'setuptools==75.3.0',
        'yappi==1.6.0'
    ],
    python_requires='>=3.8',
    package_data={
        'BBB_NMS_Save_File_Manipulator': ['help/*'],  # Include all files in the help directory
        'BBB_NMS_Save_File_Manipulator': ['images/*'],
    },
    entry_points={
        'console_scripts': [
            'bbb_nms_sfm=BBB_NMS_Save_File_Manipulator.BBB_NMS_Save_File_Manipulator:main',
        ],
    },
)


"""
from setuptools import setup, find_packages

setup(
    name='BBB-NMS-SAVE-FILE-MANIPULATOR',
    version='0.1.2-alpha',
    include_package_data=True,
    package_dir={"": "BBB_NMS_Save_File_Manipulator"},
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
    package_data={
        'BBB_NMS_Save_File_Manipulator': ['help/*'],  # Include all files in the help directory
    },
    entry_points={
        'console_scripts': [
            'bbb_nms_sfm = BBB_NMS_Save_File_Manipulator.BBB_NMS_Save_File_Manipulator:main',
        ],
    },
)
"""
