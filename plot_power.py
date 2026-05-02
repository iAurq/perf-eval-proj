import os
import argparse
import pandas as pd
import plotly.express as px
import plotly.subplots as ps
import plotly.graph_objects as go

stats = {
    'power.draw [W]': {
        'y-axis': 'Power (Watts)',
        'trace': 'pwr'
    },
    'utilization.gpu [%]': {
        'y-axis': 'GPU Utilization (%)',
        'trace': 'util_gpu'
    },
    'utilization.memory [%]': {
        'y-axis': 'Memory Utilization (%)',
        'trace': 'util_mem'
    },
    'memory.used [MiB]': {
        'y-axis': 'Memory Used (MiB)',
        'trace': 'mem_used'
    },
    'clocks.current.graphics [MHz]': {
        'y-axis': 'Graphics Frequency (MHz)',
        'trace': 'clk_graphic'
    },
    'clocks.current.memory [MHz]': {
        'y-axis': 'Memory Frequency (MHz)',
        'trace': 'clk_memory'
    }
}

def make_graphs(file_name):
    """
    This will make a graph for each metric. Imagine this is what we'll use for the paper.
    """
    # Read CSV file
    df = pd.read_csv(file_name)

    # Clean up df
    df = df.rename(columns=lambda x: x.strip())
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['relative_time'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
    df['temperature.gpu'] = df['temperature.gpu'].astype(int)
    df['power.draw [W]'] = df['power.draw [W]'].replace({' W':''}, regex=True).astype(float)
    df['utilization.gpu [%]'] = df['utilization.gpu [%]'].replace({' %':''}, regex=True).astype(int)
    df['utilization.memory [%]'] = df['utilization.memory [%]'].replace({' %':''}, regex=True).astype(int)
    df['memory.used [MiB]'] = df['memory.used [MiB]'].replace({' MiB':''}, regex=True).astype(int)
    df['clocks.current.graphics [MHz]'] = df['clocks.current.graphics [MHz]'].replace({' MHz':''}, regex=True).astype(int)
    df['clocks.current.memory [MHz]'] = df['clocks.current.memory [MHz]'].replace({' MHz':''}, regex=True).astype(int)


    # Make figure
    fig = ps.make_subplots(
        specs=[[{"secondary_y": True}]]
    )

    # Add each subplot to fig
    for stat in stats:
        fig.add_trace(
            go.Scatter(
                x=df['relative_time'],
                y=df[stat],
                name=stats[stat]['trace'],
                mode='lines+markers',
                visible=False,
            ),
        )

    # Make pretty
    fig.update_layout(
        title_text=f"{file_name.split('/')[2][:-4]} Metrics",
        # title_text=f"GPU Power Trace: {file_name.split('/')[2][:-4]}",
        xaxis_title="Relative Time (s)",
        font_family='Times New Roman',
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
        # title_x=0.5 # Set title to center
    )
    fig.update_traces(
        line={
            'width': 2,
        },
        marker={
            'size': 1,
        }
    )
    fig.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey'
    )

    os.makedirs(f'{file_name[:-4]}', exist_ok=True)
    #  Make graph for each figure
    for stat in stats:
        fig.update_yaxes(title_text=stats[stat]['y-axis'], secondary_y=False)
        fig.update_traces(
            visible=True,
            selector=({'name': stats[stat]['trace']})
        )
        fig.write_image(
            f'{file_name[:-4]}/{stats[stat]['trace']}.png',
            scale=2
            # width=1920,
            # height=1080,
        )
        fig.update_traces(
            visible=False,
            selector=({'name': stats[stat]['trace']})
        )

    # Make a silly stats file
    with open(f'{file_name[:-4]}/stats.txt', 'w') as f:
        for stat in stats:
            f.write(f'Average {stat} : {df[stat].mean()}\n')

    # # Keeping old method to make two y-axis chart if we want to use it for later
    # fig.add_trace(
    #     go.Scatter(
    #         x=df['relative_time'],
    #         y=df['power.draw [W]'],
    #         name="Power",
    #         mode='lines+markers'
    #     ),
    # )
    # fig.add_trace(
    #     go.Scatter(
    #         x=df['relative_time'],
    #         y=df['temperature.gpu'],
    #         name="Temp",
    #         mode='lines+markers',
    #         visible=False,
    #     ),
    #     secondary_y=True,
    # )

    # fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)
    # fig.update_yaxes(title_text="Power (Watts)", secondary_y=False)

    # # Display figure Power
    # fig.write_image(
    #     f'{file_name[:-4]}_pw.png',
    #     scale=2
    #     # width=1920,
    #     # height=1080,
    # )

    # fig.update_traces(
    #     visible=False,
    #     selector=({'name': 'Temp'})
    # )

    # # Display Figure Temperature
    # fig.for_each_trace(
    #     lambda trace: trace.update(visible=True) if trace.name == "Temp" else trace.update(visible=False),
    # )
    # fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    # fig.write_image(
    #     f'{file_name[:-4]}_temp.png',
    #     scale=2
    # )
    # fig.show()

