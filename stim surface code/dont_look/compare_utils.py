from .correct_surface_code import *
import stim

import sys

sys.path.append("..")
from Utils.utils import compare_plt_fig, compare_svg_diagram


def compare_circuit(
    circuit1, circuit2, without_noise=False, diagram_type="timeline-svg"
):
    if without_noise:
        circuit1 = circuit1.without_noise()
        circuit2 = circuit2.without_noise()
    d1, d2 = circuit1.diagram(diagram_type), circuit2.diagram(diagram_type)
    return compare_svg_diagram(d1, d2)


def compare_lattice(
    circuit, distance, p, without_noise=False, diagram_type="timeline-svg"
):
    c2 = stim.Circuit(coord_circuit(distance) + lattice_with_noise(distance, p))
    return compare_circuit(circuit, c2, without_noise, diagram_type)


def compare_stabilizers(
    circuit, distance, p, without_noise=False, diagram_type="timeline-svg"
):
    c2 = stim.Circuit(coord_circuit(distance) + stabilizers_with_noise(distance, p))
    return compare_circuit(circuit, c2, without_noise, diagram_type)


def compare_initialization(
    circuit, distance, p, without_noise=False, diagram_type="timeline-svg"
):
    c2 = stim.Circuit(coord_circuit(distance) + initialization_step(distance, p))
    return compare_circuit(circuit, c2, without_noise, diagram_type)


def compare_init_and_rounds(
    circuit, distance, rounds, p, without_noise=False, diagram_type="timeline-svg"
):
    c2 = stim.Circuit(
        coord_circuit(distance)
        + initialization_step(distance, p)
        + rounds_step(distance, rounds, p)
    )
    return compare_circuit(circuit, c2, without_noise, diagram_type)


def compare_surface(
    circuit, distance, rounds, p, without_noise=False, diagram_type="timeline-svg"
):
    c2 = stim.Circuit(surface_code_circuit_string(distance, rounds, p))
    return compare_circuit(circuit, c2, without_noise, diagram_type)


def compare_error_per_shot(fig):
    return compare_plt_fig(fig, "dont_look/error_per_shot.png")


def compare_error_per_round(fig):
    return compare_plt_fig(fig, "dont_look/error_per_round.png")


def compare_projection(fig):
    return compare_plt_fig(fig, "dont_look/projection.png")
