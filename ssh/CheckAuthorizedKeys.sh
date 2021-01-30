#!/bin/bash

_dirname=$(dirname $0)
_basename=$(basename $0)
_basena=${_basename%%.sh}

VENV=${VENV:-"${_dirname}/../venv"}
source "${VENV}/bin/activate"
exec "${_dirname}/${_basena}.py" $*
