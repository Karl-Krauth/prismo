from pprint import pp

from ..microfluidic import Chip
from .general import _check_valve_mapping, _timestamp, sleep

###############################
# Common flow functions
###############################

# Hard-coded valve names
_hard_coded = [
    "inlet1",
    "inlet2",
    "sandR",
    "sandL",
    "butR",
    "butL",
    "out1",
    "out2",
    "block1",
    "block2",
    "neck",
]


def safe_state(
    chip: Chip,
) -> None:
    """Closes all valves.
    Parameters:
    -----------
    chip :
        The prismo.devices.microfluidic.Chip object for 4-block device.
    """
    for valve in _hard_coded:
        try:
            _check_valve_mapping(chip, valve)
        except ValueError:
            raise ValueError(
                f"Incorrect valve name {valve} in mapping.Must be one of {_hard_coded}."
            )
    # Close all valves
    for valve in chip._mapping:
        chip[valve] = "closed"


def deadend_fill(
    chip: Chip,
    buffer: str,
) -> None:
    """Sets device to dead-end fill.
    Parameters:
    -----------
    chip :
        The prismo.devices.microfluidic.Chip object for 4-block device.
    buffer :
        Name of buffer line.
    """
    _check_valve_mapping(chip, buffer)
    for valve in _hard_coded:
        try:
            _check_valve_mapping(chip, valve)
        except ValueError:
            raise ValueError(
                f"Incorrect valve name {valve} in mapping.Must be one of {_hard_coded}."
            )

    # Close all valves except buffer, inlets, and sandwiches
    closed = ["butR", "butL", "out1", "out2", "block1", "block2"]
    for valve in closed:
        chip[valve] = "closed"

    # Dead-end fill from buffer through chambers
    opened = [buffer, "inlet1", "inlet2", "sandR", "sandL"]
    for valve in opened:
        chip[valve] = "open"


def purge_common_inlet(
    chip: Chip,
    flow: str,
    waste: str,
    wait_time: int = 5,
    keep_flow_open: bool = True,
    verbose: bool = True,
) -> None:
    """Purges air from a common inlet for a set amount of time.

    Expects that flow and waste inlet valves are in the common valve
    location (i.e., common inlet flow valves 1–5).

    Parameters:
    -----------
    chip :
        The prismo.devices.microfluidic.Chip object for 4-block device.
    flow :
        The name of the inlet being purged.
    waste :
        The name of the waste inlet to purge to.
    wait_time :
        Number of seconds to purge `flow`.
    keep_flow_open :
        Wether to keep the flow valve open.
    verbose :
        Whether to print each step.

    Returns:
    --------
    None :
        This function controls flow on a 4-block device; nothing is
        returned.

    Notes:
    ------
    Inlet1 always stays closed at the end of this function.

    Examples:
    ---------
    >>> purge_common_inlet(c.chip, "bBSA2", "waste1", wait_time=10, verbose=False)

    This will close the inlet1 control valve and open bBSA2 and waste1 flow
    valves for 10 seconds without printing anything out.
    """
    _check_valve_mapping(chip, flow)
    _check_valve_mapping(chip, waste)
    for valve in _hard_coded:
        try:
            _check_valve_mapping(chip, valve)
        except ValueError:
            raise ValueError(
                f"Incorrect valve name {valve} in mapping.Must be one of {_hard_coded}."
            )

    # Close inlet 1
    chip.inlet1 = "closed"

    # Flow to waste for the given time
    if verbose:
        print(f"Flowing {flow} to {waste} for {wait_time} seconds.")
    chip[flow] = "open"
    chip[waste] = "open"
    sleep(wait_time)

    if not keep_flow_open:
        chip[flow] = "closed"
    chip[waste] = "closed"
    if verbose:
        print(f"Done flowing {flow} to {waste}.")


def purge_block_inlets(
    chip: Chip,
    wait_time: int = 5,
    keep_block1_open: bool = False,
    verbose: bool = True,
) -> None:
    """Purges all four block-specific inlets for a set amount of time.

    Expects that block inlets contain low-pressure lines to flow to the
    adjacent block outlets, between block1 and block2 control lines.

    Parameters:
    -----------
    chip :
        The prismo.devices.microfluidic.Chip object for 4-block device.
    wait_time :
        Number of seconds to purge `flow`.
    keep_block1_open :
        Whether to keep the block1 control valve open. (Dead-end fill.)
    verbose :
        Whether to print each step.

    Returns:
    --------
    None :
        This function controls flow on a 4-block device; nothing is
        returned.

    Notes:
    ------
    None.

    Examples:
    ---------
    >>> purge_block_inlets(c.chip, wait_time=10, keep_block1_open=True)
    """
    for valve in _hard_coded:
        try:
            _check_valve_mapping(chip, valve)
        except ValueError:
            raise ValueError(
                f"Incorrect valve name {valve} in mapping.Must be one of {_hard_coded}."
            )
    # Close inlets 1 and 2
    chip.inlet1 = "closed"
    chip.inlet2 = "closed"

    # Flow upper block inlets to lower (waste) inlets
    if verbose:
        print(f"Purging all block inlets for {wait_time} seconds.")
    chip.block1 = "open"
    chip.block2 = "open"
    sleep(wait_time)

    if not keep_block1_open:
        if verbose:
            print("Leaving block 1 open.")
        chip.block1 = "closed"
    chip.block2 = "closed"
    if verbose:
        print("Done purging block inlets.")


