import csv
import re
from bot.config import CELI_SITE_URL, BROWSER_DIR, PATH_TO_DUMP, sleep
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


useragent: UserAgent = UserAgent()

options: webdriver.ChromeOptions = webdriver.ChromeOptions()
options.add_argument("--allow-profiles-outside-user-dir")
options.add_argument("--enable-profile-shortcut-manager")
options.add_argument(f"--user-data-dir=./{BROWSER_DIR}")
options.add_argument("--enable-aggressive-domstorage-flushing")
options.add_argument(f"user-agent={useragent.firefox}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")  # without GUI
options.add_argument("--enable-features=UseOzonePlatform")  # support Wayland
options.add_argument("--ozone-platform=wayland")

driver: webdriver.Chrome = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options,
)


def get_companies_count_from_paragraph(paragraph: str) -> int:
    paragraph: str = paragraph.split(" Companies)")[0]  # remove all after count
    count: str = re.findall(r"\b\d+\b", paragraph)[-1]
    return int(count)


def get_cell_from_table(section_num: int | None, index: int, field: int) -> str:
    return driver.find_element(
        By.XPATH,
        f"/html/body/main/article/section[{section_num}]/div/div/div[2]/table/tbody/tr[{index}]/td[{field}]",
    ).get_attribute("innerHTML")


def parse_table(grade: str) -> list[tuple[str, str, str, str, str]]:
    # key is grade, value is number of section
    grades = {
        "F": 2,
        "D": 3,
        "C": 4,
        "B": 5,
        "A": 6,
    }
    section_num: int | None = grades.get(grade)
    paragraph_text = driver.find_element(
        By.XPATH, f"/html/body/main/article/section[{section_num}]/div/div/div[2]/div[1]/p[1]"
    ).get_attribute("innerHTML")
    companies_count: int = get_companies_count_from_paragraph(paragraph_text)
    companies_from_table: list[tuple[str, str, str, str, str]] = []
    for i in range(1, companies_count + 1):
        name: str = get_cell_from_table(section_num, i, 1)
        action: str = get_cell_from_table(section_num, i, 2)
        industry: str = get_cell_from_table(section_num, i, 3)
        country: str = get_cell_from_table(section_num, i, 4)
        print(name, action, industry, country, grade)
        companies_from_table.append((name, action, industry, country, grade))
    return companies_from_table


def save_data_to_scv_file(data_list: list[tuple[str, str, str, str, str]]) -> None:
    with open(PATH_TO_DUMP, "w", newline="", encoding="UTF8") as file:
        writer = csv.writer(file)
        for elem in data_list:
            writer.writerow(elem)
    print("file saved successfully")


def get_yale_celi_list() -> list[tuple[str, str, str, str, str]]:
    result: list[tuple[str, str, str, str, str]] = [
        ("name", "action", "industry", "country", "yaleGrade")
    ]
    driver.get(CELI_SITE_URL)
    sleep(2)
    for grade in ["F", "D", "C", "B", "A"]:
        result += parse_table(grade)
    print("full list received")
    return result


def main() -> None:
    yale_celi_list: list[tuple[str, str, str, str, str]] = get_yale_celi_list()
    save_data_to_scv_file(yale_celi_list)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        driver.close()
        driver.quit()
