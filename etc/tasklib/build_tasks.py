import os

from invoke import task
import environ

from .base import directory, HELP_MESSAGES, set_theme, exec_watch, manage, python

__all__ = ["build_assets", "docs", "i18n", "js", "sass"]

env = environ.Env(
    EJ_THEME=(str, "ej"),
)


@task
def build_assets(ctx):
    """
    Builds all required assets to make EJ ready for deployment.
    """
    from toml import load

    # Build Javascript
    # Parcel already minifies and 'minify' doesn't seem to be helping much.
    print("Building javascript assets")
    js(ctx, minify=False)

    # Build CSS
    config = load(open(directory / "pyproject.toml"))
    for theme in config["tool"]["ej"]["conf"]["themes"]:
        print(f"\nBuilding theme: {theme!r}")
        sass(ctx, minify=True)


@task
def docs(ctx, orm=False):
    """
    Builds Sphinx documentation.
    """
    if orm:
        for app in [
            "ej_users",
            "ej_profiles",
            "ej_conversations",
            "ej_boards",
            "ej_clusters",
            "ej_dataviz",
            "ej_tools",
        ]:
            print(f"Making ORM graph for {app}")
            manage(ctx, "graph_models", app, env={}, output=f"docs/dev-docs/orm/{app}.svg")
    else:
        print("call inv docs --orm to update ORM graphs")

    ctx.run("sphinx-build docs/ build/docs/", pty=True)


@task(
    help={
        "compile": "Compile .po files",
        "edit": "Open poedit to edit translations",
        "lang": "Language",
        "keep-pot": "If true, do not clean up temporary .pot files (debug)",
    }
)
def i18n(ctx, compile=False, edit=False, lang="pt_BR", keep_pot=False):
    """
    Extract messages for translation.
    """
    if edit:
        ctx.run(f"poedit locale/{lang}/LC_MESSAGES/django.po")
    elif compile:
        ctx.run(f"{python} etc/scripts/compilemessages.py")
    else:
        print("Collecting messages")
        manage(ctx, "makemessages", keep_pot=True, locale=lang)

        print("Extract Jinja translations")
        ctx.run("pybabel extract -F etc/babel.cfg -o locale/jinja2.pot .")

        print("Join Django + Jinja translation files")
        ctx.run("msgcat locale/django.pot locale/jinja2.pot --use-first -o locale/join.pot", pty=True)
        ctx.run(r"""sed -i '/"Language: \\n"/d' locale/join.pot""", pty=True)

        print(f"Update locale {lang} with Jinja2 messages")
        ctx.run(f"msgmerge locale/{lang}/LC_MESSAGES/django.po locale/join.pot -U")

        if not keep_pot:
            print("Cleaning up")
            ctx.run("rm locale/*.pot")


@task
def js(ctx, theme=env("EJ_THEME"), watch=False, minify=False):
    """
    Build js assets
    """
    print(f"building {theme} theme")
    build_cmd = "npm run watch" if watch else "npm run build"
    cwd = os.getcwd()
    app_name = theme
    app_root = f"{directory}/src/{app_name}"
    app_static_root = f"{app_root}/static/{theme}"
    try:
        ctx.run(f"rm -rf {app_static_root}/js && mkdir {app_static_root}/js")
        os.chdir(f"{app_static_root}/ts")
        ctx.run(build_cmd)
        if minify:
            minify = f"{app_static_root}/node_modules/.bin/minify"
            base = f"{app_static_root}/js"
            for path in os.listdir(str(base)):
                if path.endswith(".js") and not path.endswith(".min.js"):
                    path = f"{base}/{path}"
                    print(f"Minifying {path}")
                    ctx.run(f"{minify} {path} > {path[:-3]}.min.js")
    finally:
        os.chdir(cwd)

        task(help={**HELP_MESSAGES})


@task
def sass(ctx, theme=env("EJ_THEME"), watch=False, background=False, minify=False):
    """
    Run Sass compiler
    """
    print(f"compiling {theme} theme")
    app_name = theme
    app_root = f"{directory}/src/{app_name}"
    app_static_root = f"{app_root}/static/{theme}"
    minify = f"{app_static_root}/node_modules/.bin/minify"
    scss_root_path = f"{app_static_root}/scss"
    css_root_path = f"{app_static_root}/css"
    ctx.run(f"mkdir -p {css_root_path}")

    def go():
        import sass

        for file in ("main", "hicontrast"):
            try:
                css_path = f"{css_root_path}/{file}.css"
                css_min_path = f"{css_root_path}/{file}.min.css"
                map_path = f"{css_root_path}/{file}.css.map"
                css, sourcemap = sass.compile(
                    filename=str(f"{scss_root_path}/{file}.scss"),
                    source_map_filename=str(map_path),
                    source_map_root=str(css_root_path),
                    source_map_contents=True,
                    source_map_embed=True,
                )
                with open(css_path, "w") as fd:
                    fd.write(css)
                    if minify:
                        ctx.run(f"{minify} {css_path} > {css_min_path}")
                with open(map_path, "w") as fd:
                    fd.write(sourcemap)
            except Exception as exc:
                print(f"ERROR EXECUTING SASS COMPILATION: {exc}")

    exec_watch(scss_root_path, go, name="sass", watch=watch, background=background)
    print("Compilation finished!")
