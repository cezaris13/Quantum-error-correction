# ============================
# Provided utility functions


def data_coords(distance):
    # Returns coordinate pairs from (1,1) to (distance,distance).
    coords = []
    for row in range(1, distance + 1):
        for col in range(1, distance + 1):
            coords.append((col, row))
    return coords


def z_measure_coords(distance):
    # Returns coordinate pairs for Z measure qubits, offset from
    #  the data qubits by 0.5.
    coords = []
    for row in range(1, distance):  # don't include the last row
        for col in range(1, distance + 1, 2):  # only take every other qubit
            if row % 2:
                coords.append((col - 0.5, row + 0.5))
            else:
                coords.append((col + 0.5, row + 0.5))
    return coords


def x_measure_coords(distance):
    # Returns coordinate pairs for X measure qubits, offset from
    #  the data qubits by 0.5 and opposite the Y measure qubits.
    coords = []
    for row in range(1, distance + 2):  # include extra for last row measures
        for col in range(2, distance, 2):  # start from second column, ignore last
            if row % 2:
                coords.append((col + 0.5, row - 0.5))
            else:
                coords.append((col - 0.5, row - 0.5))
    return coords


def coords_to_index(coords):
    # Inverts a list of coordinates into a dict that maps the coord
    #  to its index in the list.
    return {tuple(c): i for i, c in dict(enumerate(coords)).items()}


# returns false if the coordinate exists (useful with edge cases)
def adjacent_coords(
    distance: int, coord: (float, float), x_stabilizer: bool = True
) -> [((float, float), bool)]:
    data, _, _, _ = prepare_coords(distance)

    # Returns the four coordinates at diagonal 0.5 offsets from the input coord.
    # Follows the X-stabilizer plaquette corner ordering from the lecture:
    #  top-left, top-right, bottom-left, bottom-right.
    col, row = coord
    adjacents = [
        (col - 0.5, row - 0.5),
        (col + 0.5, row - 0.5),
        (col - 0.5, row + 0.5),
        (col + 0.5, row + 0.5),
    ]

    # for Z stabilizer, и pattern
    if not x_stabilizer:
        adjacents[1], adjacents[2] = adjacents[2], adjacents[1]

    coordinates = []
    for coord in adjacents:
        coordinates.append((coord, coord in data))

    return coordinates


def index_string(coord_list, c2i):
    # Returns the indicies for each coord in a list as space-delimited string.
    return " ".join(str(c2i[coord]) for coord in coord_list)


def prepare_coords(distance: int):
    # Returns coordinates for data qubits, x measures and z measures, along with
    #  a coordinate-to-index mapping for all of the qubits.
    # The indices are ordered: data first, then x measures, then z measures.
    datas = data_coords(distance)
    x_measures = x_measure_coords(distance)
    z_measures = z_measure_coords(distance)
    c2i = coords_to_index(datas + x_measures + z_measures)
    return datas, x_measures, z_measures, c2i


def coord_circuit(distance):
    # Returns a Stim circuit string that adds a QUBIT_COORDS instruction for each
    #  qubit, based on the coordinate-to-index mapping.
    _, _, _, c2i = prepare_coords(distance)
    stim_circuit = ""
    for coord, index in c2i.items():
        stim_circuit += f"QUBIT_COORDS({','.join(map(str, coord))}) {index}\n"
    return stim_circuit


def label_indices(distance):
    # Returns a Stim circuit string that labels each of the qubits with their
    #  type and index in the coordinate-to-index mapping.
    # Uses ERROR operations to do the labeling: X_ and Z_ERRORs correspond to
    #  qubits that will be used for X and Z type stabilizer measurements, and
    #  Y_ERRORs label the data qubits.
    # The index of the qubit is encoded in the operation's error probability:
    #  The value after the decimal is the index. Eg. 0.01 is 1 and 0.1 is 10.
    datas, x_measures, z_measures, c2i = prepare_coords(distance)
    all_qubits = datas + x_measures + z_measures
    i = 0
    stim_string = ""
    for coord in datas:
        stim_string += f"Y_ERROR(0.{i:>02}) {c2i[coord]}\n"
        i += 1
    stim_string += "TICK\n"
    for coord in x_measures:
        stim_string += f"X_ERROR(0.{i:>02}) {c2i[coord]}\n"
        i += 1
    stim_string += "TICK\n"
    for coord in z_measures:
        stim_string += f"Z_ERROR(0.{i:>02}) {c2i[coord]}\n"
        i += 1

    return stim_string


