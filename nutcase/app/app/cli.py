# import os
# import click

def register(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass
