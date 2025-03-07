from typing import List

def create_rep_code_stim_string(distance: int, rounds: int, p: float) -> str:
    total_qubits = 2 * distance - 1
    total_qubits_ids = range(total_qubits)
    measure_qubits_ids = total_qubits_ids[1::2]
    data_qubits_ids = total_qubits_ids[::2]

    total_sequence = ""

    total_sequence += reset_qubits(total_qubits_ids)
    total_sequence += add_error(total_qubits_ids, p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[:total_qubits-1])
    total_sequence += depolarize2(total_qubits_ids[:total_qubits-1], p)
    total_sequence += depolarize1([total_qubits_ids[-1]], p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[::-1][:total_qubits-1])
    total_sequence += depolarize1([total_qubits_ids[0]], p)
    total_sequence += depolarize2(total_qubits_ids[1:], p)
    total_sequence += add_tick()

    # put error for the measure qubits
    total_sequence += add_error(measure_qubits_ids, p)
    total_sequence += measure(measure_qubits_ids)

    total_sequence += depolarize1(data_qubits_ids, p)

    # fix it later
    total_sequence += "DETECTOR(1, 0) rec[-2]\n"
    total_sequence += "DETECTOR(3, 0) rec[-1]\n"

    if rounds > 2:
        total_sequence += "REPEAT {times} {{\n".format(times = rounds - 2)
        total_sequence += reset_qubits(measure_qubits_ids)
        total_sequence += add_error(measure_qubits_ids, p)
        total_sequence += depolarize1(data_qubits_ids, p)
        total_sequence += add_tick()

        total_sequence += add_control_gates(total_qubits_ids[:total_qubits-1])
        total_sequence += depolarize2(total_qubits_ids[:total_qubits-1], p)
        total_sequence += depolarize1([total_qubits_ids[-1]], p)
        total_sequence += add_tick()

        total_sequence += add_control_gates(total_qubits_ids[::-1][:total_qubits-1])
        total_sequence += depolarize1([total_qubits_ids[0]], p)
        total_sequence += depolarize2(total_qubits_ids[1:], p)
        total_sequence += add_tick()

        total_sequence += add_error(measure_qubits_ids, p)
        total_sequence += measure(measure_qubits_ids)

        total_sequence += depolarize1(data_qubits_ids, p)

        # fix it later
        total_sequence += "#SHIFT_COORDS(0, 1)\n"
        total_sequence += "DETECTOR(1, 0) rec[-2] rec[-4]\n"
        total_sequence += "DETECTOR(3, 0) rec[-1] rec[-3]\n"
        total_sequence += "}\n"

    total_sequence += reset_qubits(measure_qubits_ids)
    total_sequence += add_error(measure_qubits_ids, p)
    total_sequence += depolarize1(data_qubits_ids, p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[:total_qubits-1])
    total_sequence += depolarize2(total_qubits_ids[:total_qubits-1], p)
    total_sequence += depolarize1([total_qubits_ids[-1]], p)
    total_sequence += add_tick()

    total_sequence += add_control_gates(total_qubits_ids[::-1][:total_qubits-1])
    total_sequence += depolarize1([total_qubits_ids[0]], p)
    total_sequence += depolarize2(total_qubits_ids[1:], p)
    total_sequence += add_tick()

    total_sequence += add_error(total_qubits_ids, p)
    total_sequence += measure(measure_qubits_ids) ## why?
    total_sequence += measure(data_qubits_ids) ## why?

    # fix it later
    total_sequence += "#SHIFT_COORDS(0, 1)\n"
    total_sequence += "DETECTOR(1, 0) rec[-5] rec[-7]\n"
    total_sequence += "DETECTOR(3, 0) rec[-4] rec[-6]\n"
    total_sequence += "DETECTOR(1, 0) rec[-2] rec[-3] rec[-5]\n"
    total_sequence += "DETECTOR(3, 0) rec[-1] rec[-2] rec[-4]\n"
    total_sequence += "OBSERVABLE_INCLUDE(0) rec[-1]\n"

    return total_sequence

def reset_qubits(qubits: List[int]) -> str:
    return "R {elements}\n".format(elements = int_list_to_string(qubits))

def add_error(qubits: List[int], error: float) -> str:
   return "X_ERROR({error}) {elements}\n".format(error=error, elements = int_list_to_string(qubits))

def add_tick() -> str:
    return "TICK\n"

def add_control_gates(qubits: List[int]) -> str:
    return "CX {elements}\n".format(elements = int_list_to_string(qubits))

def depolarize1(qubits: List[int], error: float) -> str:
    return "DEPOLARIZE1({error}) {elements}\n".format(error = error, elements= int_list_to_string(qubits))

def depolarize2(qubits: List[int], error: float) -> str:
    return "DEPOLARIZE2({error}) {elements}\n".format(error = error, elements= int_list_to_string(qubits))

def measure(qubits: List[int]) -> str:
    return "M {elements}\n".format(elements = int_list_to_string(qubits))

def int_list_to_string(elements: List[int]) -> str:
    return " ".join(str(element) for element in elements)