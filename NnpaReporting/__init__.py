# -----------------------------------------------------------
# Copyright (C) 2024 Lutra Consulting
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

from .reporting_tool import ReportingTool


def classFactory(iface):
    return ReportingTool(iface)
