import sys
from pathlib import Path

import pytest

from pyreact.cli import main as cli


def test_create_generate_and_build_project(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    cli.create_project('sample')
    project = tmp_path / 'sample'
    assert (project / 'src/index.py').is_file()
    assert not (project / 'public/index.html').exists()
    assert '[OK] Created project' in capsys.readouterr().out

    with pytest.raises(SystemExit):
        cli.create_project('sample')

    monkeypatch.chdir(project)
    cli.generate_component('Button')
    cli.generate_component('Panel', 'class')
    cli.generate_hook('useCounter')
    assert (project / 'src/components/Button.py').is_file()
    assert 'class Panel' in (project / 'src/components/Panel.py').read_text()
    assert (project / 'src/hooks/use_counter.py').is_file()

    cli.build_project()
    assert (project / 'dist/src/index.py').is_file()
    assert (project / 'dist/serve.py').is_file()
    assert (project / 'dist/pyproject.toml').is_file()


def test_generate_errors_and_build_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit): cli.generate_component('Missing')
    with pytest.raises(SystemExit): cli.generate_hook('Missing')
    with pytest.raises(SystemExit): cli.build_project()


def test_dev_server_validation_and_delegation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        cli.run_dev_server(open_browser_window=False)
    (tmp_path / 'pyproject.toml').write_text('[tool.pyreact]\n', encoding='utf-8')
    with pytest.raises(SystemExit):
        cli.run_dev_server(open_browser_window=False)
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src/index.py').write_text('def App(props): pass\n', encoding='utf-8')
    called = {}
    monkeypatch.setattr('pyreact.runtime.serve', lambda **kwargs: called.update(kwargs))
    cli.run_dev_server(4321, open_browser_window=False, host='localhost')
    assert called == {
        'entry': 'src/index.py', 'host': 'localhost', 'port': 4321, 'public_dir': 'public',
        'title': 'PyReact App',
    }


@pytest.mark.parametrize('arguments,expected', [
    (['pyreact', 'create', 'from-main'], 'from-main'),
])
def test_main_dispatch_create(tmp_path, monkeypatch, arguments, expected):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, 'argv', arguments)
    cli.main()
    assert (tmp_path / expected).is_dir()


def test_main_dispatch_generate_build_test_and_help(tmp_path, monkeypatch, capsys):
    project = tmp_path / 'project'
    monkeypatch.chdir(tmp_path)
    cli.create_project('project')
    monkeypatch.chdir(project)

    monkeypatch.setattr(sys, 'argv', ['pyreact', 'generate', 'component', 'Card', '--class'])
    cli.main()
    monkeypatch.setattr(sys, 'argv', ['pyreact', 'generate', 'hook', 'state'])
    cli.main()
    monkeypatch.setattr(sys, 'argv', ['pyreact', 'build'])
    cli.main()
    assert (project / 'dist').is_dir()

    monkeypatch.setattr(cli, 'run_tests', lambda: None)
    monkeypatch.setattr(sys, 'argv', ['pyreact', 'test'])
    cli.main()
    monkeypatch.setattr(cli, 'run_dev_server', lambda *args, **kwargs: None)
    monkeypatch.setattr(sys, 'argv', ['pyreact', 'dev', '--host', 'localhost', '--no-open'])
    cli.main()
    monkeypatch.setattr(sys, 'argv', ['pyreact'])
    cli.main()
    assert 'usage:' in capsys.readouterr().out


def test_run_tests_exit_code(monkeypatch):
    result = type('Result', (), {'returncode': 7})()
    monkeypatch.setattr('subprocess.run', lambda *args, **kwargs: result)
    with pytest.raises(SystemExit) as error:
        cli.run_tests()
    assert error.value.code == 7
