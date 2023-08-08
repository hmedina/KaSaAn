#! /usr/bin/env python3
"""
Render a contact map.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.text as mpt
import matplotlib.widgets as mpw
import warnings
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from typing import Tuple
from KaSaAn.core import KappaContactMap
from KaSaAn.core.KappaContactMap import valid_graph_layouts


def main():
    """Plot a contact map taken from a witness file, e.g. `inputs.ka`"""

    w: int = max([len(key) for key in valid_graph_layouts.keys()])    # key width, for prettier printing
    layout_expl: str = '\n'.join(['{:<{width}}\t{}'.format(n, v.__doc__.split('\n')[0], width=w)
                                  for n, v in valid_graph_layouts.items()])

    parser = ArgumentParser(description=main.__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-i', '--input_file_name', type=str, default='inputs.ka',
                        help='Name of the file containing the contact map, written in kappa by the Kappa Static'
                        ' Analyzer (KaSA). By default, will search for `inputs.ka`, aka the "witness file".')
    # ToDo
    # parser.add_argument('-cs', '--coloring_scheme', type=str, default='',
    #                     help='Name of the file containing a coloring scheme for drawing the faces of the wedges that'
    #                     ' represent the agents.')
    parser.add_argument('-fs', '--fig_size', type=float, default=mpl.rcParams['figure.figsize'], nargs=2,
                        help='Size of the resulting figure, in inches, specified as two elements, width and height'
                        ' (text size is specified in points, so this affects the size of text relative to other'
                        ' graph elements).')
    parser.add_argument('-o', '--output_file_name', type=Path, default=None,
                        help='Name of the file to where the figure should be saved; displayed if not specified.')
    parser.add_argument('-m', '--method', type=str, choices=list(valid_graph_layouts.keys()), default='',
                        help='Interpret contact map as a plain graph and layout using one of these:\n' + layout_expl)
    parser.add_argument('--summarize_flagpole', action='store_true',
                        help='If passed, summarizes state-only sites as a numeric annotation on a special wedge'
                        ' (the flagpole). Otherwise, these sites and their states are listed in said flagpole.')
    parser.add_argument('--keep_axes_ticks', action='store_true',
                        help='If given, will keep the X & Y axes ticks; use this to estimate coordinates and offsets'
                        ' for manual agent placement.')
    parser.add_argument('-ts', '--text_size', type=int,
                        help="If given, set point size for all text elements, overriding MatPlotLib's default.")
    args = parser.parse_args()

    if args.text_size:
        mpl.rcParams['font.size'] = args.text_size

    this_cm = KappaContactMap(args.input_file_name)
    fig, ax = plt.subplots(figsize=args.fig_size, layout='constrained')

    if args.method != '':
        this_cm.layout_from_graph(args.method)
    this_cm.draw(ax, draw_state_flagpole=(not args.summarize_flagpole))

    if not args.keep_axes_ticks:
        ax.axis('off')

    if args.output_file_name:
        if not args.output_file_name.parent.exists():
            args.output_file_name.parent.mkdir(parents=True)
        fig.savefig(args.output_file_name)
    else:
        def re_coord(child_space, parent_space) -> Tuple[int, int, int, int]:
            """Convenience function to adjust a child space by a parent's and yield global rectangle parameters
             of left, bottom, width, and height."""
            ch_left, ch_bottom, ch_width, ch_height = child_space
            pr_left, pr_bottom, pr_width, pr_height = parent_space
            new_left = pr_left + ch_left * pr_width
            new_bottom = pr_bottom + ch_bottom * pr_height
            new_width = pr_width * ch_width
            new_height = pr_height * ch_height
            return (new_left, new_bottom, new_width, new_height)

        # adjust figure size to accomodate axis that holds controls
        fig.set_figheight(args.fig_size[0] * 1.2)
        fig.subplots_adjust(bottom=0.2)

        # initialize to a sane default plot, notably for swapping; some maps may not be capable of
        # having sites swapped at all
        agent_names = this_cm.get_agent_names()
        default_agent = ''
        swapping_enabled = True
        for some_agent in agent_names:
            if len(this_cm.get_binding_site_names_of(some_agent)) >= 2:
                default_agent = some_agent
                break
        if default_agent == '':
            swapping_enabled = False

        # main area layout & sizes
        controls_coords = [0.0, 0.0, 1.0, 1/5]      # left, bottom, width, height
        v_p = 0.05                                  # vertical padding
        h_p = 0.01                                  # horizontal padding
        agent_name_coords = re_coord([0.0 + h_p, 0.7 + v_p, 0.6 - 2 * h_p, 0.3 - 2 * v_p], controls_coords)
        move_opers_coords = re_coord([0.0 + h_p, 0.2 + v_p, 0.4 - 2 * h_p, 0.5 - 2 * v_p], controls_coords)
        rota_opers_coords = re_coord([0.4 + h_p, 0.2 + v_p, 0.2 - 2 * h_p, 0.5 - 2 * v_p], controls_coords)
        swap_opers_coords = re_coord([0.6 + h_p, 0.2 + v_p, 0.4 - 2 * h_p, 0.8 - 2 * v_p], controls_coords)
        figu_opers_coords = re_coord([0.0 + h_p, 0.0 + v_p, 1.0 - 2 * h_p, 0.2 - 2 * v_p], controls_coords)

        # text box to display agent name, next/prev arrows
        ax_agent_name_prev = fig.add_axes(re_coord([0.0, 0.0, 0.1, 0.5], agent_name_coords))
        ax_agent_name_next = fig.add_axes(re_coord([0.0, 0.5, 0.1, 0.5], agent_name_coords))
        ax_agent_name_text = fig.add_axes(re_coord([0.1, 0.0, 0.9, 1.0], agent_name_coords))
        t_agent_text: mpt.Text = ax_agent_name_text.text(x=0.05, y=0.5, s=default_agent, va='center_baseline',
                                                         fontsize='xx-large')
        ax_agent_name_text.set_xticks([])
        ax_agent_name_text.set_yticks([])
        button_agent_next = mpw.Button(ax_agent_name_next, '>')
        button_agent_prev = mpw.Button(ax_agent_name_prev, '<')

        class AgentNameCycler:
            def next(self, event):
                nonlocal site_list
                nonlocal swapping_enabled
                ix = agent_names.index(t_agent_text.get_text())
                if ix == len(agent_names) - 1:
                    i_next = 0
                else:
                    i_next = ix + 1
                t_agent_text.set_text(agent_names[i_next])
                site_list = this_cm.get_binding_site_names_of(t_agent_text.get_text())
                if len(site_list) >= 2:
                    swapping_enabled = True
                    t_site1_text.set_text(site_list[0])
                    t_site2_text.set_text(site_list[1])
                plt.draw()

            def prev(self, event):
                nonlocal site_list
                nonlocal swapping_enabled
                ix = agent_names.index(t_agent_text.get_text())
                if ix == 0:
                    i_prev = len(agent_names) - 1
                else:
                    i_prev = ix - 1
                t_agent_text.set_text(agent_names[i_prev])
                site_list = this_cm.get_binding_site_names_of(t_agent_text.get_text())
                if len(site_list) >= 2:
                    swapping_enabled = True
                    t_site1_text.set_text(site_list[0])
                    t_site2_text.set_text(site_list[1])
                plt.draw()

        agent_name_callback = AgentNameCycler()
        button_agent_next.on_clicked(agent_name_callback.next)
        button_agent_prev.on_clicked(agent_name_callback.prev)

        # move operations
        ax_move_radios = fig.add_axes(re_coord([0.0, 0.0, 0.5, 0.5], move_opers_coords))
        ax_move_button = fig.add_axes(re_coord([0.5, 0.0, 0.5, 0.5], move_opers_coords))
        ax_move_x_labl = fig.add_axes(re_coord([0.0, 0.5, 0.1, 0.5], move_opers_coords))
        ax_move_x_inpt = fig.add_axes(re_coord([0.1, 0.5, 0.4, 0.5], move_opers_coords))
        ax_move_y_labl = fig.add_axes(re_coord([0.5, 0.5, 0.1, 0.5], move_opers_coords))
        ax_move_y_inpt = fig.add_axes(re_coord([0.6, 0.5, 0.4, 0.5], move_opers_coords))

        ax_move_x_labl.text(x=0.5, y=0.5, s='X', va='center_baseline', ha='center', fontsize='xx-large')
        ax_move_y_labl.text(x=0.5, y=0.5, s='Y', va='center_baseline', ha='center', fontsize='xx-large')
        ax_move_x_labl.set_xticks([])
        ax_move_x_labl.set_yticks([])
        ax_move_y_labl.set_xticks([])
        ax_move_y_labl.set_yticks([])
        text_box_move_x = mpw.TextBox(ax_move_x_inpt, label='', textalignment='left')
        text_box_move_y = mpw.TextBox(ax_move_y_inpt, label='', textalignment='left')

        move_x_val = 0.0
        move_y_val = 0.0

        # sanitize textbox input to keep only floats
        def move_submit_x(expression):
            nonlocal move_x_val
            try:
                move_x_val = float(expression)
            except ValueError:
                move_x_val = 0.0
            text_box_move_x.set_val(move_x_val)

        def move_submit_y(expression):
            nonlocal move_y_val
            try:
                move_y_val = float(expression)
            except ValueError:
                move_y_val = 0.0
            text_box_move_y.set_val(move_y_val)

        text_box_move_x.on_submit(move_submit_x)
        text_box_move_y.on_submit(move_submit_y)

        radio_butt_move = mpw.RadioButtons(ax_move_radios, ['To', 'By'], active=1,
                                           label_props={'fontsize': ['xx-large', 'xx-large']})

        button_move_act = mpw.Button(ax_move_button, 'Move', color='#FFDCDC')
        button_move_act.label.set_fontsize('xx-large')

        def move_action(event):
            if radio_butt_move.value_selected == 'To':
                this_cm.move_agent_to(agent_name=t_agent_text.get_text(), new_x=move_x_val, new_y=move_y_val)
            elif radio_butt_move.value_selected == 'By':
                this_cm.move_agent_by(agent_name=t_agent_text.get_text(), delta_x=move_x_val, delta_y=move_y_val)
            ax.clear()
            this_cm.draw(ax, draw_state_flagpole=(not args.summarize_flagpole))
            plt.draw()

        button_move_act.on_clicked(move_action)

        # rotate operations
        rotate_val = 0.0

        ax_rota_button = fig.add_axes(re_coord([0.0, 0.0, 1.0, 0.5], rota_opers_coords))
        ax_rota_inputs = fig.add_axes(re_coord([0.0, 0.5, 1.0, 0.5], rota_opers_coords))
        t_agent_rota = mpw.TextBox(ax_rota_inputs, label='', textalignment='left')

        def rota_submit(expression):
            nonlocal rotate_val
            try:
                rotate_val = float(expression)
            except ValueError:
                rotate_val = 0.0
            t_agent_rota.set_val(rotate_val)

        t_agent_rota.on_submit(rota_submit)

        b_agent_rota = mpw.Button(ax_rota_button, 'Rotate', color='#DCFFDC')
        b_agent_rota.label.set_fontsize('xx-large')

        def rotate_action(event):
            this_cm.rotate_all_sites_of(agent_name=t_agent_text.get_text(), degrees=rotate_val)
            ax.clear()
            this_cm.draw(ax, draw_state_flagpole=(not args.summarize_flagpole))
            plt.draw()

        b_agent_rota.on_clicked(rotate_action)

        # swap operations
        site_list = this_cm.get_binding_site_names_of(default_agent)
        if len(site_list) >= 2:
            swapping_enabled = True

        ax_swap_button = fig.add_axes(re_coord([0.0, 0.0, 1.0, 1/3], swap_opers_coords))

        ax_swap_s1_prev = fig.add_axes(re_coord([0.0, 4/6, 0.1, 1/6], swap_opers_coords))
        ax_swap_s1_next = fig.add_axes(re_coord([0.0, 5/6, 0.1, 1/6], swap_opers_coords))
        ax_swap_s1_text = fig.add_axes(re_coord([0.1, 2/3, 0.9, 1/3], swap_opers_coords))

        ax_swap_s2_prev = fig.add_axes(re_coord([0.0, 2/6, 0.1, 1/6], swap_opers_coords))
        ax_swap_s2_next = fig.add_axes(re_coord([0.0, 3/6, 0.1, 1/6], swap_opers_coords))
        ax_swap_s2_text = fig.add_axes(re_coord([0.1, 1/3, 0.9, 1/3], swap_opers_coords))

        t_site1_text: mpt.Text = ax_swap_s1_text.text(x=0.05, y=0.5, va='center_baseline', fontsize='xx-large',
                                                      s=site_list[0] if swapping_enabled else '')
        t_site2_text: mpt.Text = ax_swap_s2_text.text(x=0.05, y=0.5, va='center_baseline', fontsize='xx-large',
                                                      s=site_list[1] if swapping_enabled else '')
        ax_swap_s1_text.set_xticks([])
        ax_swap_s1_text.set_yticks([])
        ax_swap_s2_text.set_xticks([])
        ax_swap_s2_text.set_yticks([])

        button_site1_next = mpw.Button(ax_swap_s1_next, '>')
        button_site1_prev = mpw.Button(ax_swap_s1_prev, '<')
        button_site2_next = mpw.Button(ax_swap_s2_next, '>')
        button_site2_prev = mpw.Button(ax_swap_s2_prev, '<')

        class Site1Cycler:
            def next(self, event):
                ix = site_list.index(t_site1_text.get_text())
                if ix == len(site_list) - 1:
                    i_next = 0
                else:
                    i_next = ix + 1
                t_site1_text.set_text(site_list[i_next])
                plt.draw()

            def prev(self, event):
                ix = site_list.index(t_site1_text.get_text())
                if ix == 0:
                    i_prev = len(site_list) - 1
                else:
                    i_prev = ix - 1
                t_site1_text.set_text(site_list[i_prev])
                plt.draw()

        class Site2Cycler:
            def next(self, event):
                ix = site_list.index(t_site2_text.get_text())
                if ix == len(site_list) - 1:
                    i_next = 0
                else:
                    i_next = ix + 1
                t_site2_text.set_text(site_list[i_next])
                plt.draw()

            def prev(self, event):
                ix = site_list.index(t_site2_text.get_text())
                if ix == 0:
                    i_prev = len(site_list) - 1
                else:
                    i_prev = ix - 1
                t_site2_text.set_text(site_list[i_prev])
                plt.draw()

        site1_callback = Site1Cycler()
        site2_callback = Site2Cycler()
        button_site1_next.on_clicked(site1_callback.next)
        button_site1_prev.on_clicked(site1_callback.prev)
        button_site2_next.on_clicked(site2_callback.next)
        button_site2_prev.on_clicked(site2_callback.prev)

        button_swap_act = mpw.Button(ax_swap_button, 'Swap', color='#DCDCFF')
        button_swap_act.label.set_fontsize('xx-large')

        def swap_action(event):
            if t_site1_text.get_text() != t_site2_text.get_text():
                this_cm.swap_sites_of(agent_name=t_agent_text.get_text(),
                                      site_1=t_site1_text.get_text(),
                                      site_2=t_site2_text.get_text())
                ax.clear()
                this_cm.draw(ax, draw_state_flagpole=(not args.summarize_flagpole))
                plt.draw()
            else:
                warnings.warn('Request to swap site {} against itself was ignored.'.format(t_site1_text.get_text()))

        button_swap_act.on_clicked(swap_action)

        # figure operations
        ax_figure_axes_draw = fig.add_axes(re_coord([0.0, 0.0, 1/3, 1.0], figu_opers_coords))
        ax_figure_grid_draw = fig.add_axes(re_coord([1/3, 0.0, 1/3, 1.0], figu_opers_coords))
        ax_figure_hide_axes = fig.add_axes(re_coord([2/3, 0.0, 1/3, 1.0], figu_opers_coords))
        button_axes_draw = mpw.Button(ax_figure_axes_draw, 'Draw Axes')
        button_grid_draw = mpw.Button(ax_figure_grid_draw, 'Draw Grid')
        button_axes_hide = mpw.Button(ax_figure_hide_axes, 'Hide Axes & Grid')

        def action_axes_draw(event):
            ax.axis('on')
            plt.draw()

        def action_axes_hide(event):
            ax.grid(visible=False)
            ax.axis('off')
            plt.draw()

        def action_grid_draw(event):
            ax.axis('on')
            ax.grid(visible=True)
            plt.draw()

        button_axes_draw.on_clicked(action_axes_draw)
        button_grid_draw.on_clicked(action_grid_draw)
        button_axes_hide.on_clicked(action_axes_hide)

        plt.show()


if __name__ == '__main__':
    main()
