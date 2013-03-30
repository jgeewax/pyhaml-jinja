# PyHaml Jinja

Haml-style syntax for Jinja2 templates

## NOT FOR PRODUCTION USE

This package is still very young and
therefore not quite ready for production.
Please report lots of bugs via the issue tracker so that it might become
something production ready.

## Overview

This tool makes it easy to use HAML-style syntax in your Jinja templates.
It uses Pythonic syntax
and aims to provide useful error messages
when debugging your templates.

It is a pre-processor,
meaning it takes a HAML source file,
and outputs a template to be further processed by Jinja.

## Installation

Use `pip` or `easy_install` to install this package:

    $ easy_install pip # If you don't already have it.
    $ pip install pyhaml-jinja

## Usage

To use this extension, add it to you Jinja environment and use the ".haml" 
extension for your template files.

    from jinja2 import Environment
    from pyhaml_jinja import HamlExtension

    env = Environment(extensions=[HamlExtension])

## Syntax

### Tags

This uses the standard HAML tag definitions:

    %div
      .cls1
        text
      #my-div
        text

becomes

    <div>
      <div class="cls1">
        text
      </div>
      <div id="my-div">
        text
      </div>
    </div>

### In-line data

You don't need a newline to add data to a tag:

    %div inline-data

becomes

    <div>
      inline-data
    </div>

### Nested tags

You don't need a newline to nest tags either:

    %div: %p text

becomes

    <div>
      <p>
        text
      </p>
    </div>

### Attributes

For attributes, use the same style you would pass into a Python `dict()` call (with double quotes):

    %div(a="1", b="2")
      #my-div(c="3")
        text

becomes

    <div a="1" b="2">
      <div id="my-div" c="3">
        text
      </div>
    </div>

### Line continuations

Use a backslash character to continue a line:

    %div(a="1" \
         b="2")
      text

becomes

    <div a="1" b="2">
      text
    </div>

### Preformatted text

Use a pipe character (|) for pre-formatted text:

    %pre
      |text
      |  text
      | text

becomes

    <pre>text
      text
     text
    </pre>

### Special character literals

Use a backslash to use one of the reserved characters without parsing it:

    %div
      \%div

becomes

    <div>
      %div
    </div>

### Comments

Use a semicolor (;) for HAML comments:

    %div
      ; This is a comment

becomes

    <div>
    </div>

You can still use Jinja-style comments, or HTML comments:

    %div
      {% This is a comment %}
      ! This is a comment

becomes

    <div>
      {% This is a comment %}
      <!-- This is a comment -->
    </div>

### Special blocks

For Javascript, plain-text, or CSS (so far...) use `:javascript`, `:plain`, and `:css`:

    :javascript
      alert('hi');
    :css
      body { border: none; }
    :plain
      text

becomes

    <script type="text/javascript">
      alert('hi');
    </script>
    <style type="text/css">
      body { border: none; }
    </style>
    text

### Jinja tags

Wherever you would use `{% tag ... %}`, use `-tag ...` and indentation:

    -if True
      true
    -else
      false

becomes

    {% if True %}
      true
    {% else %}
      false
    {% endif %}

### Jinja variables

Wherever you would use `{{ ... }}}` use `#{...}`:

    %div #{my_var}

becomes

    <div>
      {{ my_var }}
    </div>

### All your old tags are still valid -- the HAML is just gravy

If you need special whitespace control,
or have a tag that doesn't work properly,
just use the Jinja tag as always:

    %h1 title
    <a href="#">anchor</a>
    {%- if True -%}
      text
    {% endif -%}

becomes

    <h1>
      title
    </h1>
    <a href="#">anchor</a>
    {%- if True %}
      text
    {% endif -%}

