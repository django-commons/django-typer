#!/usr/bin/env python
import typing as t

import typer

app = typer.Typer(name="test")
state = {"verbose": False}


@app.command()
def create(
    username: str,
    password: t.Annotated[
        t.Optional[str],
        typer.Option("--password", hide_input=True, prompt=True),
    ] = None,
):
    if state["verbose"]:
        print("About to create a user")
    print(f"Creating user: {username}")
    if state["verbose"]:
        print("Just created a user")
    print(f"password: {password}")


@app.command(epilog="Delete Epilog")
def delete(username: str):
    if state["verbose"]:
        print("About to delete a user")
    print(f"Deleting user: {username}")
    if state["verbose"]:
        print("Just deleted a user")


@app.callback(epilog="Main Epilog")
def main(verbose: bool = False):
    """
    Manage users in the awesome CLI app.
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


# app.command(name="common")(_common_options)


# @app.command(cls=TyperCommandWrapper)
# def wrapped(name: str):
#     """This is a wrapped command"""
#     print("wrapped(%s)" % name)


if __name__ == "__main__":
    app()
