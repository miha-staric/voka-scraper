from config import config
import pandas as pd

def handle_default_printing(dumping_data):
    """
    Prints dumping data in default style with full records, as well as summarized table with sum of BIO and MKO dumpings.

    Args:
        dumping_data (DataFrame): Dumping data in pandas DataFrame object.
    """
    print('Full data:')
    print(dumping_data)

    pivot_summary = dumping_data.pivot_table(
        values='quantity',
        index=None,
        columns='fraction',
        aggfunc='sum',
        fill_value=0
    )

    print('Summarized data:')
    print(pivot_summary)

def handle_months_printing(dumping_data):
    """
    Prints dumping data in months style where each month has grouped BIO and MKO dumpings as well as calculated costs.

    Args:
        dumping_data (DataFrame): Dumping data in pandas DataFrame object.
    """
    dumping_data['dumpedAtDate'] = pd.to_datetime(dumping_data['dumpedAtDate'])
    dumping_data['month'] = dumping_data['dumpedAtDate'].dt.to_period('M').astype(str)

    # Group by month and fraction summing quantity
    grouped = dumping_data.groupby(['month', 'fraction']).agg(
        quantity=('quantity', 'sum')
    ).reset_index()

    # Ensure every month has both fractions present
    months = grouped['month'].unique()
    fractions = ['BIO', 'MKO']

    # Create full index as cartesian product of months x fractions
    full_index = pd.MultiIndex.from_product([months, fractions], names=['month', 'fraction'])

    # Reindex grouped DataFrame to full index, filling missing quantities with 0
    grouped = grouped.set_index(['month', 'fraction']).reindex(full_index, fill_value=0).reset_index()

    # Costs map from config
    cost_map = {
        'BIO': float(config.BIO),
        'MKO': float(config.MKO)
    }

    # Calculate real cost per fraction per row
    grouped['real_cost_fraction'] = grouped.apply(
        lambda row: row['quantity'] * cost_map.get(row['fraction'], 0),
        axis=1
    )

    # Minimum cost thresholds
    min_costs = {
        'BIO': float(config.MIN_BIO),
        'MKO': float(config.MIN_MKO)
    }

    # Apply minimum cost per fraction per row
    grouped['total_cost_fraction'] = grouped.apply(
        lambda row: max(row['real_cost_fraction'], min_costs.get(row['fraction'], 0)),
        axis=1
    )

    # Sum costs by month
    real_costs = grouped.groupby('month')['real_cost_fraction'].sum().reset_index(name='real_cost')
    total_costs = grouped.groupby('month')['total_cost_fraction'].sum().reset_index(name='total_cost')

    # Pivot quantities to columns BIO and MKO as integers
    quantities = grouped.pivot_table(
        index='month', columns='fraction', values='quantity', aggfunc='sum', fill_value=0
    ).reset_index()
    quantities[['BIO', 'MKO']] = quantities[['BIO', 'MKO']].astype(int)

    # Merge quantities with cost summaries
    final_df = pd.merge(quantities, real_costs, on='month')
    final_df = pd.merge(final_df, total_costs, on='month')

    print('Months data:')
    print(final_df)

def handle_years_printing(dumping_data):
    """
    Prints dumping data in years style where each year has grouped BIO and MKO dumpings.

    Args:
        dumping_data (DataFrame): Dumping data in pandas DataFrame object.
    """
    # Ensure date column is datetime
    dumping_data['dumpedAtDate'] = pd.to_datetime(dumping_data['dumpedAtDate'])
    
    # Extract year period as string
    dumping_data['year'] = dumping_data['dumpedAtDate'].dt.to_period('Y').astype(str)
    
    # Group by year and fraction and sum quantities
    yearly_summary = dumping_data.groupby(['year', 'fraction'])['quantity'].sum().reset_index()
    
    # Pivot so fractions become columns, fill missing with 0
    pivot = yearly_summary.pivot_table(
        index='year',
        columns='fraction',
        values='quantity',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Optional: convert quantity columns to int if all values are integer-like
    for col in ['BIO', 'MKO']:
        if col in pivot.columns:
            pivot[col] = pivot[col].astype(int)
        else:
            # If a fraction column is missing (e.g. no MKO data), add it with zeros
            pivot[col] = 0

    pivot.columns.name = None

    print("Years data:")
    print(pivot)
