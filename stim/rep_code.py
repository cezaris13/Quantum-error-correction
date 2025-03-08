from typing import List


def create_rep_code_stim_string(distance: int, rounds: int, p: float) -> str:
    total_qubits = 2 * distance - 1
    total_qubits_ids = range(total_qubits)
    measure_qubits_ids = total_qubits_ids[1::2]
    data_qubits_ids = total_qubits_ids[::2]
    measure_qubits = len(measure_qubits_ids)
    data_qubits = len(data_qubits_ids)

    total_sequence = ""

    total_sequence += reset_qubits(total_qubits_ids)
    total_sequence += add_error(total_qubits_ids, p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[: total_qubits - 1])
    total_sequence += depolarize2(total_qubits_ids[: total_qubits - 1], p)
    total_sequence += depolarize1([total_qubits_ids[-1]], p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[::-1][: total_qubits - 1])
    total_sequence += depolarize1([total_qubits_ids[0]], p)
    total_sequence += depolarize2(total_qubits_ids[1:], p)
    total_sequence += add_tick()

    # put error for the measure qubits
    total_sequence += add_error(measure_qubits_ids, p)
    total_sequence += measure(measure_qubits_ids)

    total_sequence += depolarize1(data_qubits_ids, p)

    # this one takes detector measurements qubits, only the current measurement
    for id, i in enumerate(measure_qubits_ids):
        total_sequence += f"DETECTOR({i}, 0) rec[-{measure_qubits - id}]\n"

    if rounds > 2:
        total_sequence += "REPEAT {times} {{\n".format(times=rounds - 2)
        total_sequence += reset_qubits(measure_qubits_ids)
        total_sequence += add_error(measure_qubits_ids, p)
        total_sequence += depolarize1(data_qubits_ids, p)
        total_sequence += add_tick()

        total_sequence += add_control_gates(total_qubits_ids[: total_qubits - 1])
        total_sequence += depolarize2(total_qubits_ids[: total_qubits - 1], p)
        total_sequence += depolarize1([total_qubits_ids[-1]], p)
        total_sequence += add_tick()

        total_sequence += add_control_gates(total_qubits_ids[::-1][: total_qubits - 1])
        total_sequence += depolarize1([total_qubits_ids[0]], p)
        total_sequence += depolarize2(total_qubits_ids[1:], p)
        total_sequence += add_tick()

        total_sequence += add_error(measure_qubits_ids, p)
        total_sequence += measure(measure_qubits_ids)

        total_sequence += depolarize1(data_qubits_ids, p)

        total_sequence += "SHIFT_COORDS(0, 1)\n"
        # this one takes detector measurements horizontally in time, the same measure qubit current that qubit measure and the previous one.
        for id, i in enumerate(measure_qubits_ids):
            total_sequence += f"DETECTOR({i}, 0) rec[-{measure_qubits - id}] rec[-{2 * measure_qubits - id}]\n"

        total_sequence += "}\n"

    total_sequence += reset_qubits(measure_qubits_ids)
    total_sequence += add_error(measure_qubits_ids, p)
    total_sequence += depolarize1(data_qubits_ids, p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[: total_qubits - 1])
    total_sequence += depolarize2(total_qubits_ids[: total_qubits - 1], p)
    total_sequence += depolarize1([total_qubits_ids[-1]], p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[::-1][: total_qubits - 1])
    total_sequence += depolarize1([total_qubits_ids[0]], p)
    total_sequence += depolarize2(total_qubits_ids[1:], p)
    total_sequence += add_tick()

    total_sequence += add_error(total_qubits_ids, p)
    total_sequence += measure(measure_qubits_ids)
    total_sequence += measure(data_qubits_ids)

    total_sequence += "SHIFT_COORDS(0, 1)\n"

    # this one takes detector measurements horizontally in time, the same measure qubit current that qubit measure and the previous one.
    for id, i in enumerate(measure_qubits_ids):
        total_sequence += f"DETECTOR({i}, 0) rec[-{data_qubits + measure_qubits - id}] rec[-{data_qubits + 2*measure_qubits -id}]\n"

    # this one takes detector measurements vertically around the measure qubit up and down
    for id, i in enumerate(measure_qubits_ids):
        total_sequence += f"DETECTOR({i}, 0) rec[-{data_qubits + measure_qubits - id}] rec[-{measure_qubits - id + 1}] rec[-{measure_qubits - id}]\n"

    total_sequence += "OBSERVABLE_INCLUDE(0) rec[-1]\n"

    return total_sequence


def reset_qubits(qubits: List[int]) -> str:
    return f"R {int_list_to_string(qubits)}\n"


def add_error(qubits: List[int], error: float) -> str:
    return f"X_ERROR({error}) {int_list_to_string(qubits)}\n"


def add_tick() -> str:
    return "TICK\n"


def add_control_gates(qubits: List[int]) -> str:
    return f"CX {int_list_to_string(qubits)}\n"


# When the noise applies it randomly picks X,Y, Z error
def depolarize1(qubits: List[int], error: float) -> str:
    return f"DEPOLARIZE1({error}) {int_list_to_string(qubits)}\n"


## It'll pick error for both operator parts and apply not 2 identity operators
def depolarize2(qubits: List[int], error: float) -> str:
    return f"DEPOLARIZE2({error}) {int_list_to_string(qubits)}\n"


def measure(qubits: List[int]) -> str:
    return f"M {int_list_to_string(qubits)}\n"


def int_list_to_string(elements: List[int]) -> str:
    return " ".join(str(element) for element in elements)