###############################
# Patterning
###############################


def pattern_antiGFP(
    chip: Chip,
    waste: str = "waste1",
    bBSA: str = "bBSA2",
    NA: str = "na3",
    antiGFP: str = "in4",
    PBS: str = "in5",
    outlet: str = "out2",
    verbose: bool = True,
) -> None:
    """Patterns a 4-block device to add a bBSA-NA-antiGFP pedestal
    under the button.

    Parameters:
    -----------
    chip :
        The prismo.devices.microfluidic.Chip object for 4-block device.
    waste :
        The waste valve for purging air from other inlets.
    bBSA :
        Inlet containing bBSA.
    NA :
        Inlet containing NA.
    antiGFP :
        Inlet containing antiGFP.
    PBS :
        Inlet containing PBS.
    outlet :
        Which outlet to use ('out2' = common, 'out1' = block-specific).
    verbose :
        Whether to print each step.

    Returns:
    --------
    None :
        This function runs patterning for a 4-block device; nothing is
        returned.

    Notes:
    ------
    None.

    Examples:
    ---------
    >>> pattern_antiGFP(c.chip)
    """
    # Check valve mappings for the non-hard-coded valves
    valve_args = [waste, bBSA, NA, antiGFP, PBS, outlet]
    for valve in valve_args:
        _check_valve_mapping(chip, valve)

    for valve in _hard_coded:
        try:
            _check_valve_mapping(chip, valve)
        except ValueError:
            raise ValueError(
                f"Incorrect valve name {valve} in mapping.Must be one of {_hard_coded}."
            )

    if verbose:
        print(f">>> Patterning - {_timestamp()}")
        print(f"Starting antiGFP patterning script for device {chip.name}.")
        print("NOTE: Passivation with BSA should already have been done.")
        print("Valve mappings:")
        pp(
            {
                "waste": waste,
                "bBSA": bBSA,
                "NA": NA,
                "antiGFP": antiGFP,
                "PBS": PBS,
                "outlet": outlet,
            }
        )

    # Close all valves
    for valve in chip._mapping:
        chip[valve] = "closed"
    if verbose:
        print(f"Closed all valves for device {chip.name}")

    # Prep device flow state; need sandR, sandL, inlet2, and outlet open
    chip.sandR = "open"
    chip.sandL = "open"
    chip.inlet2 = "open"
    chip[outlet] = "open"

    # Flow with buttons closed
    if verbose:
        print(f">>> Step 1: bBSA flow - {_timestamp()}")
        print(f"Flushing {bBSA} to {waste} for 5 sec, then closing {waste}.")

    purge_common_inlet(chip, bBSA, waste, wait_time=5, verbose=False)
    chip.inlet1 = "open"

    if verbose:
        print(f"Flushing {bBSA} through device with buttons closed for 5 min.")
    sleep(5 * 60)

    # Open buttons for 35 min
    chip.butR = "open"
    chip.butL = "open"
    if verbose:
        print(f"Opening buttons; flowing {bBSA} for 35 min.")
    sleep(35 * 60)

    chip[bBSA] = "closed"
    if verbose:
        print(f"Done flowing {bBSA}.")

    # Flush with PBS
    if verbose:
        print(f"Flushing PBS ({PBS}) to {waste} for 30 sec, then closing {waste}.")
    purge_common_inlet(chip, PBS, waste, wait_time=30, verbose=False)
    chip.inlet1 = "open"

    if verbose:
        print(f"Flushing PBS ({PBS}) through device with buttons open for 10 min.")
    sleep(10 * 60)

    chip[PBS] = "closed"
    if verbose:
        print(f"Done flowing PBS ({PBS}).")

    # Neutravidin
    if verbose:
        print(f">>> Step 2: Neutravidin flow - {_timestamp()}")
        print(f"Flushing NA ({NA}) to {waste} for 30 sec, then closing {waste}.")
    purge_common_inlet(chip, NA, waste, wait_time=30, verbose=False)
    chip.inlet1 = "open"

    if verbose:
        print(f"Flushing NA ({NA}) through device with buttons open for 30 min.")
    sleep(30 * 60)

    chip[NA] = "closed"
    if verbose:
        print(f"Done flowing NA ({NA}). Flowing PBS ({PBS}) through device for 10 min.")

    # Wash with PBS
    chip[PBS] = "open"
    sleep(10 * 60)

    chip[PBS] = "closed"
    if verbose:
        print(f"Done flowing PBS ({PBS}).")

    # Quench walls with bBSA
    if verbose:
        print(f">>> Step 3: bBSA quench - {_timestamp()}")
        print(f"Flowing {bBSA} for 35 min with buttons closed to quench walls.")
    chip.butR = "closed"
    chip.butL = "closed"
    chip[bBSA] = "open"
    sleep(35 * 60)

    chip[bBSA] = "closed"
    if verbose:
        print(f"Done flowing {bBSA}. Flowing PBS ({PBS}) through device for 10 min.")

    # Wash with PBS
    chip[PBS] = "open"
    sleep(10 * 60)

    chip[PBS] = "closed"
    if verbose:
        print(f"Done flowing PBS ({PBS}).")

    # Anti-GFP flowing
    if verbose:
        print(f">>> Step 4: antiGFP flow - {_timestamp()}")
        print(f"Flushing antiGFP ({antiGFP}) to {waste} for 30 sec, then closing {waste}.")
    purge_common_inlet(chip, antiGFP, waste, wait_time=30, verbose=False)
    chip.inlet1 = "open"

    if verbose:
        print(f"Flowing antiGFP ({antiGFP}) through device for 30 sec.")
    sleep(30)
    chip.butR = "open"
    chip.butL = "open"
    if verbose:
        print(f"Opened buttons. Flowing antiGFP ({antiGFP}) through device for 13.3 min.")
    sleep(int(13.3 * 60))

    if verbose:
        print(f"Flowing antiGFP ({antiGFP}) through device with buttons closed for 30 sec.")
    chip.butR = "closed"
    chip.butL = "closed"
    sleep(30)

    chip[antiGFP] = "closed"
    if verbose:
        print(f"Done flowing antiGFP ({antiGFP}) through device. Washing with PBS ({PBS}).")

    # Final PBS wash
    chip[PBS] = "open"
    sleep(10 * 60)

    if verbose:
        print(f"Done flowing PBS ({PBS}). Closing outlet.")

    # Close outlet to dead-end fill
    chip[outlet] = "closed"

    if verbose:
        print(f">>> Done with patterning - {_timestamp()}")


