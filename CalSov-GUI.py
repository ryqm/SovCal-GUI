import sys
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QTabWidget, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer

# --- Conversion Functions (Include your existing functions here) ---

# Define the months and their respective number of days in the World calendar
months = [
    ("Attinia", 42),
    ("Havenox", 41),
    ("Iorvia", 42),
    ("Victoria", 41),
    ("Protopia", 42),
    ("Gioia", 41),
    ("Wulfrum", 42),
    ("Tuxia", 43),
    ("Chimpe", 41),
    ("Ratatosqua", 42),
    ("Odinia", 39),
    ("Neo", 42),
]

# Define the days of the week in the World calendar
weekdays = ["Lunas", "Martis", "Adias", "Iovis", "Helvis", "Tunis", "Servera"]

# Total number of days in a World year
days_in_year = sum(days for name, days in months)

# Define the start date of the server
start_date = datetime.datetime(2023, 10, 11, 0, 0, 0)  # Include time at midnight

# Function to convert IRL datetime to UDC day (integer)
def irl_datetime_to_udc(irl_datetime):
    delta = irl_datetime - start_date
    udc_day = int(delta.total_seconds() // (24 * 3600)) + 1  # UDC starts at day 1
    return udc_day

# Function to convert UDC day to IRL datetime (start of the day)
def udc_to_irl_datetime(udc_day):
    total_seconds = (udc_day - 1) * 24 * 3600
    irl_datetime = start_date + datetime.timedelta(seconds=total_seconds)
    return irl_datetime

# Helper function to get the World month and day from the day of the year
def get_world_month_day(world_day_of_year):
    total_days = 0
    for name, days_in_month in months:
        total_days += days_in_month
        if world_day_of_year <= total_days:
            day_in_month = world_day_of_year - (total_days - days_in_month)
            return name, day_in_month
    # If not found, assume last month
    name, days_in_month = months[-1]
    day_in_month = world_day_of_year - (days_in_year - days_in_month)
    return name, day_in_month

# Helper function to get the day of the year from the World month and day
def get_world_day_of_year(month_name, day_in_month):
    total_days = 0
    for name, days_in_month in months:
        if name == month_name:
            total_days += day_in_month
            return total_days
        else:
            total_days += days_in_month
    raise ValueError(f"Invalid month name: {month_name}")

# Season start dates in the World calendar
season_starts = {
    "Spring": ("Iorvia", 4),
    "Summer": ("Gioia", 4),
    "Fall": ("Chimpe", 3),
    "Winter": ("Neo", 4),
}

# Function to determine the current season based on the day of the year
def get_season(world_day_of_year):
    season_days = []
    for season, (month_name, day_in_month) in season_starts.items():
        day_of_year = get_world_day_of_year(month_name, day_in_month)
        season_days.append((day_of_year, season))
    season_days.sort()
    for i in range(len(season_days)):
        if world_day_of_year < season_days[i][0]:
            return season_days[i - 1][1] if i > 0 else season_days[-1][1]
    return season_days[-1][1]

# Function to convert IRL datetime to World date (precise)
def irl_datetime_to_world_date(irl_datetime):
    delta = irl_datetime - start_date
    total_hours = delta.total_seconds() / 3600
    world_days_passed = total_hours / 3  # Each World day is 3 IRL hours
    world_year = int(world_days_passed // days_in_year) + 1
    world_day_of_year_float = (world_days_passed % days_in_year) + 1
    world_day_of_year_int = int(world_day_of_year_float)
    month_name, day_in_month = get_world_month_day(world_day_of_year_int)
    weekday_index = int(world_days_passed) % 7
    weekday_name = weekdays[weekday_index]
    season = get_season(world_day_of_year_int)
    # Calculate World time (hours and minutes)
    fraction_of_day = world_day_of_year_float - world_day_of_year_int
    world_hours = fraction_of_day * 24  # 24 World hours in a World day
    world_hour = int(world_hours)
    world_minute = int((world_hours - world_hour) * 60)
    return {
        'year': world_year,
        'month': month_name,
        'day': day_in_month,
        'weekday': weekday_name,
        'season': season,
        'world_time': f"{world_hour:02d}:{world_minute:02d}",
    }

# Function to convert World date to IRL datetime (precise)
def world_date_to_irl_datetime(world_year, world_month, day_in_month, world_time_str="00:00"):
    world_day_of_year = get_world_day_of_year(world_month, day_in_month)
    total_world_days_passed = (world_year - 1) * days_in_year + (world_day_of_year - 1)
    # Convert world_time_str to hours and minutes
    try:
        world_hour, world_minute = map(int, world_time_str.split(':'))
    except ValueError:
        world_hour = 0
        world_minute = 0
    fraction_of_day = (world_hour / 24) + (world_minute / 1440)
    total_world_days_passed += fraction_of_day
    total_irl_hours = total_world_days_passed * 3  # Each World day is 3 IRL hours
    irl_datetime = start_date + datetime.timedelta(hours=total_irl_hours)
    return irl_datetime

# Function to find the next n New Year's Eves with precise times
def get_next_new_years_eves(n):
    results = []
    # Get current IRL datetime
    now = datetime.datetime.now()
    # Convert current IRL datetime to total world days passed
    delta = now - start_date
    total_hours = delta.total_seconds() / 3600
    world_days_passed = total_hours / 3
    current_world_year = int(world_days_passed // days_in_year) + 1

    # Starting from the current World year, find the next n New Year's Eves
    for i in range(n):
        world_year = current_world_year + i
        # New Year's Eve is Neo 42
        world_month = "Neo"
        day_in_month = 42
        # Convert World date to IRL datetime
        irl_datetime = world_date_to_irl_datetime(world_year, world_month, day_in_month, "23:59")
        # Convert IRL datetime to UDC Day
        udc_day = irl_datetime_to_udc(irl_datetime)
        results.append({
            'world_year': world_year,
            'irl_datetime': irl_datetime,
            'udc_day': udc_day
        })
    return results

# --- PyQt5 GUI Application ---

class CalendarConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SovereignMc Calendar Converter")
        self.setGeometry(100, 100, 750, 700)  # Increased width by ~30%
        self.initUI()

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Top layout for welcome message and buttons
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # Welcome Message Group Box
        self.welcome_group = QGroupBox("Current Date Conversions")
        self.welcome_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        top_layout.addWidget(self.welcome_group)
        self.initWelcomeMessage()

        # Button Layout (Vertical)
        button_layout = QVBoxLayout()

        # Help Button
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        # About Button
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about)
        button_layout.addWidget(self.about_button)

        # Spacer to push buttons to the top
        button_layout.addStretch()

        # Add button layout to the top layout
        top_layout.addLayout(button_layout)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: UDC to Dates
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "UDC to Dates")
        self.tab1UI()

        # Tab 2: IRL Date to Dates
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, "IRL Date to Dates")
        self.tab2UI()

        # New Tab: World Date to Dates
        self.tab_world_date = QWidget()
        self.tabs.addTab(self.tab_world_date, "World Date to Dates")
        self.tabWorldDateUI()

        # Tab 3: Next New Year's Eves
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab3, "Next New Year's Eves")
        self.tab3UI()

        # Tab 4: Precise IRL Date
        self.tab4 = QWidget()
        self.tabs.addTab(self.tab4, "Precise IRL Date")
        self.tab4UI()

        # Results Display
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        main_layout.addWidget(self.results)

        # Timer to update the welcome message every 10 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateWelcomeMessage)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)

    def initWelcomeMessage(self):
        self.welcome_layout = QVBoxLayout()
        self.welcome_group.setLayout(self.welcome_layout)

        self.welcome_label = QLabel()
        self.welcome_label.setAlignment(Qt.AlignLeft)
        # Increased font size
        font = self.welcome_label.font()
        font.setPointSize(12)  # Adjust the font size as needed
        self.welcome_label.setFont(font)
        self.welcome_label.setTextFormat(Qt.RichText)  # Enable rich text formatting
        self.welcome_layout.addWidget(self.welcome_label)

        self.updateWelcomeMessage()

    def updateWelcomeMessage(self):
        # Get current date conversions
        irl_datetime = datetime.datetime.now()
        udc_day = irl_datetime_to_udc(irl_datetime)
        world_date = irl_datetime_to_world_date(irl_datetime)

        # Prepare welcome message with HTML formatting
        welcome_text = f"""
        <span style='font-size:14pt;'>
        <b><span style='color:#2E8B57;'>IRL Date and Time:</span></b> {irl_datetime.strftime('%B %d, %Y %H:%M:%S')}<br>
        <b><span style='color:#2E8B57;'>UDC Day:</span></b> {udc_day}<br>
        <b><span style='color:#2E8B57;'>World Date:</span></b> Year {world_date['year']}, {world_date['month']} {world_date['day']}, {world_date['weekday']}<br>
        <b><span style='color:#2E8B57;'>Time:</span></b> {world_date['world_time']}<br>
        <b><span style='color:#2E8B57;'>Season:</span></b> {world_date['season']}
        </span>
        """

        self.welcome_label.setText(welcome_text)

    def tab1UI(self):
        layout = QVBoxLayout()
        self.tab1.setLayout(layout)

        self.udc_input = QLineEdit()
        self.udc_input.setPlaceholderText("Enter UDC Day (integer)")
        layout.addWidget(self.udc_input)

        self.udc_button = QPushButton("Convert UDC Day")
        self.udc_button.clicked.connect(self.convert_udc)
        layout.addWidget(self.udc_button)

    def tab2UI(self):
        layout = QVBoxLayout()
        self.tab2.setLayout(layout)

        self.irl_input = QLineEdit()
        self.irl_input.setPlaceholderText("Enter IRL Date (YYYY-MM-DD)")
        layout.addWidget(self.irl_input)

        self.irl_button = QPushButton("Convert IRL Date")
        self.irl_button.clicked.connect(self.convert_irl)
        layout.addWidget(self.irl_button)

    def tabWorldDateUI(self):
        layout = QVBoxLayout()
        self.tab_world_date.setLayout(layout)

        self.world_date_input = QLineEdit()
        self.world_date_input.setPlaceholderText("Enter World Date (YY-MM-DD or YYY-MM-DD)")
        layout.addWidget(self.world_date_input)

        self.world_date_button = QPushButton("Convert World Date")
        self.world_date_button.clicked.connect(self.convert_world_date)
        layout.addWidget(self.world_date_button)

    def tab3UI(self):
        layout = QVBoxLayout()
        self.tab3.setLayout(layout)

        self.nye_button = QPushButton("Show Next 3 New Year's Eves")
        self.nye_button.clicked.connect(self.show_new_years_eves)
        layout.addWidget(self.nye_button)

    def tab4UI(self):
        layout = QVBoxLayout()
        self.tab4.setLayout(layout)

        self.precise_irl_input = QLineEdit()
        self.precise_irl_input.setPlaceholderText("Enter IRL Date and Time (YYYY-MM-DD HH:MM)")
        layout.addWidget(self.precise_irl_input)

        self.precise_irl_button = QPushButton("Convert Precise IRL Date")
        self.precise_irl_button.clicked.connect(self.convert_precise_irl)
        layout.addWidget(self.precise_irl_button)

    def convert_udc(self):
        udc_text = self.udc_input.text()
        try:
            udc_day = int(udc_text)
            irl_datetime = udc_to_irl_datetime(udc_day)
            world_date = irl_datetime_to_world_date(irl_datetime)
            self.display_result(udc_day, irl_datetime, world_date)
        except ValueError:
            self.show_error("Please enter a valid integer for UDC Day.")

    def convert_irl(self):
        date_str = self.irl_input.text()
        try:
            irl_datetime = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            udc_day = irl_datetime_to_udc(irl_datetime)
            world_date = irl_datetime_to_world_date(irl_datetime)
            self.display_result(udc_day, irl_datetime, world_date)
        except ValueError:
            self.show_error("Please enter a valid date in YYYY-MM-DD format.")

    def convert_world_date(self):
        date_str = self.world_date_input.text()
        try:
            # Split the date components
            parts = date_str.strip().split('-')
            if len(parts) != 3:
                raise ValueError("Invalid format")
            year_str, month_str, day_str = parts

            # Parse the year
            if len(year_str) == 2 or len(year_str) == 3:
                world_year = int(year_str)
            else:
                raise ValueError("Year must be 2 or 3 digits")

            # Parse the month and day
            month_int = int(month_str)
            day_in_month = int(day_str)

            # Validate the month
            if month_int < 1 or month_int > len(months):
                raise ValueError("Month must be between 1 and 12")

            # Get the month name and days in the month
            month_name, days_in_month = months[month_int - 1]

            # Validate the day
            if day_in_month < 1 or day_in_month > days_in_month:
                raise ValueError(f"{month_name} has {days_in_month} days")

            # Convert World date to IRL datetime
            irl_datetime = world_date_to_irl_datetime(world_year, month_name, day_in_month)
            udc_day = irl_datetime_to_udc(irl_datetime)
            world_date = irl_datetime_to_world_date(irl_datetime)

            self.display_result(udc_day, irl_datetime, world_date)
        except ValueError as e:
            self.show_error(f"Error parsing World Date: {e}")

    def convert_precise_irl(self):
        datetime_str = self.precise_irl_input.text()
        try:
            irl_datetime = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            udc_day = irl_datetime_to_udc(irl_datetime)
            world_date = irl_datetime_to_world_date(irl_datetime)
            self.display_result(udc_day, irl_datetime, world_date)
        except ValueError:
            self.show_error("Please enter the date and time in YYYY-MM-DD HH:MM format.")

    def show_new_years_eves(self):
        next_new_years_eves = get_next_new_years_eves(3)
        result_text = "<b>Next 3 New Year's Eves in the World Calendar:</b><br><br>"
        for nye in next_new_years_eves:
            irl_datetime_str = nye['irl_datetime'].strftime('%B %d, %Y %H:%M')
            result_text += f"<b>World Year {nye['world_year']}, Neo 42</b><br>"
            result_text += f"IRL Date and Time: {irl_datetime_str}<br>"
            result_text += f"UDC Day: {nye['udc_day']}<br>"
            result_text += "<hr>"
        self.results.setHtml(result_text)

    def display_result(self, udc_day, irl_datetime, world_date):
        result = f"""
        <span style='font-size:12pt;'>
        <b><span style='color:#2E8B57;'>UDC Day:</span></b> {udc_day}<br>
        <b><span style='color:#2E8B57;'>IRL Date and Time:</span></b> {irl_datetime.strftime('%B %d, %Y %H:%M:%S')}<br>
        <b><span style='color:#2E8B57;'>World Date:</span></b> Year {world_date['year']}, {world_date['month']} {world_date['day']}, {world_date['weekday']}<br>
        <b><span style='color:#2E8B57;'>Time:</span></b> {world_date['world_time']}<br>
        <b><span style='color:#2E8B57;'>Season:</span></b> {world_date['season']}<br>
        </span>
        """
        self.results.setHtml(result)

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Input Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def show_help(self):
        help_text = """
        <h2>How to Use the SovereignMc Calendar Converter</h2>
        <p>This program allows you to convert between different date formats used in the SovereignMc Minecraft server.</p>

        <h3>Calendars Explained:</h3>
        <ul>
            <li><b>IRL Date:</b> The real-world date and time.</li>
            <li><b>UDC Day:</b> The Universal Day Count, representing the number of days since the server started (starting from day 1).</li>
            <li><b>World Date:</b> The in-game calendar date, consisting of years, months, days, weekdays, and seasons.</li>
        </ul>

        <h3>World Calendar Details:</h3>
        <ul>
            <li>The World Calendar consists of 12 months with varying numbers of days.</li>
            <li>Each World day equals 3 IRL hours.</li>
            <li>There are 7 weekdays: Lunas, Martis, Adias, Iovis, Helvis, Tunis, Servera.</li>
            <li>The seasons change throughout the year: Spring, Summer, Fall, Winter.</li>
        </ul>

        <h3>Instructions:</h3>
        <p>Select the appropriate tab for the conversion you want to perform, enter the required information, and click the corresponding button. The results will be displayed below the tabs.</p>

        <h3>Example Conversions:</h3>
        <ul>
            <li>Converting UDC Day 100:
                <ul>
                    <li>IRL Date: January 18, 2024</li>
                    <li>World Date: Year 1, Havenox 42, Tunis</li>
                </ul>
            </li>
            <li>Converting IRL Date 2024-07-04:
                <ul>
                    <li>UDC Day: 268</li>
                    <li>World Date: Year 1, Chimpe 25, Martis</li>
                </ul>
            </li>
        </ul>
        """
        help_window = QMessageBox()
        help_window.setWindowTitle("Help")
        help_window.setTextFormat(Qt.RichText)
        help_window.setText(help_text)
        help_window.setStandardButtons(QMessageBox.Ok)
        help_window.exec_()

    def show_about(self):
        about_text = """
        <h2>SovereignMc Calendar Converter</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Author:</b> Ryan</p>
        <p><b>Contact:</b> Discord @ryqm</p>
        <p style="margin-top:20px;"><small>Powered by Akazawa University Technology.</small></p>
        """
        about_window = QMessageBox()
        about_window.setWindowTitle("About")
        about_window.setTextFormat(Qt.RichText)
        about_window.setText(about_text)
        about_window.setStandardButtons(QMessageBox.Ok)
        about_window.exec_()

def main():
    app = QApplication(sys.argv)
    converter = CalendarConverter()
    converter.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