def mega_graph(file_name):
    """
    I intend to use this for analysis purpose, we might want to make a prettier version.
    """
    df = pd.read_csv(file_name)

    df = df.rename(columns=lambda x: x.strip())
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['relative_time'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

    for col in stats.keys():
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract('([-+]?\\d*\\.\\d+|\\d+)').astype(float)

    groups = [
        {"title": "Power (Watts)", "metrics": ["power.draw [W]"]},
        {"title": "<span style='color:red'>Memory</span> and <span style='color:green'>GPU Utilization</span> (%)", "metrics": ["utilization.gpu [%]", "utilization.memory [%]"]},
        {"title": "Memory Used (MiB)", "metrics": ["memory.used [MiB]"]},
        {"title": "<span style='color:orange'>Graphic</span> and <span style='color:cyan'>Memory</span> Clock Frequency (MHz)", "metrics": ["clocks.current.graphics [MHz]", "clocks.current.memory [MHz]"]}
    ]

    fig = ps.make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        subplot_titles=[g["title"] for g in groups]
    )

    for row_idx, group in enumerate(groups, 1):
        for metric_col in group["metrics"]:
            if metric_col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['relative_time'],
                        y=df[metric_col],
                        name=stats[metric_col]['trace'],
                        mode='lines',
                        line=dict(width=2)
                    ),
                    row=row_idx, col=1
                )

    fig.update_layout(
        # height=1000,
        # width=1100,
        title_text=f"Distilled GPU Metrics: {file_name.split('/')[-1]}",
        font_family='Times New Roman',
        plot_bgcolor='white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=20, t=80, b=60),
        showlegend=False,
    )

    fig.update_xaxes(showline=True, linecolor='black', gridcolor='lightgrey', mirror=True, ticks='outside')
    fig.update_yaxes(showline=True, linecolor='black', gridcolor='lightgrey', mirror=True, ticks='outside')
    fig.update_xaxes(title_text="Relative Time (s)", row=4, col=1)

    os.makedirs(f'{file_name[:-4]}', exist_ok=True)
    output_path = f"{file_name[:-4]}/distilled.png"
    fig.write_image(output_path, scale=3)
    print(f"Distilled graph saved: {output_path}")

parser = argparse.ArgumentParser(description="Plot_Power.py")
parser.add_argument(
    '--report',
    type=str,
    default='outputs/spec/3dsmax-08_20260501_132819_smi.csv',
    help='Input csv report (or directory that contains all reports)'
)
args = parser.parse_args()

if os.path.isfile(args.report):
    make_graphs(args.report)
    mega_graph(args.report)
elif os.path.isdir(args.report):
    dirc = args.report
    for file in os.listdir(dirc):
        if file.endswith(".csv"):
            make_graphs(f'{dirc}/{file}')
            mega_graph(f'{dirc}/{file}')