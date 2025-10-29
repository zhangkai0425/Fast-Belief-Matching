import numpy as np
import stim


ID = 'ID'
CX = 'CX'
PX = 'PX'
PZ = 'PZ'
MX = 'MX'
MZ = 'MZ'

def add_noise(circuit, p_gates, qubits=None, occupied_qubits=None):
    assert p_gates[MZ] == p_gates[MX]
    assert p_gates[PZ] == p_gates[PX]

    circuit_new = stim.Circuit()
    if qubits is None:
        qubits = circuit.get_final_qubit_coordinates().keys()
    if occupied_qubits is None:
        occupied_qubits = set()

    for inst in circuit:
        if inst.name == 'REPEAT':
            circuit_new.append(stim.CircuitRepeatBlock(inst.repeat_count, add_noise(
                inst.body_copy(), p_gates, qubits, occupied_qubits)))
        else:
            targets = inst.targets_copy()
            if inst.name in ['R', 'M', 'MR', 'CX']:
                occupied_qubits.update(
                    target.qubit_value for target in targets)
                if inst.name in ['M', 'MR']:
                    circuit_new.append(stim.CircuitInstruction('X_ERROR', targets, [p_gates[MZ]]))  # TODO: differentiate MZ and MX
                    if inst.name == 'MR':
                        occupied_qubits.add(-1)  # Double-length tick
            elif inst.name == 'TICK':
                if occupied_qubits:
                    idle_targets = [stim.GateTarget(i) for i in qubits if i not in occupied_qubits]
                    if idle_targets:
                        if -1 in occupied_qubits:  # MR happened in this tick
                            idle_targets += idle_targets
                        circuit_new.append(stim.CircuitInstruction('DEPOLARIZE1', idle_targets, [p_gates[ID]]))
                occupied_qubits = set()
            circuit_new.append(inst)
            if inst.name in ['R', 'MR']:
                circuit_new.append(stim.CircuitInstruction('X_ERROR', targets, [p_gates[PZ]]))  # TODO: differentiate PZ and PX
            elif inst.name == 'CX':
                circuit_new.append(stim.CircuitInstruction('DEPOLARIZE2', targets, [p_gates[CX]]))

    return circuit_new


def surface_code_circuit(d, num_layer, p_surface=0.001):
    p_gates = {
        ID: p_surface,
        CX: p_surface,
        PX: p_surface,
        PZ: p_surface,
        MX: p_surface,
        MZ: p_surface
    }

    circuit = stim.Circuit.generated("surface_code:rotated_memory_z",
                                     distance=d,
                                     rounds=num_layer)

    assert circuit[-1] == stim.CircuitInstruction('OBSERVABLE_INCLUDE', [stim.target_rec(-(d - 1) * d - j - 1) for j in range(d)], [0])
    circuit = circuit[:-1]
    circuit.append(stim.CircuitInstruction('OBSERVABLE_INCLUDE', [stim.target_rec(-j - 1) for j in range(d)], [0]))

    return add_noise(circuit, p_gates)


def get_transformed_coordinates(circuit):
    d = len(circuit[-1].targets_copy())
    return {k: ((2 * d - int(y)) // 2, int(x) // 2, int(z)) for k, (x, y, z) in circuit.get_detector_coordinates().items()}