from decimal import Decimal
from datetime import date, datetime
import pandas as pd



def agate_to_df(table):
    def _pandify(table):
        for row in table.rows:
            p = []
            for v in row:
                if isinstance(v, date):
                    val = datetime(v.year, v.month, v.day)
                elif isinstance(v, Decimal):
                    val = int(v) if v.to_integral_value() == v else float(v)
                else:
                    val = v
                p.append(val)
            yield(p)

    return pd.DataFrame(_pandify(table), columns=table.column_names)

