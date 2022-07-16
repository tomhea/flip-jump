import pickle
from os import path
from pathlib import Path
from typing import Optional, List, Dict, Set

import easygui

import fjm
from defs import get_nice_label_repr


class BreakpointHandlerUnnecessary(Exception):
    pass


def display_message_box_and_get_answer(msg: str, title: str, choices: List[str]) -> str:
    # TODO deprecated warning. use another gui (tkinter? seems not so simple)
    return easygui.buttonbox(msg, title, choices)


class BreakpointHandler:
    """
    Handle breakpoints (know when breakpoints happen, query user for action).
    """
    def __init__(self, breakpoints: Dict[int, str], address_to_label: Dict[int, str]):
        self.breakpoints = breakpoints
        self.address_to_label = address_to_label

        if 0 not in self.address_to_label:
            self.address_to_label[0] = 'memory_start_0x0000'

        self.next_break = None

    def should_break(self, ip: int, op_counter: int) -> bool:
        return self.next_break == op_counter or ip in self.breakpoints

    def get_address_str(self, address: int) -> str:
        if address in self.breakpoints and self.breakpoints[address] is not None:
            label_repr = get_nice_label_repr(self.breakpoints[address], pad=4)
            return f'{hex(address)[2:]}:\n{label_repr}'
        elif address in self.address_to_label:
            label_repr = get_nice_label_repr(self.address_to_label[address], pad=4)
            return f'{hex(address)[2:]}:\n{label_repr}'
        else:
            address_before = max([a for a in self.address_to_label if a <= address])
            label_repr = get_nice_label_repr(self.address_to_label[address_before], pad=4)
            return f'{hex(address)[2:]} ({hex(address - address_before)} after:)\n{label_repr}'

    def get_message_box_body(self, ip: int, mem: fjm.Reader, op_counter: int) -> str:
        address = self.get_address_str(ip)
        flip = self.get_address_str(mem.get_word(ip))
        jump = self.get_address_str(mem.get_word(ip + mem.w))
        return f'Address {address}.\n\n{op_counter} ops executed.\n\nflip {flip}.\n\njump {jump}.'

    def query_user_for_debug_action(self, ip: int, mem: fjm.Reader, op_counter: int) -> str:
        title = "Breakpoint" if ip in self.breakpoints else "Debug Step"
        body = self.get_message_box_body(ip, mem, op_counter)
        actions = ['Single Step', 'Skip 10', 'Skip 100', 'Skip 1000', 'Continue', 'Continue All']

        action = display_message_box_and_get_answer(body, title, actions)
        if action is None:
            action = 'Continue All'
        return action

    def apply_debug_action(self, action: str, op_counter: int) -> None:
        """
        @raise BreakpointHandlerUnnecessary for the "Continue All" action
        """
        if action == 'Single Step':
            self.next_break = op_counter + 1
        elif action == 'Skip 10':
            self.next_break = op_counter + 10
        elif action == 'Skip 100':
            self.next_break = op_counter + 100
        elif action == 'Skip 1000':
            self.next_break = op_counter + 1000
        elif action == 'Continue':
            self.next_break = None
        elif action == 'Continue All':
            self.next_break = None
            raise BreakpointHandlerUnnecessary()


def handle_breakpoint(breakpoint_handler: BreakpointHandler, ip: int, mem: fjm.Reader, statistics: 'RunStatistics') \
        -> BreakpointHandler:
    """
    show debug message, query user for action, apply its action.
    @param breakpoint_handler: the breakpoint handler
    @param ip: current ip
    @param mem: the memory
    @param statistics: the statistics of the current run
    @return: the breakpoint handler (or None if it is not necessary anymore)
    """
    print('  program break', end="", flush=True)
    with statistics.pause_timer:
        action = breakpoint_handler.query_user_for_debug_action(ip, mem, statistics.op_counter)
    print(f': {action}')

    try:
        breakpoint_handler.apply_debug_action(action, statistics.op_counter)
    except BreakpointHandlerUnnecessary:
        breakpoint_handler = None

    return breakpoint_handler


