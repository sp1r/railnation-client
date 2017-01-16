#!/bin/sh

export PYTHONPATH=${PYTHONPATH}:`dirname $0`/lib

exec python3 -m railnation $@