###############################
# SDS Wash
###############################


def SDS_wash(
    chip: Chip,
    waste: str = "waste1",
    SDS: str = "bBSA2",
    PBS: str = "in5",
    outlet: str = "out2",
    wash_lagoons: bool = True,
    final_neck_state: str = "closed",
    verbose: bool = True,
) -> None:
    """Washes chip with SDS one time. To be used within a loop to repeat
    wash multiple times and acquire images after each wash.

    Parameters:
    -----------
    chip :
        The prismo.devices.microfluidic.Chip object for 4-block device.
    waste :
        The waste valve for purging air from other inlets.
    SDS :
        Inlet containing SDS.
    PBS :
        Inlet containing wash PBS.
    outlet :
        Which outlet to use ('out2' = common, 'out1' = block-specific).
    wash_lagoons :
        Whether to wash with necks open or closed. Default open.
    final_neck_state :
        How to leave necks, "open" or "closed". Default "closed".
    verbose :
        Whether to print each step.

    Returns:
    --------
    None :
        This function SDS-washes a 4-block device; nothing is returned.

    Notes:
    ------
    None.

    Examples:
    ---------
    >>> SDS_wash(c.chip)
    """
    # Check valve mappings for the non-hard-coded valves
    valve_args = [waste, SDS, PBS, outlet]
    for valve in valve_args:
        _check_valve_mapping(chip, valve)

    for valve in _hard_coded:
        try:
            _check_valve_mapping(chip, valve)
        except ValueError:
            raise ValueError(
                f"Incorrect valve name {valve} in mapping.Must be one of {_hard_coded}."
            )

    if final_neck_state not in ("open", "closed"):
        raise ValueError('final_neck_state takes only "open" or "closed" as argument.')

    if verbose:
        print(f">>> SDS Wash - {_timestamp()}")
        print("Valve mappings:")
        pp(
            {
                "waste": waste,
                "SDS": SDS,
                "PBS": PBS,
                "outlet": outlet,
            }
        )

        # Set dead-end fill flow state
        deadend_fill(chip, buffer=PBS)
        chip[PBS] = "closed"

        # Flow SDS over device for 5 min
        if wash_lagoons:
            chip.neck = "open"
        else:
            chip.neck = "closed"

        purge_common_inlet(chip, SDS, waste, verbose=False)
        chip.inlet1 = "open"
        chip[outlet] = "open"

        sleep(5 * 60)

        chip[SDS] = "closed"
        chip[outlet] = "closed"

        # Wash with PBS for 10 min
        if verbose:
            print(f">>> Washing with PBS - {_timestamp()}")
        purge_common_inlet(chip, PBS, waste, verbose=False)
        chip.inlet1 = "open"
        chip[outlet] = "open"

        sleep(10 * 60)

        chip[outlet] = "closed"

        chip.neck = final_neck_state
