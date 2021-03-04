import logging
import os
import keyboard
import time
import datetime
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *

from random import choice

from Database_Bot_Razboi import add_attack_statistics_to_db, get_money_stolen_today


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s:[%(filename)s:%(lineno)d] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.WARNING,
    # filename='logs.txt',
)
logger = logging.getLogger("test_logger")
# logger.info('This will not show up')
# logger.warning('This will.')

PATH = "C:\Program Files (x86)\chromedriver.exe"

option = webdriver.ChromeOptions()
option.add_argument("headless")
driver = webdriver.Chrome(PATH, options=option)

# driver = webdriver.Chrome(PATH)

driver.get("http://www.razboi.ro/r3/index.php")


class ResultsAttack:
    """
    The class for stats of the page after attack
    """

    def __init__(
        self,
        sum_stolen,
        sum_won_total,
        name_attacked_user_name,
        enemy_power_attack_int,
        my_power_attack_int,
    ):
        self.sum_stolen = sum_stolen
        self.sum_won_total = sum_won_total
        self.name_attacked_user_name = name_attacked_user_name
        self.enemy_power_attack_int = enemy_power_attack_int
        self.my_power_attack_int = my_power_attack_int


class User:
    """
    This is the User class that will return information about the user from an attack page
    """

    def __init__(self, link, name, money, position, army):
        self.link = link
        self.name = name  # name.text to get the string of the element
        self.money = money  # is is int  type
        self.position = position
        self.army = army


def time_decorator(func):
    def inner1(*args, **kwargs):
        now_time = time.time()
        func(*args, **kwargs)
        tine_after = time.time()
        print(f"this time passed since this {func} was used{now_time-tine_after}")

    return inner1


