# SPDX-FileCopyrightText: 2021-present M. Coleman, J. Cook, F. Franza
# SPDX-FileCopyrightText: 2021-present I.A. Maione, S. McIntosh
# SPDX-FileCopyrightText: 2021-present J. Morris, D. Short
#
# SPDX-License-Identifier: LGPL-2.1-or-later

"""
Tests for the plotter module.
"""

from dataclasses import asdict

import numpy as np
import pytest

from bluemira.base.components import Component, PhysicalComponent
from bluemira.base.constants import EPS
from bluemira.display import plot_2d, plot_3d, plotter
from bluemira.display.error import DisplayError
from bluemira.geometry import face, placement, tools
from bluemira.utilities.plot_tools import Plot3D

SQUARE_POINTS = np.array([
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0),
    (1.0, 0.0, 1.0),
    (0.0, 0.0, 1.0),
])


class TestPlotOptions:
    def setup_method(self):
        self.default = plotter.DefaultPlotOptions()

    def test_default_options(self):
        """
        Check the values of the default options correspond to the global defaults.
        """
        the_options = plotter.PlotOptions().as_dict()
        default_dict = asdict(self.default)
        d_view = default_dict.pop("view")
        o_view = the_options.pop("view")
        assert the_options == default_dict
        assert the_options is not default_dict
        for no, d in enumerate(d_view):
            try:
                assert o_view[no] == d
            except ValueError:  # noqa: PERF203
                assert all(o_view[no] == d)

    def test_options(self):
        """
        Check the values can be set by passing kwargs.
        """
        the_options = plotter.PlotOptions(show_points=True)
        options_dict = the_options.as_dict()

        for key, val in options_dict.items():
            if key == "show_points":
                assert val != getattr(self.default, key)
            elif key == "view":
                for no, d in enumerate(getattr(self.default, key)):
                    try:
                        assert val[no] == d
                    except ValueError:  # noqa: PERF203
                        assert all(val[no] == d)
            else:
                assert val == getattr(self.default, key)

    def test_options_placement_dict(self):
        """
        Check the options can be obtained as a dictionary with a BluemiraPlacement
        """
        the_placement = placement.BluemiraPlacement()
        the_options = plotter.PlotOptions(view=the_placement)
        options_dict = the_options.as_dict()
        for key, val in options_dict.items():
            if key == "view":
                for no, d in enumerate(getattr(self.default, key)):
                    try:
                        assert val[no] != d
                    except ValueError:  # noqa: PERF203
                        assert all(val[no] == d)
                assert val is not the_placement
            else:
                assert val == getattr(self.default, key)

    def test_modify_options(self):
        """
        Check the display options can be modified by passing in keyword args
        """
        the_options = plotter.PlotOptions()
        the_options.modify(show_points=True)
        options_dict = the_options.as_dict()
        for key, val in options_dict.items():
            if key == "show_points":
                assert val != getattr(self.default, key)
            elif key == "view":
                for no, d in enumerate(getattr(self.default, key)):
                    try:
                        assert val[no] == d
                    except ValueError:  # noqa: PERF203
                        assert all(val[no] == d)
            else:
                assert val == getattr(self.default, key)

    def test_dictionary_options_allow_modification(self):
        the_options = plotter.PlotOptions()
        the_options.wire_options["color"] = "blue"
        assert the_options.wire_options["color"] == "blue"

        dupe = plotter.PlotOptions()
        assert dupe.wire_options["color"] == "black"

    def test_dictionary_options_reset_defaults(self):
        the_options = plotter.PlotOptions()
        the_options.wire_options = {"color": "blue"}
        assert the_options.wire_options["color"] == "blue"
        assert the_options.wire_options["linewidth"] == pytest.approx(
            0.5, rel=0, abs=EPS
        )

    def test_wrong_view_str_raises_DisplayError(self):
        the_options = plotter.PlotOptions()
        with pytest.raises(DisplayError):
            the_options.view = "string"

    def test_properties(self):
        """
        Check the display option properties can be accessed
        """
        the_options = plotter.PlotOptions()
        dict_default = asdict(self.default)
        for key, val in dict_default.items():
            if key == "view":
                for no, d in enumerate(getattr(self.default, key)):
                    try:
                        assert val[no] == d
                    except ValueError:  # noqa: PERF203
                        assert all(val[no] == d)
            else:
                assert getattr(the_options, key) == val

        the_options.show_points = not self.default.show_points
        the_options.show_wires = not self.default.show_wires
        the_options.show_faces = not self.default.show_faces
        the_options.point_options = {}
        the_options.wire_options = {}
        the_options.face_options = {}
        the_options.view = "xyz"
        the_options.view = placement.BluemiraPlacement()
        the_options.ndiscr = 20
        the_options.byedges = not self.default.byedges

        for key, val in dict_default.items():
            if key == "view":
                for no, d in enumerate(getattr(self.default, key)):
                    try:
                        assert val[no] == d
                    except ValueError:  # noqa: PERF203
                        assert all(val[no] == d)
            elif key.endswith("options"):
                assert getattr(the_options, key) == val
            else:
                assert getattr(the_options, key) != val


