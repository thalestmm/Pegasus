from fpdf import FPDF
from math import ceil
from datetime import date
from typing import Dict


class CarpCalculator:
    def __init__(self, values:Dict):

        self.name = values['name'].upper()
        self.trigram = values['trigram'].upper()

        self.drop_height = int(values['drop_height'])
        self.terrain_alt = int(values['terrain_alt'])
        self.point_of_impact = int(values['point_of_impact'])

        self.pressure = int(values['pressure'])
        self.temperature = float(values['temperature'])
        self.speed = int(values['speed'])
        self.mag_course = int(values['mag_course'].replace("°","").replace("º",""))

        self.parachute_limits = {
            "T-10 AC/RAC": [13, 13],
            "T-10 C/D, MC1-1C, RALC": [13, 10],
            "ASA": [18, 14],
            "G11 A, G12 D": [18, 18],
            "G13, G14": [20, 20],
            "STAB": [25, 25]
        }
        self.chute_name_list = []
        for chute in self.parachute_limits:
            self.chute_name_list.append(chute)

        self.chute_selection = self.chute_name_list[values['chute_selection']]
        self.chute_amount = int(values['chute_amount'])
        self.rate_of_fall = float(values['rate_of_fall'])
        self.vertical_distance = int(values['vertical_distance'])
        self.dec_quocient = float(values['dec_quocient'])
        self.tfc = float(values['tfc'])
        self.exit_time = float(values['exit_time'])

        if values['measure_unit'] == "M":
            self.measure_unit = 'M'
        else:
            self.measure_unit = 'J'

        self.today = date.today()
        self.offset2 = 50  # 2° OFFSET ALWAYS 50 - EITHER YD OR M

        # CORRECT DROP HEIGHT
        self.ground_temp = self.temperature - (self.f_05() * (-2) / 1000)

    def f_03(self):
        return self.drop_height + self.terrain_alt

    @staticmethod
    def f_a(pressure=1013):
        return (1013 - pressure) * 30

    # PRESSURE ALTITUDE
    def f_05(self):
        return self.f_03() + self.f_a(self.pressure)

    # Caso a temperatura seja 15, não deve haver defasagem entre a correta altura de lançamento e a planejada

    def f_b(self):
        difference = (-1.6) * self.temperature + 24
        return int(self.drop_height + difference)

    # INDICATED ALTITUDE
    def f_08(self):
        return self.f_b() + self.terrain_alt

    # Com uma temperatura no solo de 15C e 1013 HPa, não deve
    # haver defasagem entre velocidade prevista e real

    # TRUE AIR SPEED
    def f_11(self, speed):
        speed = self.speed
        difference = 0.4 * self.temperature - 6
        return ceil(speed + difference)

    # ADJUSTED RATE OF FALL
    def f_13(self) -> int:
        difference = 0.056 * self.temperature - 0.84
        return round(self.rate_of_fall + difference)

    # STABILIZATION ALTITUDE
    def f_16(self):
        return self.f_03() - self.point_of_impact - self.vertical_distance

    # TOTAL TIME OF FALL
    def f_19(self):
        time_of_fall = self.f_16() / self.f_13()
        return round(time_of_fall + self.tfc)

    # FORWARD TRAVEL DISTANCE
    def ftt(self):
        return self.dec_quocient + self.exit_time

    def ftd(self):
        return round((self.ftt() * self.f_11()) / 1.78)

    # WIND CIRCLES
    def cv(self):
        return round((self.f_19()*5)/1.78)

    # 5 HEADING TAIL
    def ht5(self):
        return round((5 * (self.ftt() + self.f_19())) / 1.78)

    def carp_vectors(self):
        carp_vectors = [self.ftd(), self.cv(), self.ht5(), self.offset2]
        new_carp_vectors = []

        # IF DESIRED UNIT IS METERS, MULTIPLY BY 0.91
        if self.measure_unit == 'M':
            unit = "m"
            for i in carp_vectors:
                new_carp_vectors.append(round(i * 0.91))
            pass
        else:
            unit = "yd"

        new_carp_vectors[-1] = 50 # RETURN 2° OFFSET TO 50

        launch_axis = []
        for i in range(12):
            course = self.mag_course + 30*i
            if course > 360:
                course-=360
            if course < 100:
                launch_axis.append(f'0{course}°')
            if course < 10:
                launch_axis.append(f'00{course}°')
            else:
                launch_axis.append(f'{course}°')

        return new_carp_vectors, launch_axis, unit

    def full_execute(self):
        carp_vectors, launch_axis, unit = self.carp_vectors()
        return self.name, self.trigram, self.today, carp_vectors, launch_axis, unit, \
               self.chute_amount, self.chute_selection, self.parachute_limits, \
               self.pressure, self.temperature, self.drop_height, self.speed


