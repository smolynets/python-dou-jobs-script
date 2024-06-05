import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

current_date = datetime.now()

month_translation = {
    'січня': 'January',
    'лютого': 'February',
    'березня': 'March',
    'квітня': 'April',
    'травня': 'May',
    'червня': 'June',
    'липня': 'July',
    'серпня': 'August',
    'вересня': 'September',
    'жовтня': 'October',
    'листопада': 'November',
    'грудня': 'December'
}

companies = [
    "epam-systems",
    "softserve",
    "luxoft",
    "n-ix",
    "globallogic",
    "zone3000",
    "ukrenergo-digital-solutions",
    "evoplay",
    "ajax-systems",
    "genesis-technology-partners",
    "dataart",
    "sigma-software",
    "eleks",
    "avenga",
    "autodoc",
    "netpeak-group",
    "grid-dynamics",
    "lohika-systems",
    "levi9",
]
last_pub_days = 3

email_subject = "Test HTML Email"
smtp_server = 'smtp.gmail.com'
smtp_port = 587

to_email = "smolynets@gmail.com"
from_email = "smolynets2@gmail.com"
email_app_password = "prem vwaq xlcp knak "  # Replace with your email app password

def send_html_email(email_subject, to_email, from_email, email_app_password, records):
    email_html_body = f"""
    <html>
    <body>
    <h1>{current_date.strftime("%d %B")} - Python Job Vacancies for last {last_pub_days} days</h1>
    <ul>
    """
    for record in records:
        email_html_body += f"<li><strong>{record[0]}</strong></li>\n"
        email_html_body += f"<li><strong>Position:</strong> {record[1]}</li>\n"
        email_html_body += f"<li><strong>Link:</strong> <a href='{record[2]}'>{record[2]}</a></li>\n"
        email_html_body += f"<li><strong>Description:</strong> {record[3]}</li>\n"
        email_html_body += f"<li><strong>Date Posted:</strong> {record[4]}</li>\n"
        email_html_body += "<br>"  # Add a line break between records for better readability
    email_html_body += """
    </ul>
    </body>
    </html>
    """

    # Create the MIME message
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = email_subject

    # Attach the HTML body with UTF-8 encoding
    message.attach(MIMEText(email_html_body, 'html', 'utf-8'))

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Start TLS Encryption
        server.login(from_email, email_app_password)
        server.send_message(message)  # Use send_message to automatically handle encodings

def check_pub_date(vacancy):
    date_div = vacancy.find('div', class_='date')
    date_str = date_div.text if date_div else None
    day, month = date_str.split()
    translated_month = month_translation[month]
    current_year = datetime.now().year
    date_str_english = f"{day} {translated_month} {current_year}"
    date_object = datetime.strptime(date_str_english, '%d %B %Y')
    days_difference = datetime.now() - date_object
    return days_difference > timedelta(days=last_pub_days), date_str

def main(companies):
    records = []
    for company in companies:
        url = f"https://jobs.dou.ua/companies/{company}/vacancies/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the page: {e}")
            exit(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        vacancies_section = soup.find('div', class_='l-items')
        if vacancies_section:
            vacancies = vacancies_section.find_all('li', class_='l-vacancy')
            python_vacancies = [x for x in vacancies if "python" in x.find('a').text.strip().lower()]
            if len(python_vacancies):
                for vacancy in python_vacancies:
                    is_older_than_last_pub_days, date_str = check_pub_date(vacancy)
                    if not is_older_than_last_pub_days:
                        vacancy_record = []
                        vacancy_record.append(f"Company - {company}")
                        title = vacancy.find('a').text.strip()
                        href = vacancy.find('a')["href"]
                        short_desc = vacancy.find('div', class_='sh-info').text.strip()
                        short_desc = short_desc.replace('\xa0', ' ')
                        short_desc = short_desc.replace('\n\n\n', ' ')
                        vacancy_record.append(title)
                        vacancy_record.append(href)
                        vacancy_record.append(short_desc)
                        if date_str:
                            vacancy_record.append(date_str)
                        records.append(vacancy_record)
        else:
            print("Could not find the vacancies section on the page.")
    send_html_email(email_subject, to_email, from_email, email_app_password, records)
    # for record in records:
    #     for line in record:
    #         print(line)
    #     print("\n")

if __name__ == '__main__':
    main(companies)
