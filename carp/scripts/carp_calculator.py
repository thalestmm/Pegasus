from fpdf import FPDF
from math import ceil
from datetime import date


parachute_limits = {
    "T-10 AC/RAC": [13, 13],
    "T-10 C/D, MC1-1C, RALC": [13, 10],
    "ASA": [18, 14],
    "G11 A, G12 D": [18, 18],
    "G13, G14": [20, 20],
    "STAB": [25, 25]
}
counter = 0
chute_name_list = []
for chute in parachute_limits:
    counter += 1
    chute_name_list.append(chute)


try:
    name = values['name'].upper()
    trigram = values['trigram'].upper()
    drop_height = int(values['drop_height'])
    terrain_alt = int(values['terrain_alt'])
    point_of_impact = int(values['point_of_impact'])
    pressure = int(values['pressure'])
    temperature = float(values['temperature'])
    speed = int(values['speed'])
    mag_course = int(values['mag_course'].replace("°","").replace("º",""))
    chute_selection = values['chute_selection']
    chute_amount = int(values['chute_amount'])
    rate_of_fall = float(values['rate_of_fall'])
    vertical_distance = int(values['vertical_distance'])
    dec_quocient = float(values['dec_quocient'])
    tfc = float(values['tfc'])
    exit_time = float(values['exit_time'])
    if values['measure_unit_m'] == True:
        measure_unit = 'M'
    else:
        measure_unit = 'J'