def get_breakpoints(breakpoint_addresses: Optional[Set[int]],
                    breakpoint_labels: Optional[Set[str]],
                    breakpoint_contains_labels: Optional[Set[str]],
                    label_to_address: Dict[str, int])\
        -> Dict[int, str]:
    """
    generate the breakpoints' dictionary
    """
    breakpoints = {}

    update_breakpoints_from_addresses_set(breakpoint_addresses, breakpoints)
    update_breakpoints_from_breakpoint_contains_set(breakpoint_contains_labels, breakpoints, label_to_address)
    update_breakpoints_from_breakpoint_set(breakpoint_labels, breakpoints, label_to_address)

    return breakpoints


def update_breakpoints_from_breakpoint_set(breakpoint_labels: Optional[Set[str]],
                                           breakpoints: Dict[int, Optional[str]],
                                           label_to_address: Dict[str, int]) -> None:
    """
    add breakpoints from breakpoint_labels.
    @param breakpoints[in,out] - adds breakpoints to it
    """
    if breakpoint_labels:
        for bl in breakpoint_labels:
            if bl not in label_to_address:
                print(f"Warning:  Breakpoint label {bl} can't be found!")
            else:
                address = label_to_address[bl]
                breakpoints[address] = bl


def update_breakpoints_from_breakpoint_contains_set(breakpoint_contains_labels: Optional[Set[str]],
                                                    breakpoints: Dict[int, Optional[str]],
                                                    label_to_address: Dict[str, int]) -> None:
    """
    add breakpoints generated with breakpoint_contains_labels.
    @param breakpoints[in,out] - adds breakpoints to it
    """
    # TODO improve the speed of this part with suffix trees
    if breakpoint_contains_labels:
        for bcl in breakpoint_contains_labels:
            for label in label_to_address:
                if bcl in label:
                    address = label_to_address[label]
                    breakpoints[address] = label


def update_breakpoints_from_addresses_set(breakpoint_addresses: Optional[Set[int]],
                                          breakpoints: Dict[int, Optional[str]]) -> None:
    """
    add breakpoints of addresses breakpoint_addresses.
    @param breakpoints[in,out] - adds breakpoints to it
    """
    if breakpoint_addresses:
        for address in breakpoint_addresses:
            breakpoints[address] = None


def load_labels_dictionary(debugging_file: Path, labels_file_needed: bool) -> Dict[str, int]:
    """
    load the labels_dictionary from debugging_file, if possible.
    """
    label_to_address = []
    if debugging_file is not None:
        if path.isfile(debugging_file):
            with open(debugging_file, 'rb') as f:
                label_to_address = pickle.load(f)
        else:
            print(f"Warning:  debugging file {debugging_file} can't be found!")
    elif labels_file_needed:
        print(f"Warning:  debugging labels can't be found! no debugging file specified.")
    return label_to_address


def get_breakpoint_handler(debugging_file: Path, breakpoint_addresses: Set[int], breakpoint_labels: Set[str],
                           breakpoint_contains_labels: Set[str]) -> Optional[BreakpointHandler]:
    """
    generate the breakpoint handler from the debugging file and the breakpoint sets.
    @param debugging_file: the debug file path (created at assemble time)
    @param breakpoint_addresses: set of addresses to break at
    @param breakpoint_labels: set of labels to break at
    @param breakpoint_contains_labels: set of strings, to break at every label that contains one of them
    @return: the breakpoint handler
    """
    labels_file_needed = any((breakpoint_addresses, breakpoint_contains_labels))
    label_to_address = load_labels_dictionary(debugging_file, labels_file_needed)

    address_to_label = {label_to_address[label]: label for label in label_to_address}
    breakpoints = get_breakpoints(breakpoint_addresses, breakpoint_labels, breakpoint_contains_labels, label_to_address)

    return BreakpointHandler(breakpoints, address_to_label) if breakpoints else None
