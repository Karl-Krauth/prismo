import time
from ..microfluidic import Chip

###############################
# Common flow functions
###############################

def purge_common_inlet(
    chip: Chip, 
    flow: str,
    waste: str,
    time: int = 5,
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
    time :
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
    >>> purge_common_inlet(c.chip, 'bBSA2', 'waste1', time=10, verbose=False)

    This will close the inlet1 control valve and open bBSA2 and waste1 flow
    valves for 10 seconds without printing anything out.
    """

    # Close inlet 1
    chip.inlet1 = 'closed'

    # Flow to waste for the given time
    if verbose:
        print(f"Flowing {flow} to {waste} for {time} seconds.")
    setattr(chip, flow, 'open')
    setattr(chip, waste, 'open')
    for i in range(time):
        time.sleep(1)

    if not keep_open:
        setattr(chip, flow, 'closed')
    setattr(chip, waste, 'closed')
    if verbose:
        print(f"Done flowing {flow} to {waste}.")


def purge_block_inlets(
    chip: Chip,
    time: int = 5,
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
    time :
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
    >>> purge_block_inlets(c.chip, time=10, keep_block1_open=True)
    """

    # Close inlets 1 and 2
    chip.inlet1 = 'closed'
    chip.inlet2 = 'closed'

    # Flow upper block inlets to lower (waste) inlets
    if verbose:
        print(f"Purging all block inlets for {time} seconds.")
    chip.block1 = 'open'
    chip.block2 = 'open'
    for i in range(time):
        time.sleep(1)

    if not keep_block1_open:
        if verbose:
            print("Leaving block 1 open.")
        chip.block1 = 'closed'
    chip.block2 = 'closed'
    if verbose:
        print("Done purging block inlets.")

###############################
# Patterning
###############################

def pattern_antiGFP(
    chip: Chip,
    waste: str = 'waste1',
    bBSA: str = 'bBSA2',
    NA: str = 'na3',
    antiGFP: str = 'in4',
    PBS: str = 'in5',
    outlet: str = 'out2',
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
        Which outlet to use ('out2' = common, 'out1' = block-specific.
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
    if verbose:
        print(f'Starting antiGFP patterning script for device {chip.name}.')
        print('NOTE: Passivation with BSA should already have been done.')
        mappings = {
            'waste': waste,
            'bBSA': bBSA,
            'NA': NA,
            'antiGFP': antiGFP,
            'PBS': PBS,
            'outlet': outlet,
        }
        print(f'NOTE: mappings = \n{mappings}')

    # Close all valves
    for valve in chip._mapping:
        setattr(chip, valve, 'closed')
    if verbose:
        print(f'Closed all valves for device {chip.name}')

    # Prep bBSA flow
    chip.sandR = 'open'
    chip.sandL = 'open'
    
    setattr(chip, outlet, 'open')

    setattr(chip, bBSA, 'open')
    setattr(chip, waste, 'open')

    if verbose:
        print(f'Flushing {bBSA} to {waste} for 5 sec, then closing {waste}.')
    purge_common_inlet(chip, bBSA, waste, time=5, verbose=False)

    # Flow with buttons closed
    chip.inlet1 = 'open'
    if verbose:
        print(f'Flushing {bBSA} through device with buttons closed for 5 min.')
    for i in range(5*60):
        time.sleep(1)

    # Open buttons for 35 min
    chip.butR = 'open'
    chip.butL = 'open'
    if verbose:
        print(f'Opening buttons; flowing {bBSA} for 35 min.')
    for i in range(35*60):
        time.sleep(1)

    setattr(chip, bBSA, 'closed')
    if verbose:
        print(f'Done flowing {bBSA}.')

    # Flush with PBS
    if verbose:
        print(f'Flushing PBS ({PBS}) to {waste} for 30 sec, then closing {waste}.')
    purge_common_inlet(chip, PBS, waste, time=30, verbose=False)
    chip.inlet1 = 'open'
    
    if verbose:
        print(f'Flushing PBS ({PBS}) through device with buttons open for 10 min.')
    for i in range(10*60):
        time.sleep(1)

    setattr(chip, PBS, 'closed')
    if verbose:
        print(f'Done flowing PBS ({PBS}).')

    # Neutravidin
    if verbose:
        print(f'Flushing NA ({NA}) to {waste} for 30 sec, then closing {waste}.')
    purge_common_inlet(chip, NA, waste, time=30, verbose=False)
    chip.inlet1 = 'open'

    if verbose:
        print(f'Flushing NA ({NA}) through device with buttons open for 30 min.')
    for i in range(30*60):
        time.sleep(1)

    setattr(chip, NA, 'closed')
    if verbose:
        print(f'Done flowing NA ({NA}). Flowing PBS ({PBS}) through device for 10 min.')

    # Wash with PBS
    setattr(chip, PBS, 'open')
    for i in range(10*60):
        time.sleep(1)

    setattr(chip, PBS, 'closed')
    if verbose:
        print(f'Done flowing PBS ({PBS}).')
        print(f'Flowing {bBSA} for 35 min with buttons closed to quench walls.')

    # Quench walls with bBSA
    chip.butR = 'closed'
    chip.butL = 'closed'
    setattr(chip, bBSA, 'open')
    for i in range(35*60):
        time.sleep(1)

    setattr(chip, bBSA, 'closed')
    if verbose:
        print(f'Done flowing {bBSA}. Flowing PBS ({PBS}) through device for 10 min.')

    # Wash with PBS
    setattr(chip, PBS, 'open')
    for i in range(10*60):
        time.sleep(1)

    setattr(chip, PBS, 'closed')
    if verbose:
        print(f'Done flowing PBS ({PBS}). NEXT STEP IS ANTI-GFP FLOWING.')

    # Anti-GFP flowing
    if verbose:
        print(f'Flushing antiGFP ({antiGFP}) to {waste} for 30 sec, then closing {waste}.')
    purge_common_inlet(chip, antiGFP, waste, time=30, verbose=False)
    chip.inlet1 = 'open'
    
    if verbose:
        print(f'Flowing antiGFP ({antiGFP}) through device for 30 sec.')
    for i in range(30):
        time.sleep(1)
    chip.butR = 'open'
    chip.butL = 'open'
    if verbose:
        print(f'Opened buttons. Flowing antiGFP ({antiGFP}) through device for 13.3 min.')
    for i in range(int(13.3*60)):
        time.sleep(1)
    
    if verbose:
        print(f'Flowing antiGFP ({antiGFP}) through device with buttons closed for 30 sec.')
    chip.butR = 'closed'
    chip.butL = 'closed'
    for i in range(30):
        time.sleep(1)

    if verbose:
        print(f'Done flowing antiGFP ({antiGFP}) through device. Washing with PBS.')

    # Final PBS wash
    setattr(chip, PBS, 'open')
    for i in range(10*60):
        time.sleep(1)

    if verbose:
        print(f'Done flowing PBS ({PBS}). Closing outlet.')

    # Close outlet to dead-end fill
    setattr(chip, outlet, 'closed')
    
    