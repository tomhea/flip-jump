import collections
from typing import Dict, Tuple, List

from flipjump.utils.constants import MACRO_SEPARATOR_STRING


def _prepare_first_and_second_level_significant_macros(
        child_significance_min_thresh: float, macro_code_size: Dict[str, int],
        main_thresh: float, secondary_thresh: float)\
        -> Tuple[Dict[str, int], Dict[str, Dict[str, int]]]:
    first_level = {}
    second_level = collections.defaultdict(lambda: dict())
    for k, v in macro_code_size.items():
        if MACRO_SEPARATOR_STRING not in k:
            if v < main_thresh:
                continue
            first_level[k] = v
        else:
            if v < secondary_thresh:
                continue
            k_split = k.split(MACRO_SEPARATOR_STRING)
            if len(k_split) != 2:
                continue
            parent, name = k_split
            if float(v) / macro_code_size[parent] < child_significance_min_thresh:
                continue
            second_level[parent][name] = v
    return first_level, second_level


def _clean_name_for_pie_graph(macro_name: str) -> str:
    return macro_name


def _choose_most_significant_macros(first_level: Dict[str, int], second_level: Dict[str, Dict[str, int]],
                                    secondary_thresh: float, total_code_size: int) -> List[Tuple[str, int]]:
    chosen = []
    for k, v in sorted(first_level.items(), key=lambda x: x[1], reverse=True):
        k_name = _clean_name_for_pie_graph(k)
        if len(second_level[k]) == 0:
            chosen.append((k_name, v))
        else:
            for k2, v2 in sorted(second_level[k].items(), key=lambda x: x[1], reverse=True):
                k2_name = _clean_name_for_pie_graph(k2)
                chosen.append((f"{k_name}  =>  {k2_name}", v2))
                v -= v2
            if v >= secondary_thresh:
                chosen.append((f"{k_name} others", v))
    others = total_code_size - sum([value for label, value in chosen])
    chosen.append(('all others', others))
    return chosen


def _show_macro_usage_graph(chosen_macros: List[Tuple[str, int]]) -> None:
    try:
        import plotly.graph_objects as go
    except ImportError:
        ordered_chosen_macros = sorted(chosen_macros, key=lambda name_count: name_count[1], reverse=True)
        total_ops = sum([count for name, count in chosen_macros])

        print('\n\n\nThe most used macros are:\n')
        for macro_name, ops_count in ordered_chosen_macros:
            print(f'  {macro_name}:  {ops_count:,} ops ({ops_count / total_ops:.2%})')
        print("\n\n* The statistics can be displayed in an interactive graph - "
              "that feature requires the plotly python library. *\n"
              "  Try `pip install plotly`.\n")
        return

    fig = go.Figure(data=[go.Pie(labels=[label for label, value in chosen_macros],
                                 values=[value for label, value in chosen_macros],
                                 textinfo='label+percent'
                                 )])
    fig.show()


def show_macro_usage_pie_graph(macro_code_size: Dict[str, int], total_code_size: int, *,
                               min_main_thresh: float = 0.05, min_secondary_thresh: float = 0.01,
                               child_significance_min_thresh: float = 0.1) -> None:
    """
    choose and present in a pie graph the macros with the most code-usage
    @param macro_code_size: dictionary between macro-paths and their code-size.
    @param total_code_size: total number of FlipJump ops in the program.
    @param min_main_thresh: the fraction of the program's code-usage needed for a 1st-level macro to be chosen.
    @param min_secondary_thresh: the fraction of the program's code-usage needed for a 2nd-level macro to be chosen.
    @param child_significance_min_thresh: the fraction of the 1st-level macro code-usage needed
     for its 2nd-level macro (son) needs to be chosen
    @note: if plotly isn't installed - prints those macro names and their code-usage numbers.
    """
    main_thresh = min_main_thresh * total_code_size
    secondary_thresh = min_secondary_thresh * total_code_size

    first_level, second_level = _prepare_first_and_second_level_significant_macros(
        child_significance_min_thresh, macro_code_size, main_thresh, secondary_thresh
    )

    chosen_macros = _choose_most_significant_macros(first_level, second_level, secondary_thresh, total_code_size)

    _show_macro_usage_graph(chosen_macros)
