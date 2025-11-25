import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def create_financial_timeline(upfront_cost, annual_savings, payback_period, npv_25yr, inverter_replacement_cost):
    """Creates a Plotly line chart for cumulative savings over 25 years."""
    years = np.arange(0, 26)
    cumulative_savings = np.zeros(26)
    
    # Simple model: constant annual savings, one inverter replacement
    for i in range(1, 26):
        savings = annual_savings
        # Inverter replacement at year 10 (cost incurred at the start of year 10)
        if i == 10:
            savings -= inverter_replacement_cost
        
        cumulative_savings[i] = cumulative_savings[i-1] + savings
    
    # Adjust for initial cost
    cumulative_net_savings = cumulative_savings - upfront_cost
    
    df = pd.DataFrame({
        'Year': years,
        'Cumulative Net Savings (KSh)': cumulative_net_savings
    })
    
    fig = px.line(df, x='Year', y='Cumulative Net Savings (KSh)', 
                  title='Financial Timeline: Cumulative Net Savings Over 25 Years',
                  labels={'Cumulative Net Savings (KSh)': 'Cumulative Net Savings (KSh)', 'Year': 'Year'},
                  template='plotly_white')
    
    # Mark payback point
    fig.add_trace(go.Scatter(
        x=[payback_period],
        y=[0],
        mode='markers',
        name=f'Payback Point ({payback_period:.1f} yrs)',
        marker=dict(size=10, color='red')
    ))
    
    # Mark inverter replacement
    fig.add_trace(go.Scatter(
        x=[10],
        y=[cumulative_net_savings[10]],
        mode='markers',
        name='Inverter Replacement (Year 10)',
        marker=dict(size=10, color='orange', symbol='star')
    ))
    
    fig.update_layout(
        hovermode="x unified",
        yaxis_tickprefix="KSh ",
        shapes=[
            dict(
                type='line',
                xref='x', yref='y',
                x0=0, y0=0,
                x1=25, y1=0,
                line=dict(color='Gray', width=1, dash='dash')
            )
        ]
    )
    
    return fig

def create_cost_breakdown_pie(panel_cost, inverter_cost, battery_cost, installation_cost, other_cost):
    """Creates a Plotly pie chart for system cost breakdown."""
    labels = ['Panels', 'Inverter', 'Battery (if included)', 'Installation', 'Other (Mounts, Cables, Permits)']
    values = [panel_cost, inverter_cost, battery_cost, installation_cost, other_cost]
    
    # Filter out zero values for cleaner chart
    data = [(l, v) for l, v in zip(labels, values) if v > 0]
    labels, values = zip(*data)
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(title_text="System Cost Breakdown (KSh)", template='plotly_white')
    
    return fig

def create_co2_offset_gauge(annual_co2_offset_tons):
    """Creates a Plotly gauge chart for annual CO2 offset."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=annual_co2_offset_tons,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Annual CO₂ Offset (Tons)"},
        gauge={
            'axis': {'range': [0, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkgreen"},
            'bgcolor': "white",
            'steps': [
                {'range': [0, 1], 'color': 'lightgray'},
                {'range': [1, 3], 'color': 'lightgreen'},
                {'range': [3, 5], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 4.0
            }
        }
    ))
    fig.update_layout(margin=dict(l=20, r=30, t=50, b=20))
    return fig

def create_monthly_energy_flow(annual_generation_kwh, monthly_consumption_kwh):
    """Creates a simple bar chart for monthly energy flow (generation vs consumption)."""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Simplified: assume uniform consumption and generation for a first pass
    monthly_consumption = [monthly_consumption_kwh] * 12
    monthly_generation = [annual_generation_kwh / 12] * 12
    
    df = pd.DataFrame({
        'Month': months,
        'Consumption (kWh)': monthly_consumption,
        'Generation (kWh)': monthly_generation
    })
    
    fig = go.Figure(data=[
        go.Bar(name='Consumption', x=df['Month'], y=df['Consumption (kWh)'], marker_color='blue'),
        go.Bar(name='Generation', x=df['Month'], y=df['Generation (kWh)'], marker_color='orange')
    ])
    
    fig.update_layout(barmode='group', title='Monthly Energy Flow (Consumption vs. Generation)', template='plotly_white')
    
    return fig

if __name__ == '__main__':
    # Example usage for testing
    upfront_cost = 396000
    annual_savings = 50400
    payback_period = 7.8
    npv_25yr = 2100000
    inverter_replacement_cost = 100000
    
    # Financial Timeline
    fig_timeline = create_financial_timeline(upfront_cost, annual_savings, payback_period, npv_25yr, inverter_replacement_cost)
    # fig_timeline.show() # Cannot show in sandbox
    
    # Cost Breakdown
    panel_cost = 180000
    inverter_cost = 80000
    battery_cost = 50000
    installation_cost = 60000
    other_cost = 26000
    fig_pie = create_cost_breakdown_pie(panel_cost, inverter_cost, battery_cost, installation_cost, other_cost)
    # fig_pie.show()
    
    # CO2 Gauge
    annual_co2_offset_tons = 2.4
    fig_gauge = create_co2_offset_gauge(annual_co2_offset_tons)
    # fig_gauge.show()
    
    # Monthly Energy Flow
    annual_generation_kwh = 4500
    monthly_consumption_kwh = 300
    fig_flow = create_monthly_energy_flow(annual_generation_kwh, monthly_consumption_kwh)
    # fig_flow.show()
    
    print("Visualization functions created successfully.")
