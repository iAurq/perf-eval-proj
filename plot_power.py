import argparse
import pandas as pd
import plotly.express as px
import plotly.subplots as ps
import plotly.graph_objects as go

parser = argparse.ArgumentParser(description="Plot_Power.py")
parser.add_argument('--report', type=str, default='data/test.csv', help='Input csv report')
args = parser.parse_args()

# Read CSV file
file_name = args.report
df = pd.read_csv(file_name)
df = df.rename(columns=lambda x: x.strip())

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['relative_time'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
df['temperature.gpu'] = df['temperature.gpu'].astype(int)

df['power.draw [W]'] = df['power.draw [W]'].replace({' W':''}, regex=True).astype(float)

# Make figure
fig = ps.make_subplots(
    specs=[[{"secondary_y": True}]]
)

fig.add_trace(
    go.Scatter(
        x=df['relative_time'],
        y=df['power.draw [W]'],
        name="Power",
        mode='lines+markers'
    ),
    secondary_y=False,
)

# fig.add_trace(
#     go.Scatter(
#         x=df['relative_time'],
#         y=df['temperature.gpu'],
#         name="Temp",
#         mode='lines+markers'
#     ),
#     secondary_y=True,
# )

# fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)
fig.update_yaxes(title_text="Power (Watts)", secondary_y=False)

# Make pretty
fig.update_layout(
    title_text=f"GPU Power Trace: {file_name.split('/')[1][:-4]}",
    xaxis_title="Relative Time (s)",
    font_family='Times New Roman',
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

# Display figure
fig.write_image(
    f'{args.report[:-4]}.png',
    scale=2
    # width=1920,
    # height=1080,
)
fig.show()
