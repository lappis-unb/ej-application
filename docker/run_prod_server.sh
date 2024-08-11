#!/usr/bin/env bash

# includes poetry binary in $PATH
export PATH="/root/.local/bin:$PATH"

# prepare database
inv db

if [ "$SERVER_MODE" != "api" ]; then
    # install js dependencies
    (cd src/$EJ_THEME/static/$EJ_THEME/ && npm i)

    # prepare all assets (js, css)
    inv build-assets

    # generate translations
    inv i18n
    inv i18n --compile

    # generates documentation
    inv docs

    # runs django collectstatic command
    inv collect
fi

# runs prod server
inv gunicorn
