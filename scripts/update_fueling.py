from mission_planner.models import Airport
import pandas as pd
import logging


def download_new_file():
    pass


def run():
    # CLEAR ALL FUELING DATA ON DB FOR SAFETY
    Airport.objects.all().update(has_fueling=False)

    filepath = 'scripts/data/Localidades_contratadas.xlsx'

    df = pd.read_excel(filepath, "JANEIRO 23 ")
    # TODO: AUTO PICK THE MOST RECENT TABLE AVAILABLE

    icao = df.iloc[3:,3]
    qav  = df.iloc[3:,13]
    adtv = df.iloc[3:,14]

    qav = qav.where(qav == 'OK', other = 0)
    qav = qav.where(qav == 0, other=1)
    qav = qav.convert_dtypes()

    adtv = adtv.where(adtv == 'OK', other = 0)
    adtv = adtv.where(adtv == 0, other=1)
    adtv = adtv.convert_dtypes()

    clean_df = pd.concat([icao, qav, adtv], axis=1)
    clean_df = clean_df.rename(columns={'Unnamed: 3':'icao',
                                         'Unnamed: 13':'qav',
                                         'Unnamed: 14':'adtv',})

    clean_df['fueling_available'] = clean_df.qav + clean_df.adtv
    clean_df = clean_df.astype({'fueling_available': 'boolean'})

    icao_signs = clean_df.icao.items()
    fueling    = clean_df.fueling_available.items()

    for icao, fueling in zip(icao_signs, fueling):
        if type(icao[1]) is not str:
            continue
        airport = Airport.objects.get(icao_sign=icao[1])
        airport.has_fueling = fueling[1]
        airport.save()

    logging.info("Done!")