class PDF(FPDF):
    def __init__(self, name, trigram, carp_vectors,
                 launch_axis, carp_unit, chute_amount, chute_selection, parachute_limits, pressure, temperature,
                 drop_height, speed, orientation='P', unit='mm', dimensions=(210, 297),):

        super().__init__(orientation, unit, dimensions)

        self.add_page()
        self.set_author("Ten Av Thales - OCT 2022")

        self.scale = 0.2 # SCALE TO BEST FIT THE DATA

        self.doc_width, self.doc_height = dimensions
        center = (self.doc_width / 2, self.doc_height / 2)
        self.xc, self.yc = center

        self.carp_vectors = carp_vectors
        self.name         = name
        self.trigram      = trigram
        self.launch_axis  = launch_axis
        self.unit         = carp_unit

        self.chute_amount = chute_amount
        self.chute_selection = chute_selection
        self.parachute_limits = parachute_limits
        self.pressure = pressure
        self.temperature = temperature
        self.drop_height = drop_height
        self.speed = speed

        # CALLING THE CLASS' METHODS
        self.create_basic()
        self.set_title()
        self.description()
        self.head_tail5()
        self.my_footer()
        self.offset2()  # 2° OFFSET
        self.target()  # ALVO
        self.mag_courses()
        self.wind_circles()  # CÍRCULOS DE VENTO

        self.today = date.today()
        self.output(f'CARP {trigram.upper()} - {self.today}.pdf', 'F')

    def create_basic(self):
        self.line(25, self.yc, doc_width - 25, self.yc)
        self.line(self.xc, 64, self.xc, doc_height - 60)
        # ARROW
        self.line(self.xc - 2, 64, self.xc, 60)
        self.line(self.xc, 60, self.xc + 2, 64)
        self.line(self.xc - 2, 64, self.xc + 2, 64)

    def set_title(self, **kwargs):
        self.set_font("Arial", "BI", 15)
        self.cell(0, 10, "COMPUTED AIR RELEASE POINT",0,0,"C")

    def description(self):
        self.set_font("Arial","",13)
        self.text(15, 30,f"FTD = {self.carp_vectors[0]} {self.unit}")
        self.ellipse(15,32,5,5)
        self.text(16.85,34.8,'.')
        self.text(20.5, 36,f" = {self.carp_vectors[1]} {self.unit}")
        self.text(15, 42,f"5 H/T = {self.carp_vectors[2]} {self.unit}")
        self.text(15,48,f"{self.pressure} HPa")
        self.text(15,54,f"{self.temperature}°C")
        self.text(15,60,f"{self.drop_height} ft")
        self.text(15,66,f"{self.chute_amount} {self.chute_selection}")
        self.text(self.doc_width-68,30,f"Limites: {self.parachute_limits[self.chute_selection][0]}kt (D) e {self.parachute_limits[self.chute_selection][1]}kt (N)")

    def my_footer(self):
        self.set_font("Arial","I",13)
        self.text(15,self.doc_height-10,f"{self.name.upper()} - {self.today}")

    def target(self):
        self.set_font("Arial","B",16)
        self.set_text_color(255,42,42)
        self.text(self.doc_width/2-2, self.doc_height/2 - self.carp_vectors[0]*self.scale, 'A')

    def wind_circles(self):
        self.set_draw_color(255,42,42)
        boung_box = (self.xc - (self.carp_vectors[1] * self.scale), self.yc - (self.carp_vectors[1] * self.scale))
        xe,ye = boung_box
        for i in range(4):
            adjust = self.carp_vectors[1]*self.scale
            increase = (i+1)*adjust
            self.ellipse(xe-increase+adjust,ye-increase+adjust,increase*2,increase*2)

    def offset2(self):
        boundary = 75
        self.set_font("Arial","",7)
        for i in range(4):
            value = self.carp_vectors[-1]*(i+1)
            if value < 100:
                value = f"0{value}"
            else:
                value = f"{value}"
            distance = (i + 1) * self.carp_vectors[-1] * self.scale
            self.line(self.xc + distance, boundary, self.xc + distance, self.doc_height - boundary)
            self.text(self.xc + distance - 2, boundary - 1.5, f"{value}")
            self.line(self.xc - distance, boundary, self.xc - distance, self.doc_height - boundary)
            self.text(self.xc - distance - 2, boundary - 1.5, f"{value}")

    def head_tail5(self):
        boundaries = (42,6)
        self.set_font('Arial','B',14)
        self.set_draw_color(102,102,102)
        a,b = boundaries
        self.line(a, self.yc + b, self.xc, self.yc)
        self.rect(27.5, self.yc + 4, 12, 6.5)
        self.text(a - 13.5, self.yc + b + 3, f"{-self.carp_vectors[0]}")
        self.line(self.xc, self.yc, self.doc_width - a, self.yc + b)
        self.rect(self.doc_width - 40, self.yc + 4, 12, 6.5)
        self.text(self.doc_width - 38, self.yc + b + 3, f"{self.speed}")

        for i in range(3):
            forward_ftd = -self.carp_vectors[0] + (i+1)*self.carp_vectors[2]
            backward_ftd = -self.carp_vectors[0] - (i+1)*self.carp_vectors[2]
            if -100 < forward_ftd < 0:
                forward_ftd = f"-0{-forward_ftd}"
            elif 0 < forward_ftd < 10:
                forward_ftd = f" 00{forward_ftd}"
            elif 100 > forward_ftd > 0:
                forward_ftd = f" 0{forward_ftd}"
            factor = (i + 1) * self.carp_vectors[-2] * self.scale
            self.line(a, self.yc + b + factor, self.xc, self.yc + factor)
            self.text(a - 13.5, self.yc + b + 2.5 + factor, f"{backward_ftd}")
            self.line(self.xc, self.yc + factor, self.doc_width - a, self.yc + b + factor)
            self.text(self.doc_width - 38, self.yc + b + 2.5 + factor, f"{self.speed + 5 * (i + 1)}")
            self.line(a, self.yc + b - factor, self.xc, self.yc - factor)
            self.text(a - 13.5, self.yc + b + 2.5 - factor, f"{forward_ftd}")
            self.line(self.xc, self.yc - factor, self.doc_width - a, self.yc + b - factor)
            self.text(self.doc_width - 38, self.yc + b + 2.5 - factor, f"{self.speed - 5 * (i + 1):03d}")

    def mag_courses(self):
        self.set_font("Arial","B",16)
        self.set_text_color(0,102,255)
        self.set_draw_color(0,0,0)
        self.rect(self.xc - 7, 50, 14, 7)

        self.text(self.xc - 5.5, 55.5, f"{self.launch_axis[0]}")
        self.line(self.doc_width - 62, self.yc - 72, self.xc, self.yc)
        self.text(self.doc_width - 60, self.yc - 72, f"{self.launch_axis[1]}")
        self.line(self.doc_width - 45, self.yc - 34, self.xc, self.yc)
        self.text(self.doc_width - 55, self.yc - 36, f"{self.launch_axis[2]}")
        self.text(self.doc_width - 23, self.yc + 1.5, f"{self.launch_axis[3]}")
        self.line(self.doc_width - 45, self.yc + 34, self.xc, self.yc)
        self.text(self.doc_width - 58, self.yc + 39, f"{self.launch_axis[4]}")
        self.line(self.doc_width - 62, self.yc + 72, self.xc, self.yc)
        self.text(self.doc_width - 60, self.yc + 75, f"{self.launch_axis[5]}")
        self.text(self.xc - 5.5, self.doc_height - 54, f"{self.launch_axis[6]}")
        self.line(self.xc, self.yc, 62, self.yc + 72)
        self.text(49, self.yc + 75, f"{self.launch_axis[7]}")
        self.line(self.xc, self.yc, 45, self.yc + 34)
        self.text(48, self.yc + 39, f"{self.launch_axis[8]}")
        self.text(13, self.yc + 1.5, f"{self.launch_axis[9]}")
        self.line(self.xc, self.yc, 45, self.yc - 34)
        self.text(47, self.yc - 36, f"{self.launch_axis[10]}")
        self.line(self.xc, self.yc, 62, self.yc - 72)
        self.text(50, self.yc - 72, f"{self.launch_axis[11]}")


if __name__ == "__main__":
    pass












