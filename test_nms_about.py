# File: test_nms_about.py
# Path: C:\MBIN_PROJECTS\Working_Projects\BBB-NMS-Save-File-Manipulator\test_nms_about.py
# Purpose: Exercise Help/About wiring with synthetic widgets, without launching the app or accessing saves.
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

# load_methods: Extract only Help-menu methods and version, avoiding all Qt imports and app side effects.
def load_methods():
    tree = ast.parse(Path(__file__).with_name('NMSHelpMenu.py').read_text(encoding='utf-8'))
    version = next(node for node in tree.body if isinstance(node, ast.Assign)
                   and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'APP_VERSION')
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)
               and node.name in ('create_help_menu', 'show_about')]
    namespace = {'QAction': lambda name, parent: SimpleNamespace(name=name, triggered=Mock()),
                 'QMessageBox': SimpleNamespace(about=Mock())}
    nodes: list[ast.stmt] = [version]  # Keep the extracted statements explicitly typed.
    nodes.extend(methods)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<help methods>', 'exec'), namespace)
    return namespace

class AboutTests(unittest.TestCase):
    # test_exact_version_and_popup: Exercise the actual popup callback with its exact title and text.
    def test_exact_version_and_popup(self):
        env = load_methods()
        parent = object()
        env['show_about'](parent)
        self.assertEqual(env['APP_VERSION'], 'v0.5 alpha')
        env['QMessageBox'].about.assert_called_once_with(
            parent, 'About BBB NMS Save File Manipulator', 'BBB NMS Save File Manipulator\nv0.5 alpha')

    # test_help_menu_wiring: Keep Open Help, add About after a separator, and invoke the connected callback.
    def test_help_menu_wiring(self):
        env = load_methods()
        parent = SimpleNamespace(open_help=Mock(), show_about=Mock())
        menu, bar = Mock(), Mock()
        bar.addMenu.return_value = menu
        env['create_help_menu'](parent, bar)
        bar.addMenu.assert_called_once_with('Help')
        actions = [call.args[0] for call in menu.addAction.call_args_list]
        self.assertEqual([action.name for action in actions], ['Open Help', 'About'])
        menu.addSeparator.assert_called_once_with()
        actions[0].triggered.connect.assert_called_once_with(parent.open_help)
        actions[1].triggered.connect.assert_called_once_with(parent.show_about)
        actions[1].triggered.connect.call_args.args[0]()
        parent.show_about.assert_called_once_with()

if __name__ == '__main__':
    unittest.main(verbosity=2)
