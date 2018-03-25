#!/usr/bin/env python


import importlib

import click


def get_modules(imports):
    """Import modules into dict mapping name to module."""
    modules = {}
    for module_name in imports:
        modules[module_name] = importlib.import_module(module_name)
    return modules


def make_pipeline_strings(command, placeholder='?'):
    """Parse pipeline into individual components."""
    command_strings = command.split('||')
    pipeline = []
    for string in command_strings:
        if placeholder not in string:
            string = string + '({placeholder})'.format(placeholder=placeholder)
        stage = string.replace(placeholder, 'value').strip()
        pipeline.append(stage)
    return pipeline


def main(command, in_stream, imports, placeholder):
    modules = get_modules(imports)
    pipeline = make_pipeline_strings(command, placeholder)
    for line in in_stream:
        value = line
        for step in pipeline:
            value = eval(step, modules, {'value': value})
        yield value


@click.command()
@click.option('--import', '-i', 'imports', type=str, multiple=True)
@click.option('--placeholder', '-p', type=str, default='?')
@click.argument('command')
@click.argument('in_stream', default=click.get_text_stream('stdin'), required=False)
def cli(imports, command, in_stream, placeholder):
    """Pipe data through python functions."""
    gen = main(command, in_stream, imports, placeholder)
    for line in gen:
        click.echo(line, nl=False)
    click.echo()
