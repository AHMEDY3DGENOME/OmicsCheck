import gzip
import pandas as pd
from io import BytesIO

def parse_series_matrix(buffer: BytesIO) -> pd.DataFrame:
    """
    Parses a GEO .gz matrix file and extracts expression data,
    either using the table markers or by fallback logic.
    """
    with gzip.open(buffer, 'rt') as f:
        lines = f.readlines()

    # Try to locate matrix start/end using official markers
    try:
        start = next(i for i, line in enumerate(lines) if line.startswith("!series_matrix_table_begin")) + 1
        end = next(i for i, line in enumerate(lines) if line.startswith("!series_matrix_table_end"))
        data_lines = lines[start:end]
    except StopIteration:
        # Fallback: look for first line that starts with 'ID_REF' as header
        data_start = next(i for i, line in enumerate(lines) if line.startswith("ID_REF"))
        data_lines = lines[data_start:]

    # Convert lines to DataFrame
    data_str = "".join(data_lines)
    df = pd.read_csv(BytesIO(data_str.encode()), sep='\t')

    # Clean index
    df.set_index(df.columns[0], inplace=True)

    # Ensure numeric values
    df = df.apply(pd.to_numeric, errors='coerce')

    # Drop empty rows/columns
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    return df
