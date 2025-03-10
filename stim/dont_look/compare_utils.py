from .correct_rep_code import create_rep_code_stim_string
import stim

import sys

sys.path.append("..")
from Utils.utils import compare_plt_fig, compare_svg_diagram


def compare_circuit_timelines(circuit1, circuit2):
    d1, d2 = circuit1.diagram("timeline-svg"), circuit2.diagram("timeline-svg")
    return compare_svg_diagram(d1, d2)


def compare_part1(circuit):
    return compare_circuit_timelines(
        circuit, stim.Circuit.from_file("dont_look/correct_part1.stim")
    )


def compare_part2(circuit):
    return compare_circuit_timelines(
        circuit, stim.Circuit.from_file("dont_look/correct_part2.stim")
    )


def compare_part3(circuit):
    return compare_circuit_timelines(
        circuit, stim.Circuit.from_file("dont_look/correct_part3.stim")
    )


def compare_repcode(circuit, distance, rounds, p):
    return compare_circuit_timelines(
        circuit, stim.Circuit(create_rep_code_stim_string(distance, rounds, p))
    )


def compare_repcode_plot1(fig):
    return compare_plt_fig(fig, "dont_look/repcode_plot1.png")


def compare_repcode_plot2(fig):
    return compare_plt_fig(fig, "dont_look/repcode_plot2.png")


def compare_repcode_plot3(fig):
    return compare_plt_fig(fig, "dont_look/repcode_plot3.png")
