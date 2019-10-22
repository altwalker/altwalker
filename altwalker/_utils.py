import platform
import subprocess
import signal
import os

import psutil
import click


def kill(pid):
    """Send the SIGINT signal to a process and all its children."""

    process = psutil.Process(pid)

    for child in process.children(recursive=True):
        os.kill(child.pid, signal.SIGINT)

    os.kill(process.pid, signal.SIGINT)


def get_command(command_name):
    command = ["cmd.exe", "/C"] if platform.system() == "Windows" else []
    command.append(command_name)

    return command


def url_join(base, url):
    """Join a base with an url."""

    return "{}/{}".format(base.strip("/"), url.strip("/"))


def has_git():
    """Returns True if it can run ``git --version``, otherwise returns False."""

    try:
        process = subprocess.Popen(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response = process.communicate()

        return response[1] == b""
    except FileNotFoundError:
        return False


def click_formatwarning(message, category, filename, lineno, file=None, line=None):
    """Format a warning on a single line and style the text."""

    return click.style("{}: {}\n".format(category.__name__, message), fg="yellow")


def _percentege_color(percentage):
    if percentage < 50:
        return "red"

    if percentage < 80:
        return "yellow"

    return "green"


def _style_percentage(percentege):
    return click.style("{}%".format(percentege), fg=_percentege_color(percentege))


def _style_fail(number):
    color = "red" if number > 0 else "green"

    return click.style(str(number), fg=color)


def _echo_stat(title, value, indent=2):
    title = " " * indent + title.ljust(30, ".")
    value = str(value).rjust(15, ".")

    click.echo(title + value)


def echo_statistics(statistics):
    """Pretty-print statistics."""

    click.echo("Statistics:")
    click.echo()

    total_models = statistics["totalNumberOfModels"]
    completed_models = statistics["totalCompletedNumberOfModels"]
    model_coverage = _style_percentage(completed_models * 100 // total_models)

    _echo_stat("Model Coverage", model_coverage)
    _echo_stat("Number of Models", click.style(str(total_models), fg="white"))
    _echo_stat("Completed Models", click.style(str(completed_models), fg="white"))

    _echo_stat("Failed Models", _style_fail(statistics["totalFailedNumberOfModels"]))
    _echo_stat("Incomplete Models", _style_fail(statistics["totalIncompleteNumberOfModels"]))
    _echo_stat("Not Executed Models", _style_fail(statistics["totalNotExecutedNumberOfModels"]))
    click.echo()

    edge_coverage = _style_percentage(statistics["edgeCoverage"])
    _echo_stat("Edge Coverage", edge_coverage)

    total_edges = statistics["totalNumberOfEdges"]
    _echo_stat("Number of Edges", click.style(str(total_edges), fg="white"))
    _echo_stat("Visited Edges", click.style(str(statistics["totalNumberOfVisitedEdges"]), fg="white"))
    _echo_stat("Unvisited Edges", click.style(str(statistics["totalNumberOfUnvisitedEdges"]), fg="white"))
    click.echo()

    vertex_coverage = _style_percentage(statistics["vertexCoverage"])
    _echo_stat("Vertex Coverage", vertex_coverage)

    total_vertices = statistics["totalNumberOfVertices"]
    _echo_stat("Number of Vertices", click.style(str(total_vertices), fg="white"))
    _echo_stat("Visited Vertices", click.style(str(statistics["totalNumberOfVisitedVertices"]), fg="white"))
    _echo_stat("Unvisited Vertices", click.style(str(statistics["totalNumberOfUnvisitedVertices"]), fg="white"))
    click.echo()


def echo_status(status):
    """Pretty-print status."""

    status_message = "PASS" if status else "FAIL"

    click.echo("Status: ", nl=False)
    click.secho(" {} ".format(status_message), bg="green" if status else "red")
    click.echo()