class TestPlot3d:
    """
    Generic 3D plotting tests.
    """

    def test_plot_3d_same_axis(self):
        ax_orig = Plot3D()
        ax_1 = plot_3d(tools.make_circle(), show=False, ax=ax_orig)
        ax_2 = plot_3d(tools.make_circle(radius=2), show=False, ax=ax_1)

        assert ax_1 is ax_orig
        assert ax_2 is ax_orig

    def test_plot_3d_new_axis(self):
        ax_orig = Plot3D()  # Empty axis
        ax_orig.figure.suptitle("EMPTY")
        ax_1 = plot_3d(tools.make_circle(), show=False)
        ax_2 = plot_3d(tools.make_circle(radius=2), show=False)

        assert ax_1 is not ax_2
        assert ax_1 is not ax_orig
        assert ax_2 is not ax_orig


class TestPointsPlotter:
    def test_plotting_2d(self):
        plotter.PointsPlotter().plot_2d(SQUARE_POINTS, show=False)

    def test_plotting_3d(self):
        plotter.PointsPlotter().plot_3d(SQUARE_POINTS, show=False)


class TestWirePlotter:
    def setup_method(self):
        self.wire = tools.make_polygon(SQUARE_POINTS)

    def test_plotting_2d(self):
        plotter.WirePlotter().plot_2d(self.wire, show=False)

    def test_plotting_2d_with_points(self):
        plotter.WirePlotter(show_points=True).plot_2d(self.wire, show=False)

    def test_plotting_3d(self):
        plotter.WirePlotter().plot_3d(self.wire, show=False)

    def test_plotting_3d_with_points(self):
        plotter.WirePlotter(show_points=True).plot_3d(self.wire, show=False)


class TestFacePlotter:
    def setup_method(self):
        wire = tools.make_polygon(SQUARE_POINTS)
        wire.close()
        self.face = face.BluemiraFace(wire)

    def test_plotting_2d(self):
        plotter.FacePlotter().plot_2d(self.face, show=False)

    def test_plotting_2d_with_wire(self):
        plotter.FacePlotter(show_wires=True).plot_2d(self.face, show=False)

    def test_plotting_3d(self):
        plotter.FacePlotter().plot_3d(self.face, show=False)

    def test_plotting_3d_with_wire_and_points(self):
        plotter.FacePlotter(show_wires=True, show_points=True).plot_3d(
            self.face, show=False
        )


class TestComponentPlotter:
    def setup_method(self):
        wire1 = tools.make_polygon(SQUARE_POINTS, closed=True)
        wire2 = tools.make_polygon(SQUARE_POINTS + 2.0, closed=True)
        wire3 = tools.make_polygon(SQUARE_POINTS + 4.0, closed=True)
        wire4 = tools.make_polygon(SQUARE_POINTS + 6.0, closed=True)
        face1 = face.BluemiraFace(wire1)
        face2 = face.BluemiraFace(wire2)
        face3 = face.BluemiraFace(wire3)
        face4 = face.BluemiraFace(wire4)
        # default group
        self.group = Component("Parent")
        self.child1 = PhysicalComponent("Child1", shape=face1, parent=self.group)
        self.child2 = PhysicalComponent("Child2", shape=face2, parent=self.group)
        # make child2 have non-default colour on creation
        self.child2.plot_options.face_options["color"] = "green"

        # custom group
        self.group2 = Component("Components")
        self.group2_options = self.group2.plot_options
        self.group2_options.wire_options = {}
        self.group2_options.show_wires = False
        self.group2_options.face_options = {"color": "red"}
        self.child3 = PhysicalComponent("Child3", shape=face3, parent=self.group2)
        self.child4 = PhysicalComponent("Child4", shape=face4, parent=self.group2)
        self.child4.plot_options.face_options["color"] = "green"

    def test_plotting_2d(self):
        pl = plotter.ComponentPlotter()
        ax = pl.plot_2d(self.group, show=False)
        ax.figure.suptitle("blue face, green face, no wires on blue")

        ax = plot_2d(self.group2, self.group2_options, show=False)
        ax.figure.suptitle("red face and green face, no wires on red")

    def test_plotting_2d_nothing_to_plot(self):
        ax = plotter.ComponentPlotter(show_faces=False).plot_2d(self.group, show=False)
        assert ax is None

    def test_plotting_2d_show_wires(self):
        ax = plotter.ComponentPlotter(show_wires=True).plot_2d(self.group, show=False)
        ax.figure.suptitle("blue face, green face, with wires")

    def test_plotting_3d(self):
        ax = plotter.ComponentPlotter().plot_3d(self.group, show=False)
        ax.figure.suptitle("blue face, green face, no wires on blue")

    def test_plotting_3d_with_wires_and_points(self):
        ax = plotter.ComponentPlotter(show_wires=True, show_points=True).plot_3d(
            self.group, show=False
        )
        ax.figure.suptitle("wires, points, faces")
