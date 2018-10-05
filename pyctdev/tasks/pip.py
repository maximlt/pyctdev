"""
"""

from .. import params

from ..task import DoitTask

from ._pip import _pip_install_with_options, _twine_upload, _maybe_sdist_build_deps, test_package, pkg_exists, build_pkg

from . import register as some_register, list_test_envs, env_capture, develop_install, package_upload, package_build, package_test 

from .._doithacks import CmdAction2


def register(x): return some_register('pip', x)


# TODO: could this be universal? see conda.py
register(
    DoitTask(
        task_type=list_test_envs,
        actions=[CmdAction2('tox -l')])
)

register(
    DoitTask(
        task_type=env_capture,
        # TODO: should do other stuff too...?
        actions=[CmdAction2("pip freeze")]))


# TODO: missing vs. conda
#  - env_dependency_graph
#  - package_test
#  - env_file_generate
#  - env_create


register(
    DoitTask(
        task_type=develop_install,
        actions=[CmdAction2(_pip_install_with_options)],
        params=[
            {**params.extra, 'default': ['tests']},
            params.channel,
            params.all_extras]))


register(
    DoitTask(
        task_type=package_upload,
        additional_doc="""upload pip packages to pypi""",
        task_dep=["package_test"],
        params=[
            params.sdist,
            params.user,
            params.password,
            {'name': 'pypi',
             'long': 'pypi',
             'type': str,
             'default': 'testpypi'}
        ],
        actions=[CmdAction2(_twine_upload)]))


register(
    DoitTask(
        task_type=package_build,
        additional_doc="""Build pip package, then install and test all_quick (or other
    specified env) in venv

    Won't rebuild if version hasn't changed. Will always rebuild if 'dirty' in versoin.

    E.g.

    ``doit package_build --formats=bdist_wheel``
    ``doit package_build -e all_quick-Ewith_numpy``

        """,
        uptodate=[pkg_exists],
        params=[  # TODO missing some form of
            # params.pin_deps
            # params.pin_deps_as_env
            # params.force
            # params.purge
            # params.universal_wheel,
            params.sdist,
            # pip only
            {'name': 'sdist_install_build_deps',
             'long': 'sdist-install-build-deps',
             'type': bool,
             'default': False},
        ],
        actions=[CmdAction2(_maybe_sdist_build_deps),
                 CmdAction2(build_pkg),
                 ]))


register(
    DoitTask(
        task_type=package_test,
        additional_doc="The test groups selected determine which optional extras (if any) will be installed. See tox.ini for mappings.",
        task_dep=["package_build"],
        params=[params.test_python,
                params.test_group,
                params.test_requires,
                params.channel,
                params.sdist
                ],
        actions=[CmdAction2(test_package)]))
