from ..commands.upstream2_typer import app

# do not create a new app as with inheritance -
# instead work directly with the upstream app.


# override init
@app.callback()
def init():
    return "plugin:init"


# override sub1
@app.command()
def sub1():
    return "plugin:sub1"


# add a 3rd top level command
@app.command()
def sub3():
    return "plugin:sub3"


# add a new subcommand to grp1
@app.grp1.command()
def grp1_cmd2():
    return "plugin:grp1_cmd2"
