"""The DSir Python curriculum, ordered by dependency."""

from . import (
    m01_foundations,
    m02_setup,
    m03_values,
    m04_operators_strings,
    m05_decisions,
    m06_loops,
    m07_collections,
    m08_functions,
    m09_modules,
    m10_files,
    m11_debugging,
    m12_oop,
    m13_algorithms,
    m14_testing_git,
    m15_apis,
    m16_sql,
    m17_automation,
    m18_fastapi,
    m19_deploy_security,
    m20_portfolio,
)

MODULES = [
    m01_foundations.MODULE,
    m02_setup.MODULE,
    m03_values.MODULE,
    m04_operators_strings.MODULE,
    m05_decisions.MODULE,
    m06_loops.MODULE,
    m07_collections.MODULE,
    m08_functions.MODULE,
    m09_modules.MODULE,
    m10_files.MODULE,
    m11_debugging.MODULE,
    m12_oop.MODULE,
    m13_algorithms.MODULE,
    m14_testing_git.MODULE,
    m15_apis.MODULE,
    m16_sql.MODULE,
    m17_automation.MODULE,
    m18_fastapi.MODULE,
    m19_deploy_security.MODULE,
    m20_portfolio.MODULE,
]

PROJECTS = [
    item
    for module in MODULES
    for item in module.get("projects", [])
]