class CarpCalculator:
    def __init__(self):
        today = date.today()

    def f_03():
        return drop_height + terrain_alt

    def f_a(pressure=1013):
        return (1013 - pressure) * 30

    # PRESSURE ALTITUDE
    def f_05():
        return f_03() + f_a(pressure)

    # Caso a temperatura seja 15, não deve haver defasagem entre a correta
    # altura de lançamento e a planejada

    # CORRECT DROP HEIGHT
    ground_temp = temperature - (f_05() * (-2) / 1000)

    def f_b():
        difference = (-1.6) * temperature + 24
        return int(drop_height + difference)

    # INDICATED ALTITUDE
    def f_08():
        return f_b() + terrain_alt

    # Com uma temperatura no solo de 15C e 1013 HPa, não deve
    # haver defasagem entre velocidade prevista e real

    # TRUE AIR SPEED
    def f_11(speed=speed):
        difference = 0.4 * temperature - 6
        return ceil(speed + difference)

    # ADJUSTED RATE OF FALL
    def f_13(rate_of_fall=rate_of_fall, temperature=temperature):
        difference = 0.056 * temperature - 0.84
        return round(rate_of_fall + difference)

    # STABILIZATION ALTITUDE
    def f_16(vert_dist=vertical_distance, poi=point_of_impact):
        return f_03() - poi - vert_dist

    # TOTAL TIME OF FALL
    def f_19(tofc=tfc):
        time_of_fall = f_16() / f_13()
        return round(time_of_fall + tofc)

    # FORWARD TRAVEL DISTANCE
    ftt = dec_quocient + exit_time # FORWARD TRAVEL TIME
    def ftd(dec_quoc=dec_quocient, et=exit_time):
        return round((ftt * f_11()) / 1.78)

    # WIND CIRCLES
    def cv():
        return round((f_19()*5)/1.78)

    # 5 HEADING TAIL
    def ht5():
        return round((5 * (ftt + f_19())) / 1.78)

    offset2 = 50 # 2° OFFSET ALWAYS 50 - EITHER YD OR M


    carp_vectors = [ftd(),cv(),ht5(),offset2]
    new_carp_vectors = []

    # IF DESIRED UNIT IS METERS, MULTIPLY BY 0.91
    if measure_unit == 'M' :
        unit = "m"
        for i in carp_vectors:
            new_carp_vectors.append(round(i * 0.91))
        pass
    else:
        unit = "yd"

    new_carp_vectors[-1] = 50 # RETURN 2° OFFSET TO 50

    launch_axis = []
    for i in range(12):
        course = mag_course + 30*i
        if course > 360:
            course-=360
        if course < 100:
            launch_axis.append(f'0{course}°')
        else:
            launch_axis.append(f'{course}°')

    # PRINT SETUP
    doc_width = 210
    doc_height = 297

    scale = 0.20 # SCALE TO BEST FIT THE DATA

    class PDF(FPDF):
        def create_basic(self):
            pdf.line(25, yc, doc_width - 25, yc)
            pdf.line(xc, 64, xc, doc_height - 60)
            # ARROW
            pdf.line(xc - 2, 64, xc, 60)
            pdf.line(xc, 60, xc + 2, 64)
            pdf.line(xc - 2, 64, xc + 2, 64)

        def set_title(self):
            self.set_font("Arial", "BI", 15)
            pdf.cell(0, 10, "COMPUTED AIR RELEASE POINT",0,0,"C")

        def description(self):
            self.set_font("Arial","",13)
            self.text(15,30,f"FTD = {new_carp_vectors[0]} {unit}")
            self.ellipse(15,32,5,5)
            self.text(16.85,34.8,'.')
            self.text(20.5,36,f" = {new_carp_vectors[1]} {unit}")
            self.text(15,42,f"5 H/T = {new_carp_vectors[2]} {unit}")
            self.text(15,48,f"{pressure} HPa")
            self.text(15,54,f"{temperature}°C")
            self.text(15,60,f"{drop_height} ft")
            self.text(15,66,f"{chute_amount} {chute_selection}")
            self.text(doc_width-68,30,f"Limites: {parachute_limits[chute_selection][0]}kt (D) e {parachute_limits[chute_selection][1]}kt (N)")

        def my_footer(self):
            self.set_font("Arial","I",13)
            self.text(15,doc_height-10,f"{name.upper()} - {today}")

        def target(self):
            self.set_font("Arial","B",16)
            self.set_text_color(255,42,42)
            self.text(doc_width/2-2, doc_height/2 - new_carp_vectors[0]*scale, 'A')

        def wind_circles(self):
            self.set_draw_color(255,42,42)
            boung_box = (xc-(new_carp_vectors[1]*scale),yc-(new_carp_vectors[1]*scale))
            xe,ye = boung_box
            for i in range(4):
                adjust = new_carp_vectors[1]*scale
                increase = (i+1)*adjust
                self.ellipse(xe-increase+adjust,ye-increase+adjust,increase*2,increase*2)

        def offset2(self):
            boundary = 75
            self.set_font("Arial","",7)
            for i in range(4):
                value = new_carp_vectors[-1]*(i+1)
                if value < 100:
                    value = f"0{value}"
                else:
                    value = f"{value}"
                distance = (i + 1) * new_carp_vectors[-1] * scale
                pdf.line(xc + distance, boundary, xc + distance, doc_height - boundary)
                pdf.text(xc + distance - 2, boundary - 1.5,f"{value}")
                pdf.line(xc - distance, boundary, xc - distance, doc_height - boundary)
                pdf.text(xc - distance - 2, boundary - 1.5, f"{value}")

        def head_tail5(self):
            boundaries = (42,6)
            self.set_font('Arial','B',14)
            self.set_draw_color(102,102,102)
            a,b = boundaries
            pdf.line(a, yc + b, xc, yc)
            pdf.rect(27.5, yc + 4, 12, 6.5)
            pdf.text(a-13.5,yc+b+3,f"{-new_carp_vectors[0]}")
            pdf.line(xc, yc, doc_width - a, yc + b)
            pdf.rect(doc_width - 40, yc + 4, 12, 6.5)
            pdf.text(doc_width - 38,yc + b + 3,f"{speed}")

            for i in range(3):
                forward_ftd = -new_carp_vectors[0] + (i+1)*new_carp_vectors[2]
                backward_ftd = -new_carp_vectors[0] - (i+1)*new_carp_vectors[2]
                if forward_ftd > -100 and forward_ftd < 0:
                    forward_ftd = f"-0{-forward_ftd}"
                elif forward_ftd > 0 and forward_ftd < 10:
                    forward_ftd = f" 00{forward_ftd}"
                elif forward_ftd < 100 and forward_ftd > 0:
                    forward_ftd = f" 0{forward_ftd}"
                factor = (i + 1) * new_carp_vectors[-2] * scale
                pdf.line(a, yc + b + factor, xc, yc + factor)
                pdf.text(a - 13.5, yc + b + 2.5 + factor, f"{backward_ftd}")
                pdf.line(xc, yc + factor, doc_width - a, yc + b + factor)
                pdf.text(doc_width - 38, yc + b + 2.5 + factor, f"{speed+5*(i+1)}")
                pdf.line(a, yc + b - factor, xc, yc - factor)
                pdf.text(a - 13.5, yc + b + 2.5 - factor, f"{forward_ftd}")
                pdf.line(xc, yc - factor, doc_width - a, yc + b - factor)
                pdf.text(doc_width - 38, yc + b + 2.5 - factor, f"{speed - 5 * (i + 1):03d}")

        def mag_courses(self):
            self.set_font("Arial","B",16)
            self.set_text_color(0,102,255)
            self.set_draw_color(0,0,0)
            pdf.rect(xc - 7, 50, 14, 7)
            pdf.text(xc-5.5,55.5,f"{launch_axis[0]}")
            pdf.line(doc_width - 62, yc - 72, xc, yc)
            pdf.text(doc_width - 60, yc - 72, f"{launch_axis[1]}")
            pdf.line(doc_width - 45, yc - 34, xc, yc)
            pdf.text(doc_width - 55, yc - 36, f"{launch_axis[2]}")
            pdf.text(doc_width - 23, yc + 1.5, f"{launch_axis[3]}")
            pdf.line(doc_width - 45, yc + 34, xc, yc)
            pdf.text(doc_width - 58, yc + 39, f"{launch_axis[4]}")
            pdf.line(doc_width - 62, yc + 72, xc, yc)
            pdf.text(doc_width - 60, yc + 75, f"{launch_axis[5]}")
            pdf.text(xc - 5.5, doc_height - 54, f"{launch_axis[6]}")
            pdf.line(xc, yc, 62, yc + 72)
            pdf.text(49, yc + 75, f"{launch_axis[7]}")
            pdf.line(xc, yc, 45, yc + 34)
            pdf.text(48, yc + 39, f"{launch_axis[8]}")
            pdf.text(13, yc + 1.5, f"{launch_axis[9]}")
            pdf.line(xc, yc, 45, yc - 34)
            pdf.text(47, yc - 36, f"{launch_axis[10]}")
            pdf.line(xc, yc, 62, yc - 72)
            pdf.text(50, yc - 72, f"{launch_axis[11]}")

    pdf = PDF('P','mm',(doc_width,doc_height))
    pdf.add_page()
    pdf.set_author("Ten Av Thales - OCT 2021")
    center = (doc_width/2,doc_height/2)
    xc,yc = center

    # CALLING THE CLASS' METHODS
    pdf.create_basic()
    pdf.set_title()
    pdf.description()
    pdf.head_tail5()
    pdf.my_footer()
    pdf.offset2() # 2° OFFSET
    pdf.target() # ALVO
    pdf.mag_courses()
    pdf.wind_circles() # CÍRCULOS DE VENTO


    pdf.output(f'CARP {trigram.upper()} - {today}.pdf', 'F')