class BotRazboi:
    """
    This is the main class that get the elements and all the information form the game pages.
    """

    def __init__(self):
        self.chosen= True
        self.MINIM_ATTACK_SUM = 25000
        self.STILL_ATTACK = True
        self.numar_atacuri = 0
        self.users = []
        self.rezultat = []
        self.attacked_user_position = "300"
        self.my_army = 0
        self.weapon_cost = []
        self.go_forward = True
        self.LIMIT_START_TAKE_ACTION = 100000
        self.available_attacks = 0
        self.total_power_attack = 0
        self.total_power_defence = 0
        self.money_left_on_shop_int = 0
        self.search_and_destroy_activated = False
        self.log_in_false = True
        self.refreshed_pages = 0
        self.this_list = [0, 1, 2, 3]
        self.forbidden_users = (
            []
        )  # list of players that will not be attacked(will be populated
        self.admin_list = [
            "GoDoRoJa",
            "gk",
            "buburuza",
        ]
        self.start_time = time.time()
        self.paused_time = 0
        self.local_datetime_converted_now = "TimeStamp"
        self.total_attack_power_purchased = 0
        self.total_defence_power_purchased = 0
        self.total_money_deposited = 0
        self.numar_atacuri_inceput = 0
        self.total_pillged = 0
        self.number_soldiers = 0
        self.total_money_seif = 0

    def logg_in_error(self):
        log_in_error = driver.find_element_by_xpath(
            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/"
            "tr/td[2]/table/tbody/tr[1]/td/table/tbody/tr[2]/td/font"
        )
        if log_in_error.text == "Nu ai introdus codul corect din imagine!":
            print("Secret code incorrect , please try again!!!! ")
        self.logg_in()

    def logg_in(self):
        """
        Actions that will be made the first time the program will run, log in and take basic information
        """
        try:
            login_id = driver.find_element_by_name("nick")
            pass_id = driver.find_element_by_name("pass")
            cod_secret = driver.find_element_by_name("cod_secret")
            # Pass the Login information
            name_input = input("Please enter your username:")
            pass_input = input("Please enter your password")
            pass_id.send_keys(pass_input)
            login_id.send_keys(name_input)
            driver.get_screenshot_as_file(
                os.path.abspath(os.getcwd()) + r"\Screenshots\loginCAPTCHA.png"
            )
            cod_secret.send_keys(str(input("Type in the secret password: \n"
                                           "The Code can be known by accessing loginCAPTCHA.png "
                                           "from Screenshots folder: \n")))
            pass_id.send_keys(Keys.ENTER)
            self.get_stats_from_user_page()
            self.log_in_false = False
            # my_id = driver.find_elements_by_link_text("id=85")
        except TimeoutException:
            self.log_in_false = True
            self.logg_in_error()
        except NoSuchElementException:
            self.click_camp_de_lupta()

    def get_stats_from_user_page(self):
        """
        Get the logged in user army size
        """
        self.click_status_b()
        army_size = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td/center/"
                "p/table/tbody/tr/td/table[2]/tbody/tr[3]/td[2]/p/span/font"
            )
        )
        nr_attacks = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                "tr[6]/td/center/p/table/tbody/tr/td/table[2]/tbody/tr[6]/td[2]/p/span/font"
            )
        )
        total_power = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                "tr[6]/td/center/p/table/tbody/tr/td/table[2]/tbody/tr[8]/td[2]/p/span/font"
            )
        )
        number_soldiers = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td/center/"
                "p/table/tbody/tr/td/table[2]/tbody/tr[3]/td[2]/p/span/font"
            )
        )
        total_money_seif = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td/center/"
                "p/table/tbody/tr/td/table[2]/tbody/tr[4]/td[2]/p/b[2]/span/font"
            )
        )
        self.my_army = int(army_size.text.split()[0])
        self.available_attacks = int(nr_attacks.text.split("/")[0])
        self.total_power_attack = int(total_power.text.split("/")[0])
        self.total_power_defence = int(total_power.text.split("/")[1])
        self.number_soldiers = int(number_soldiers.text.split()[0])
        self.total_money_seif = int(total_money_seif.text.split()[0])

        self.click_camp_de_lupta()
        print(
            f"The total Power Attack is               :{self.total_power_attack} \n"
            f"The total Power Defence is              :{self.total_power_defence} \n"
            f"The number of soldiers is               :{self.number_soldiers} \n"
            f"The money deposited in seif is          :{self.total_money_seif} \n"
            f"Total Number of attacks available :     :{self.available_attacks}"
        )

    def add_forbidden_user(self, x):
        """
        When a player should not be attacked this method will add it to the forbidden players list
        """
        if x not in self.forbidden_users:
            with open("forbidden_users.txt", "a+") as f_file:
                f_file.write(f"{x}\n")
                self.forbidden_users.append(x)
            f_file.close()
        else:
            pass

    def populate_forbidden_users(self):

        with open("forbidden_users.txt", "r+") as f_file:
            for f in f_file:
                self.forbidden_users.append(f[:-1])
            f_file.close()

    def get_time_stamp(self):

        self.local_datetime_converted_now = datetime.datetime.today()

    def add_attack_statistics_to_db(self):
        now_time = str(datetime.datetime.now())
        attack_statistics_to_db = add_attack_statistics_to_db(
            self.rezultat.name_attacked_user_name,
            self.rezultat.sum_stolen,
            self.rezultat.sum_won_total,
            self.rezultat.enemy_power_attack_int,
            self.rezultat.my_power_attack_int,
            now_time,
        )
        return attack_statistics_to_db

    def get_first_user_army_size(self):
        """
        This will return the first player army size
        """
        first_user_on_page_army_size = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td/table/tbody/"
                "tr/td/table/tbody/tr[2]/td[3]/p/span/font"
            )
        )
        return int(first_user_on_page_army_size.text)

    def click_pagina_urmatoare(self):
        """
        Will move to the next page of users
        """
        go_to_next_page = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                "tr[9]/td/table/tbody/tr/td[3]/p[2]/b/span/a"
            )
        )
        print(
            "Page Moved to lower Positions>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        )
        go_to_next_page.click()

    def click_pagina_precedenta(self):
        """
        Will move to the previous page
        """
        go_to_next_page = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                (
                    "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                    "tr[9]/td/table/tbody/tr/td[1]/p/b/span/a"
                )
            )
        )
        print(
            "Page was moved to higher positions <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        )
        go_to_next_page.click()

    def click_status_b(self):
        """
        Will click and move on the page with logged in player statistics
        """
        status_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[2]/td/a"
            )
        )
        status_b.click()

    def click_date_personale_b(self):
        """
        Will move to page with personal data of player
        """
        date_personale_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[3]/td/a"
            )
        )
        date_personale_b.click()

    def click_camp_de_lupta(self):
        """
        Will move to page of players that can be attacked
        """
        camp_de_lupta_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[4]/td/a"
            )
        )
        camp_de_lupta_b.click()

    def click_atacurile_mele_b(self):
        """
        Will move to the page where we can see the attacks made so far
        """
        atacurile_mele_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[5]/td/a"
            )
        )
        atacurile_mele_b.click()

    def click_atacuri_asupra_mea_b(self):
        """
        Will move to the page where we can see the attacks made so far on the logged in user
        """
        atacuri_asupra_mea_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[6]/td/a"
            )
        )
        atacuri_asupra_mea_b.click()

    def click_magazin_but(self):
        """
          Will move to the page where you can buy items
        """
        magazin_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/"
                "tr[1]/td/table/tbody/tr/td[2]/table/tbody/tr[7]/td/a"
            )
        )
        magazin_b.click()

    def click_seif_but(self):
        """
          Will move to the seif page
        """
        seif_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[8]/td/a"
            )
        )
        seif_b.click()

    def click_loto_b(self):
        """
          Will move to the loto page
        """
        loto_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[9]/td/a"
            )
        )
        loto_b.click()

    def click_upgrade_b(self):
        """
          Will move to the page where you can purchase upgrades
        """
        upgrade_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[10]/td/a"
            )
        )
        upgrade_b.click()

    def click_aliati_b(self):
        """
          Will move to the page of allies if you are on an alliance
        """
        aliati_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[11]/td/a"
            )
        )
        aliati_b.click()

    def click_aliante_b(self):
        """
          Will move to the page where you can see all the alliances of the game
        """
        aliante_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[10]/td/a"
            )
        )
        aliante_b.click()

    def click_atacaurile_noastre_b(self):
        """
          Will move to the page  where you can see the attacks of the aliance
        """
        atacurile_noastre_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[13]/td/a"
            )
        )
        atacurile_noastre_b.click()

    def click_atacuri_asupra_noastra_b(self):
        """
        Will move to the page  where you can see the attacks of other alliances on your alliance
        """
        atacuri_asupra_noastra_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[14]/td/a"
            )
        )
        atacuri_asupra_noastra_b.click()

    def click_buncar_alianta(self):
        """
        Will move to the page  where is the vault of the alliance
        """
        buncar_alianta_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[15]/td/a"
            )
        )
        buncar_alianta_b.click()

    def click_top_b(self):
        """
        Will move to the page where you can see the top players
        """
        top_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[16]/td/a"
            )
        )
        top_b.click()

    def click_log_out_b(self):
        """
        Will log out the user
        """
        log_out_b = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/"
                "tr/td[2]/table/tbody/tr[16]/td/a"
            )
        )
        log_out_b.click()

    def set_start_position(self):
        option_to_select = input("Select the position you would like to move to : \n")
        if option_to_select == keyboard.is_pressed("space"):
            self.click_camp_de_lupta()
            self.get_user_field_elements()  # call populate with user elements and stats
        else:
            go_to_position = WebDriverWait(driver, 2).until(
                lambda x: x.find_element_by_xpath(
                    "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                    "tr[3]/td/table/tbody/tr[3]/td[1]/input[2]"
                )
            )
            go_to_position.send_keys(int(option_to_select))
            go_to_position.send_keys(Keys.ENTER)
            self.get_user_field_elements()
            driver.get_screenshot_as_file(
                os.path.abspath(os.getcwd()) + r"\Screenshots\players_page.png"
            )

    def click_button_attack_user(self):
        """
        Will click the attack button from a user page
        """

        button_attack = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/"
                "tbody/tr/td[2]/table/tbody/tr[12]/td/center/p/table/"
                "tbody/tr[4]/td/p/input"
            )
        )

        button_attack.click()

    def get_attack_statistics(self):
        """
        Will get the details of the the page after the attack of a player.
        """
        my_power_attack = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/"
                "tbody/tr/td[2]/table[2]/tbody/tr[3]/td/font/b[2]"
            )
        )
        power_attack_enemy = WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/"
                "tbody/tr/td[2]/table[2]/tbody/tr[3]/td/font/b[3]"
            )
        )
        attacked_user_name = WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/"
                "tr/td[2]/table[2]/tbody/tr[3]/td/font/b[1]"
            )
        )
        suma_castigata_elem = WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/"
                "tr/td[2]/table[2]/tbody/tr[3]/td/font/center/font/font/font/b"
            )
        )
        suma_furata_elem = WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/"
                "tr/td[2]/table[2]/tbody/tr[3]/td/font/center/font/b[1]"
            )
        )
        sum_stolen = int(suma_furata_elem.text.split()[0])
        sum_won_total = int(suma_castigata_elem.text.split()[0])
        name_attacked_user_name = str(attacked_user_name.text)
        enemy_power_attack_int = int(power_attack_enemy.text)
        my_power_attack_int = int(my_power_attack.text)
        self.rezultat = ResultsAttack(
            sum_stolen,
            sum_won_total,
            name_attacked_user_name,
            enemy_power_attack_int,
            my_power_attack_int,
        )

    def buy_weapons_defence(self):
        """
        Will buy the most expensive defence weapon
        """
        self.click_magazin_but()
        hummer_blindat = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_name("arma12")
        )
        hummer_blindat.send_keys("1")
        hummer_blindat.send_keys(Keys.ENTER)
        print(
            "******************************************************** A Hummer blindat has been purchased!"
        )
        driver.back()
        driver.back()
        driver.back()
        driver.back()

    def buy_weapons_attack(self):
        """
        Will purchase the most expensive attack weapon
        """
        self.click_magazin_but()
        hummer_blindat = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_name("arma6")  # arma 5 = 100
        )
        hummer_blindat.send_keys("1")
        hummer_blindat.send_keys(Keys.ENTER)
        print(
            "****************************************************** A Bazooka weapon has been purchased"
        )
        driver.back()
        driver.back()
        driver.back()
        driver.back()

    def add_to_seif(self):
        """
        Will add to vault(seif) the sum decided.
        """
        self.click_seif_but()
        to_be_added_in_vault = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_name("suma")
        )
        to_be_added_in_vault.send_keys(self.LIMIT_START_TAKE_ACTION)
        to_be_added_in_vault.send_keys(Keys.ENTER)
        print(
            f"*************************************************** You deposited     {self.LIMIT_START_TAKE_ACTION} "
        )
        self.total_money_deposited += self.LIMIT_START_TAKE_ACTION
        driver.back()
        driver.back()
        driver.back()
        driver.back()

    def get_weapon_cost(self):
        """
        Will get the cost of weapons that can be purchased
        """
        self.click_magazin_but()
        for i in range(2, 15):
            name_weapon = WebDriverWait(driver, 5).until(
                lambda x: x.find_element_by_xpath(
                    f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                    f"tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[{i}]/td[1]/p/b/span/font"
                )
            )
            type_bonus = WebDriverWait(driver, 5).until(
                lambda x: x.find_element_by_xpath(
                    f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                    f"tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]/p/span/font"
                )
            )
            price_weapon = WebDriverWait(driver, 5).until(
                lambda x: x.find_element_by_xpath(
                    f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                    f"tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[{i}]/td[3]/p/span/font"
                )
            )
            quantity_to_purchase = WebDriverWait(driver, 5).until(
                lambda x: x.find_element_by_xpath(
                    f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                    f"tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/center/p/input"
                )
            )
            purchased_already_quantity = WebDriverWait(driver, 5).until(
                lambda x: x.find_element_by_xpath(
                    f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[6]/td/center/"
                    f"p/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]/p/span/font"
                )
            )
            type_bonus_str = str(type_bonus.text)
            name_weapon_str = str(name_weapon.text)
            price_weapon_int = int(price_weapon.text)
            self.weapon_cost.append(
                (
                    name_weapon_str,
                    type_bonus_str,
                    price_weapon_int,
                    quantity_to_purchase,
                    purchased_already_quantity,
                )
            )
        self.click_camp_de_lupta()

    def get_money_left_on_shop(self):
        money_left_elem = WebDriverWait(driver, 5).until(
            lambda x: x.find_element_by_xpath(
                "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/tr[13]/td/p/b[2]/span/font"
            )
        )
        money = int(money_left_elem.text.split()[0])
        self.money_left_on_shop_int = money

    def change_amount_deposited(self):
        """
        Will change the sum of money that can be added to vault(seif).
        """
        amount_chosen = input(
            "How much money do you like to put on vault(seif) on one entrance? \n"
        )
        self.LIMIT_START_TAKE_ACTION = int(amount_chosen)
        print(
            f"The new deposited amount is:                                          {str(amount_chosen)}"
        )

    def default_option(self):
        """
        Set the default weapons to buy and cost.
        """
        self.LIMIT_START_TAKE_ACTION = int(self.weapon_cost[12][2])
        print(f"Limit to buy has been set to default {self.LIMIT_START_TAKE_ACTION}")

        self.chosen = self.buy_weapons_defence

    def attack_user(self, attacked_user):
        """
        This will take all actions to attack an user and print in console details of the attack
        """
        attacked_user.link.click()
        logger.info("Click an user")
        try:
            try:
                self.click_button_attack_user()
                logger.info("Click attack an user")
            except NoSuchElementException:
                self.add_forbidden_user(attacked_user.name)
            except StaleElementReferenceException:
                self.click_camp_de_lupta()
            self.numar_atacuri -= 1
            print("Remaining attacks:       " + str(self.numar_atacuri))

            self.get_attack_statistics()

            print(
                f"You attacked {self.rezultat.name_attacked_user_name} with "
                f" >>>{self.rezultat.my_power_attack_int}<<< Power and he defended himself"
                f" with >>>{self.rezultat.enemy_power_attack_int}<<< Power"
            )
            print(
                f"                                   You gain:                 {self.rezultat.sum_stolen}\n"
                f"                      You now have in total:                 {self.rezultat.sum_won_total}"
            )
            self.total_pillged += self.rezultat.sum_stolen
            self.add_attack_statistics_to_db()
            sum_to_deposit = 525000
            if self.rezultat.my_power_attack_int > self.rezultat.enemy_power_attack_int:
                logger.info("checked if attack power bigger")
                print(self.rezultat.name_attacked_user_name + "was successful attacked")
                while self.rezultat.sum_stolen > 250000 and (
                    attacked_user.money - self.rezultat.sum_stolen > 150000
                ):
                    attacked_user.money -= self.rezultat.sum_stolen
                    print(
                        f"Money left on {attacked_user.name} after attack: {str(attacked_user.money)}"
                    )
                    driver.refresh()
                    print(
                        "You stolen more then 100.000 WEU, you will refresh the page, attack"
                    )
                    self.get_attack_statistics()
                    self.add_attack_statistics_to_db()
                    print(
                        f"You attacked {self.rezultat.name_attacked_user_name} with "
                        f" >>>{self.rezultat.my_power_attack_int}<<< Power and he defended himself"
                        f" with >>>{self.rezultat.enemy_power_attack_int}<<< Power"
                    )
                    print(
                        f"                                   You gain:                 {self.rezultat.sum_stolen}\n"
                        f"                      You now have in total:                 {self.rezultat.sum_won_total}"
                    )
                    self.numar_atacuri -= 1
                    self.total_pillged += self.rezultat.sum_stolen
                    print(
                        f"YOu stolen after refresh:              {self.rezultat.sum_stolen}"
                    )
                    self.search_and_destroy()
                if self.search_and_destroy_activated:
                    logger.info("checked if search and destroy acctivated")

                    if self.rezultat.sum_won_total > int(sum_to_deposit):
                        logger.info(f"checked if sum bigger then {str(sum_to_deposit)}")
                        self.LIMIT_START_TAKE_ACTION = (
                            self.rezultat.sum_won_total - random.randint(1026, 3983)
                        )
                        self.add_to_seif()

                    elif self.rezultat.sum_won_total >= self.weapon_cost[10][2]:
                        logger.info("checked if sum bigger then [10][2]")
                        self.search_and_destroy()
                    elif self.rezultat.sum_won_total < self.weapon_cost[10][2]:
                        logger.info("checked if sum smaller then [10][2]")
                        print(
                            f"You attacked {self.rezultat.name_attacked_user_name} with "
                            f" >>>{self.rezultat.my_power_attack_int}<<< Power and he defended himself"
                            f" with >>>{self.rezultat.enemy_power_attack_int}<<< Power"
                        )
                        print("You did not steeled enough to make a difference.")
                        self.total_pillged += self.rezultat.sum_stolen
                        self.search_and_destroy()
                    else:
                        logger.info("go back 2 times after checking attack")
                        driver.back()
                        driver.back()

                else:
                    if self.rezultat.sum_won_total > self.LIMIT_START_TAKE_ACTION:
                        logger.info("If search and destroy not active")
                        self.chosen()
                    else:

                        driver.back()
                        driver.back()

            elif (
                self.rezultat.my_power_attack_int * 134 / 100
                <= self.rezultat.enemy_power_attack_int
            ):
                logger.info(
                    "elif self.rezultat.my_power_attack_int * 134 / 100"
                    " <= self.rezultat.enemy_power_attack_int:"
                )
                self.get_time_stamp()
                self.add_attack_statistics_to_db()
                print(
                    f"You attacked {self.rezultat.name_attacked_user_name} with "
                    f" >>> {self.rezultat.my_power_attack_int} <<< Power and he defended himself"
                    f" with >>> {self.rezultat.enemy_power_attack_int} <<< Power"
                )
                print(
                    f"                                   You gain:                 {self.rezultat.sum_stolen}\n"
                    f"                      You now have in total:                 {self.rezultat.sum_won_total}"
                )
                print(
                    f" The attack on {self.rezultat.name_attacked_user_name} has FAILED!"
                )
                driver.refresh()
                print(
                    f" The attack on {self.rezultat.name_attacked_user_name} Has been repeated"
                )
                self.get_attack_statistics()
                if (
                    self.rezultat.my_power_attack_int
                    > self.rezultat.enemy_power_attack_int
                ):
                    logger.info(
                        "self.rezultat.my_power_attack_int > self.rezultat.enemy_power_attack_int:"
                    )
                    print(
                        self.rezultat.name_attacked_user_name
                        + "was successful attacked"
                    )
                    while self.rezultat.sum_stolen > 250000 and (
                            attacked_user.money - self.rezultat.sum_stolen > 150000
                    ):
                        logger.info(
                            "while self.rezultat.sum_stolen > 100000 and ( \
                            attacked_user.money - self.rezultat.sum_stolen > 100000"
                        )
                        attacked_user.money -= self.rezultat.sum_stolen
                        print(
                            f"Money left on {attacked_user.name} after attack: {str(attacked_user.money)}"
                        )
                        driver.refresh()
                        self.numar_atacuri -= 1
                        print(
                            "You stollen more then 100.000 WEU, you will refresh the page, attack"
                        )
                        self.get_attack_statistics()
                        self.total_pillged += self.rezultat.sum_stolen
                        self.add_attack_statistics_to_db()
                        self.total_pillged += self.rezultat.sum_stolen

                        print(
                            f"You attacked {self.rezultat.name_attacked_user_name} with "
                            f" >>> {self.rezultat.my_power_attack_int} <<< Power and he defended himself"
                            f" with >>> {self.rezultat.enemy_power_attack_int} <<< Power"
                        )
                        print(
                            f"                                   You gain:                 {self.rezultat.sum_stolen}\n"
                            f"                      You now have in total:                 {self.rezultat.sum_won_total}"
                        )
                        self.search_and_destroy()
                    if self.search_and_destroy_activated:
                        if self.rezultat.sum_won_total > self.sum_to_deposit:
                            logger.info(
                                "if self.rezultat.sum_won_total > 320000: and search and destroy active"
                            )
                            self.LIMIT_START_TAKE_ACTION = (
                                self.rezultat.sum_won_total
                                - random.randint(1026, 13983)
                            )
                            self.add_to_seif()
                        elif self.rezultat.sum_won_total > self.weapon_cost[10][2]:
                            self.search_and_destroy()
                        else:
                            driver.back()
                            driver.back()
                    else:
                        if self.rezultat.sum_won_total > self.LIMIT_START_TAKE_ACTION:

                            self.chosen()
                        else:
                            if self.search_and_destroy_activated:
                                self.search_and_destroy()
                            else:
                                driver.back()
                                driver.back()
                elif (
                    self.rezultat.my_power_attack_int * 134 / 100
                    <= self.rezultat.enemy_power_attack_int
                ):
                    logger.info(
                        "elif self.rezultat.my_power_attack_int * 134 / 100 "
                        "<= self.rezultat.enemy_power_attack_int:"
                    )
                    print(
                        f"You attacked {self.rezultat.name_attacked_user_name} with "
                        f" >>> {self.rezultat.my_power_attack_int} <<< Power and he defended himself"
                        f" with >>> {self.rezultat.enemy_power_attack_int} <<< Power"
                    )
                    print(
                        f"                                   You gain:               {self.rezultat.sum_stolen}\n"
                        f"                      You now have in total:               {self.rezultat.sum_won_total}"
                    )
                    print(
                        f" The attack on {self.rezultat.name_attacked_user_name} has FAILED!"
                    )
                    driver.refresh()
                    self.numar_atacuri -= 1
                    self.get_attack_statistics()
                    print(
                        f"You attacked {self.rezultat.name_attacked_user_name} with "
                        f" >>> {self.rezultat.my_power_attack_int} <<< Power and he defended himself"
                        f" with >>> {self.rezultat.enemy_power_attack_int} <<< Power"
                    )
                    print(
                        f"                                   You gain:                 {self.rezultat.sum_stolen}\n"
                        f"                      You now have in total:                 {self.rezultat.sum_won_total}"
                    )
                    self.add_attack_statistics_to_db()
                    self.total_pillged += self.rezultat.sum_stolen
                    self.search_and_destroy()
                else:
                    self.add_forbidden_user(self.rezultat.name_attacked_user_name)
                    print(
                        f"The attack on  <<< {self.rezultat.name_attacked_user_name} >>> "
                        f"has FAILED and he was added to"
                        f" the list of the people you don't attack <><><><><><><><><><><"
                    )
                driver.back()
                driver.back()
            else:
                logger.info("go back 2 times")
                driver.back()
                driver.back()

        except TimeoutException:
            self.click_camp_de_lupta()  # Imp

    def move_to_next_page(self):
        """
        This is a function that takes a decision to move forward or backwards on the field with players to be attacked.
        """
        try:
            first_user = self.users[0]
            last_user = self.users[29]
            print(
                f"No users meeting the requirements found on this page from position: "
                f" {str(first_user.position)} to position {str(last_user.position)}, switch to next Page >"
            )
            if self.go_forward:
                if last_user.army >= self.my_army // 3:
                    if last_user.army <= self.my_army * 3:
                        self.click_pagina_urmatoare()
                        self.get_user_field_elements()
                    elif last_user.army <= self.my_army // 3:
                        self.click_pagina_precedenta()
                        self.get_user_field_elements()
                        self.go_forward = False
                elif last_user.army <= self.my_army // 3:
                    self.click_pagina_precedenta()
                    self.get_user_field_elements()
                    self.go_forward = False
            elif not self.go_forward:
                if last_user.army >= self.my_army // 3:
                    if first_user.army <= self.my_army * 3:
                        try:
                            self.click_pagina_precedenta()
                            self.get_user_field_elements()
                        except TimeoutException:
                            self.click_pagina_urmatoare()
                            self.get_user_field_elements()
                            self.go_forward = True
                    elif first_user.army >= self.my_army * 3:
                        self.click_pagina_urmatoare()
                        self.get_user_field_elements()
                        self.go_forward = True
        except IndexError:
            self.click_camp_de_lupta()

    def attack_player_with_most_money(self):
        """
        Will sort the players after the amount of money they have (must be bigger then the minimum decided ).
        If list is empty it will move to another page.
        If list is not empty the player with the highest amount will be attacked.
        """
        # pip(1)
        self.repopulate_users_on_new_page()
        lista_bani = []
        most_money_list = []
        for user in self.users:
            if user.name not in self.forbidden_users:
                most_money_list.append(user.money)
                if self.search_and_destroy_activated:
                    if user.money > self.MINIM_ATTACK_SUM + random.randint(10, 38000):
                        if int(self.my_army // 3) <= user.army <= (self.my_army * 3):
                            lista_bani.append(user.money)
                            lista_bani.sort()
                else:
                    if user.money > self.MINIM_ATTACK_SUM:
                        if int(self.my_army // 3) <= user.army <= (self.my_army * 3):
                            lista_bani.append(user.money)
                            lista_bani.sort()
            elif user.name in self.forbidden_users and user.name not in self.admin_list:
                if user.money > self.MINIM_ATTACK_SUM:
                    print(
                        f"<<< {user.name} >>> is in forbidden user and cannot be attacked, he have"
                        f"    {str(user.money)} WEU"
                    )
                    if self.search_and_destroy_activated:
                        self.get_time_stamp()
        if len(lista_bani) == 0:
            print(
                f"Most money on page: {max(most_money_list)}, Minimum to attack: {self.MINIM_ATTACK_SUM}, "
                f"Attacks made so far: {str(self.numar_atacuri_inceput - self.numar_atacuri)} left"
                f" {self.numar_atacuri}"
            )
            self.refreshed_pages += 1
            elapsed_time = time.time() - self.start_time
            print(
                f"Next Page. Refreshed {self.refreshed_pages} times. "
                f"Paused: {str(datetime.timedelta(seconds=self.paused_time))}",
                f'Game running for {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))}',
            )

            while keyboard.is_pressed("CTRL+SPACE"):
                run.roll_on()
            else:
                if self.search_and_destroy_activated:
                    print(
                        f"You gained:  {self.total_attack_power_purchased} / {self.total_defence_power_purchased} POWER"
                        f" and {self.total_money_deposited} "
                        f"deposited from total of {self.total_pillged} stolen."
                    )
                    print("-" * 70)
                    if self.refreshed_pages % 725 == 0:
                        now = datetime.datetime.now()
                        to_be_paused = choice(
                            [632, 423, 923, 523, 723, 493, 723, 456, 713, 533]
                        )
                        print(
                            f"Game will be paused (BIG PAUSE) for {to_be_paused} seconds from {str(now)}"
                        )
                        self.paused_time += int(to_be_paused)
                        print(
                            f"After Pause ends, total paused time will be  "
                            f":  {str(datetime.timedelta(seconds=self.paused_time))}"
                        )
                        self.get_stats_from_user_page()
                        driver.back()
                        driver.back()
                        time.sleep(to_be_paused)
                    elif self.refreshed_pages % 123 == 0:
                        now = datetime.datetime.now()
                        x = choice([182, 90, 62, 120, 146, 81, 120, 201, 73])
                        print(f"Game will be paused for {x} seconds")
                        self.paused_time += int(x)
                        print(
                            f"Game will be paused for {x} seconds from {str(now)}"
                        )
                        print(
                            f"After Pause ends, total paused time will be  "
                            f":  {str(datetime.timedelta(seconds=self.paused_time))}"
                        )
                        time.sleep(x)

                    for i in self.this_list:
                        if i == 0:
                            logger.info("Check if first page")
                            driver.switch_to.window(driver.window_handles[1])
                            driver.refresh()
                            self.this_list.remove(0)
                            break
                        elif i == 1:
                            logger.info("Check if second page")
                            driver.switch_to.window(driver.window_handles[2])
                            driver.refresh()
                            self.this_list.remove(1)
                            break
                        elif i == 2:
                            logger.info("Check if 3 page")
                            driver.switch_to.window(driver.window_handles[3])
                            driver.refresh()
                            self.this_list.remove(2)
                            break
                        elif i == 3:
                            logger.info("Check if 4 page")
                            driver.switch_to.window(driver.window_handles[0])
                            driver.refresh()
                            # self.this_list.remove(3)
                            self.this_list = [0, 1, 2, 3]
                            break

                        #     break
                        # elif i == 4:
                        #     logger.info("Check if 5 page")
                        #     driver.switch_to.window(driver.window_handles[0])
                        #     driver.refresh()

                    pass
                else:
                    self.move_to_next_page()
        else:
            print(f"There ware users that have money above the limit : {lista_bani}")
            for user in self.users:
                if user.money == lista_bani[-1]:
                    print(
                        " User "
                        + user.name
                        + " with this money will be attacked      :"
                        + str(user.money)
                    )
                    attacked_user = user
                    self.attacked_user_position = str(user.position)
                    self.attack_user(attacked_user)

    def print_users(self):
        """
        Will print the list of users in a field.
        """
        for user in self.users:
            try:
                print(
                    str(user.position)
                    + "."
                    + " Player name: "
                    + str(user.name)
                    + " soldiers: "
                    + str(user.army)
                    + " Total Money: "
                    + str(user.money)
                    + "\n"
                )
            except AttributeError:
                print("Attribute error")

    def attack_users_on_page(self):
        """
        This is the function that start to attack players after decided if there are still attacks left
        """
        try:
            self.MINIM_ATTACK_SUM = int(input("Enter the minim attack sum: \n"))
            self.numar_atacuri = int(input("Number of attacks: \n"))
            self.numar_atacuri_inceput = self.numar_atacuri
            print("The number of total attacks is " + str(self.numar_atacuri))
            print(
                "The players will be attacked only if they have more then: "
                + str(self.MINIM_ATTACK_SUM)
            )
            while keyboard.is_pressed("CTRL+SPACE"):
                self.roll_on()
            else:
                def use_all_attacks():
                    while self.numar_atacuri > 0:
                        if self.STILL_ATTACK:
                            self.attack_player_with_most_money()
                        else:
                            print("Attacks had been completed, stopped!")
                            self.roll_on()
                            self.repopulate_users_on_new_page()
                            self.STILL_ATTACK = False

                use_all_attacks()

            print("Attacks are over, you must start again.")
            self.get_stats_from_user_page()
            self.roll_on()
        except ValueError:
            self.roll_on()

    def search_and_destroy(self):
        self.click_magazin_but()
        self.get_money_left_on_shop()
        power_purchased_this_attack = 0
        while self.money_left_on_shop_int > self.weapon_cost[10][2]:
            if self.total_power_attack <= self.total_power_defence + 20000:
                while self.money_left_on_shop_int >= self.weapon_cost[6][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[8]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_attack_power_purchased += 150
                    power_purchased_this_attack += 150
                    print("You purchased a REALLY BIG attack weapon")
                    self.get_money_left_on_shop()
                while self.money_left_on_shop_int >= self.weapon_cost[5][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[7]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_attack_power_purchased += 100
                    power_purchased_this_attack += 100
                    print("You purchased a Big attack weapon")
                    self.get_money_left_on_shop()
                while self.money_left_on_shop_int >= self.weapon_cost[4][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[6]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_attack_power_purchased += 50
                    power_purchased_this_attack += 50
                    print("You purchased a Medium attack weapon")
                    self.get_money_left_on_shop()
                while self.money_left_on_shop_int >= self.weapon_cost[3][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[5]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_attack_power_purchased += 20
                    power_purchased_this_attack += 20
                    print("You purchased a Small attack weapon")
                    self.get_money_left_on_shop()
                while self.money_left_on_shop_int >= self.weapon_cost[2][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[4]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_attack_power_purchased += 8
                    power_purchased_this_attack += 8
                    print("You purchased a Very Small attack weapon!")
                    self.get_money_left_on_shop()
                print("You purchased ATTACK WEAPONS!")

            elif self.total_power_attack > self.total_power_defence + 20000:
                while self.money_left_on_shop_int >= self.weapon_cost[12][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[14]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_defence_power_purchased += 100
                    power_purchased_this_attack += 100
                    print("You purchased a BIG DEFENCE weapon")
                    self.get_money_left_on_shop()
                while self.money_left_on_shop_int >= self.weapon_cost[11][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[13]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_defence_power_purchased += 50
                    power_purchased_this_attack += 50
                    print("You purchased a Medium DEFENCE weapon")
                    self.get_money_left_on_shop()
                while self.money_left_on_shop_int >= self.weapon_cost[10][2]:
                    quantity_to_purchase = WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[12]/td/center/p/table/tbody/tr/td/table/tbody/tr[12]/td[4]/center/p/input"
                        )
                    )
                    quantity_to_purchase.send_keys("1")
                    quantity_to_purchase.send_keys(Keys.ENTER)
                    self.total_defence_power_purchased += 20
                    power_purchased_this_attack += 20
                    print("You purchased a Small DEFENCE weapon")
                    self.get_money_left_on_shop()
                print("You purchased DEFENCE WEAPONS!")
        print(
            f" You gained from this attack :       {power_purchased_this_attack} POWER"
        )
        print(f"You have left on yourself       {self.money_left_on_shop_int} Money")
        driver.get(
            f"http://www.razboi.ro/r3/index.php?shpg=9&go={str(self.attacked_user_position)}"
        )

    def preferred_option(self):
        """
        Will let you decide what you wanna buy with the money you get from attacks
        """
        optiune = str(
            input(
                "Select what you would like to change:  \n"
                "Type           *** a ***           to buy attack weapons \n"
                "Type           *** d ***           to buy defence weapons \n"
                "Type           *** s ***           will change the amount deposited \n"
            )
        )
        if optiune == "a":
            print("You will now start buy Attack Weapons!!!")
            self.LIMIT_START_TAKE_ACTION = self.weapon_cost[6][2]
            self.chosen = self.buy_weapons_attack
        if optiune == "d":
            self.LIMIT_START_TAKE_ACTION = self.weapon_cost[12][2]
            self.chosen = self.buy_weapons_defence
            print("You will now start buy Defence Weapons!!!")
        if optiune == "s":
            self.change_amount_deposited()
            print("You will now Deposit the amount on the vault!!!")
            self.chosen = self.add_to_seif
        self.roll_on()

    def get_user_field_elements(self):
        """
        Will get the list of players in the game
        """
        for i in range(2, 32):
            try:
                user_link = WebDriverWait(driver, 2).until(
                    lambda x: x.find_element_by_xpath(
                        f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                        f"tr[6]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]/p[2]/b/span/a"
                    )
                )
                user_money = WebDriverWait(driver, 2).until(
                    lambda x: x.find_element_by_xpath(
                        f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                        f"tr[6]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[4]/p[2]/span/font"
                    )
                )
                user_position = WebDriverWait(driver, 2).until(
                    lambda x: x.find_element_by_xpath(
                        f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                        f"tr[6]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[1]/p/span/font"
                    )
                )
                user_army = WebDriverWait(driver, 2).until(
                    lambda x: x.find_element_by_xpath(
                        f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                        f"tr[6]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[3]/p/span/font"
                    )
                )
                user_name = WebDriverWait(driver, 2).until(
                    lambda x: x.find_element_by_xpath(
                        f"/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                        f"tr[6]/td/table/tbody/tr/td/table/tbody/tr[{i}]/td[2]/p[2]/b/span/a/font"
                    )
                )
                user_money_nr = int(user_money.text.split()[0])
                user_name_str = user_name.text
                user_position_nr = int(user_position.text)
                user_army_nr = int(user_army.text)
                user = User(
                    user_link,
                    user_name_str,
                    user_money_nr,
                    user_position_nr,
                    user_army_nr,
                )

                self.users.append(user)
            except TimeoutException:
                self.roll_on()
            except StaleElementReferenceException:
                self.roll_on()
            except NoSuchWindowException:
                self.roll_on()

    def repopulate_users_on_new_page(self):
        """
        Will clear the least of players from the last page and populate it with the new one
        """
        self.users.clear()
        self.get_user_field_elements()

    # TODO FINISH get Statistics Option
    def get_statistics_option(self):
        """
        Will let you decide whatstatistics you would like to return.
        """
        optiune = str(
            input(
                "Select what you would like to change:  \n"
                "Type           *** a ***           Tell you how much money stolen with app \n"
                "Type           *** d ***           to buy defended attacks \n"
                "Type           *** m ***           main page statistics\n"
            )
        )
        if optiune == "a":
            print(str(get_money_stolen_today()))
            self.roll_on()
        if optiune == "d":
            pass
        if optiune == "a":
            pass

    def roll_on(self):
        """
        Will let you decide if you wanna attack, change the buy options or quit
        """
        self.STILL_ATTACK = True
        answer = str(
            input(
                "What would you like to do? \n"
                "If you type     *** x ***     you will attack. \n"
                "If you type     *** y ***     Search and DESTROY. \n"
                "If you type     *** o ***     you will select options. \n"
                "If you type     *** s ***     you will select Statistics. \n"
                "If you type     *** m ***     Set start position \n"
                "If you type     *** q ***     you will quit the bot!\n"
            )
        )
        while not keyboard.is_pressed("CTRL+SPACE"):
            if answer == "x":
                self.repopulate_users_on_new_page()
                print("You will now start attacking the users!")
                self.attack_users_on_page()
            if answer == "o":
                print("You will now select Options")
                self.preferred_option()
            if answer == "m":
                print("Select what start position you would like")
                self.set_start_position()
                self.roll_on()
            if answer == "s":
                self.get_statistics_option()
                self.roll_on()
            if answer == "y":
                s_and_d = input(
                    "You would like to disable or enable Search and Destroy?"
                )
                if s_and_d == "y":
                    print("You selected Search and destroy")
                    self.search_and_destroy_activated = True
                    self.click_camp_de_lupta()
                    go_to_position = WebDriverWait(driver, 2).until(
                        lambda x: x.find_element_by_xpath(
                            "/html/body/center/p/table/tbody/tr[3]/td/table/tbody/tr/td[2]/table/tbody/"
                            "tr[3]/td/table/tbody/tr[3]/td[1]/input[2]"
                        )
                    )
                    go_to_position.send_keys("1")
                    go_to_position.send_keys(Keys.CONTROL, Keys.ENTER)  # Not duplicate
                    go_to_position.send_keys(Keys.BACK_SPACE)
                    go_to_position.send_keys("250")
                    go_to_position.send_keys(Keys.CONTROL, Keys.ENTER)
                    go_to_position.send_keys(Keys.BACK_SPACE)
                    go_to_position.send_keys(Keys.BACK_SPACE)
                    go_to_position.send_keys(Keys.BACK_SPACE)
                    go_to_position.send_keys("280")
                    go_to_position.send_keys(Keys.CONTROL, Keys.ENTER)
                    go_to_position.send_keys(Keys.BACK_SPACE)
                    go_to_position.send_keys(Keys.BACK_SPACE)
                    go_to_position.send_keys(Keys.BACK_SPACE)
                    # go_to_position.send_keys("350")
                    # go_to_position.send_keys(Keys.CONTROL, Keys.ENTER)
                    # go_to_position.send_keys(Keys.BACK_SPACE)
                    # go_to_position.send_keys(Keys.BACK_SPACE)
                    # go_to_position.send_keys(Keys.BACK_SPACE)
                    self.roll_on()
                else:
                    print("You disabled search and destroy")
                    self.search_and_destroy_activated = False
                    self.roll_on()
            elif answer == "q":
                self.click_log_out_b()
                print("You have logged out!")
                driver.quit()
                global this_will_keep_going
                this_will_keep_going = False
            else:
                print("You must type x or quit")
                self.roll_on()
        else:
            print("SELECT A VALID INPUT")
            self.roll_on()


"""
Here we start to run the BOT.
"""
if __name__ == '__main__':

    this_will_keep_going = True
    run = BotRazboi()
    run.populate_forbidden_users()

    while this_will_keep_going:
        while not keyboard.is_pressed("CTRL+SPACE"):
            run.logg_in()
            try:
                run.click_camp_de_lupta()
                run.get_weapon_cost()
            except TimeoutException:
                run.click_camp_de_lupta()
                run.get_weapon_cost()
            run.default_option()
            run.roll_on()
        else:
            run.click_log_out_b()
            this_will_keep_going = False
            print("this_will_keep_going went FALSE!")