# ======================================================
# hidden answer functions


def lattice_with_noise(distance: int, p: float) -> str:
    data, x_measures, z_measures, c2i = prepare_coords(distance)

    adjacent_z = {
        z: adjacent_coords(distance, z, x_stabilizer=True) for z in z_measures
    }
    adjacent_x = {
        x: adjacent_coords(distance, x, x_stabilizer=False) for x in x_measures
    }

    stim_string = f""
    for i in range(4):
        used_qubits = set()

        for z_measure in z_measures:
            adjacent_coordinate, coordinate_exists = adjacent_z[z_measure][i]
            if coordinate_exists:
                used_qubits.update([adjacent_coordinate, z_measure])
                stim_string += f"CX {c2i[adjacent_coordinate]} {c2i[z_measure]}\n"

        for x_measure in x_measures:
            adjacent_coordinate, coordinate_exists = adjacent_x[x_measure][i]
            if coordinate_exists:
                used_qubits.update([adjacent_coordinate, x_measure])
                stim_string += f"CX {c2i[x_measure]} {c2i[adjacent_coordinate]}\n"

        for z_measure in z_measures:
            adjacent_coordinate, coordinate_exists = adjacent_z[z_measure][i]
            if coordinate_exists:
                stim_string += (
                    f"DEPOLARIZE2({p}) {c2i[adjacent_coordinate]} {c2i[z_measure]}\n"
                )

        for x_measure in x_measures:
            adjacent_coordinate, coordinate_exists = adjacent_x[x_measure][i]

            if coordinate_exists:
                stim_string += (
                    f"DEPOLARIZE2({p}) {c2i[x_measure]} {c2i[adjacent_coordinate]}\n"
                )

        for key, value in c2i.items():
            if not key in used_qubits:
                stim_string += f"DEPOLARIZE1({p}) {value}\n"

        stim_string += "TICK\n"

    return stim_string


def stabilizers_with_noise(distance, p):
    datas, x_measures, z_measures, c2i = prepare_coords(distance)
    all_measures = x_measures + z_measures
    all_qubits = datas + all_measures
    # Use `lattice_with_noise` to create a full lattice of stabilizers
    #  including the resets and measurements. No detectors yet.
    stim_string = f""
    return NotImplemented


def initialization_step(distance, p):
    datas, x_measures, z_measures, c2i = prepare_coords(distance)
    all_measures = x_measures + z_measures
    all_qubits = datas + all_measures
    # Use `lattice_with_noise` to create the first round of stabilizer
    #  measurements in the surface code. Reference but don't use
    #  `stabilizers_with_noise`. Add first-round detectors.
    stim_string = f""
    return NotImplemented


def rounds_step(distance, rounds, p):
    datas, x_measures, z_measures, c2i = prepare_coords(distance)
    # Use `stabilizers_with_noise` to implement the `REPEAT` block of
    #  stabilizers. Include the mid-round detectors.
    stim_string = f""
    return NotImplemented


def final_step(distance, p):
    datas, x_measures, z_measures, c2i = prepare_coords(distance)
    all_measures = x_measures + z_measures
    all_qubits = datas + all_measures
    # Use `lattice_with_noise` to implement the final round of stabilizer
    #  measurements and the final data measurements. Add the last round
    #  detectors, the final data measure detectors, and the
    #  `OBSERVABLE_INCLUDE` instruction.
    stim_string = f""
    return NotImplemented


def surface_code_circuit_string(distance, rounds, p):
    string = coord_circuit(distance)
    string += initialization_step(distance, p)
    string += rounds_step(distance, rounds, p)
    string += final_step(distance, p)
    return string
