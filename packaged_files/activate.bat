@echo off

REM Add a prompt the cmd line
set PROMPT=(umuenv)$P$G

REM Set venv dir to umuenv
pushd %~dp0
set UMUENV_DIR=%CD%
popd

set UMU_HEADERS=%UMUENV_DIR%\include
set UMU_LIBS=%UMUENV_DIR%\libs