#BotRazboi


#### This was my first Python project- not complete, not pretty, but worked.
#### Looking now after 1 year on the code, It made me realize how much I learned since then.

An automated Selenium Script to play with visual feedback on command line.
In order to play you will need to create an account on http://www.razboi.ro/

It uses a Selenium and chromedriver to login and interact with the website.
The script will run selenium headless.



The script allow you to login and decide your next actions.
 - Use Search and Destroy.
   - You will provide a limit of money the user can have before being attacked.
   - Provide the number of attacks you wish to spend before stopping
   - After that it will run through the pages between the maximum number fo soldiers 
     that the account have and if any of the users have that amount, it will automatically
     attack and buy weapons depending on the ratio that it is currently selected.
   - In order to simulate human behaviour will take breaks from time to time.

 - Use Automatic attacks on users providing a minimum value of money available on other players.     
 - Select the type of weapons to buy on manual. By default, will buy defence weapons.
 - Check statistics regarding the amount of money stolen.
 - Check statistics regarding account information.
 - Set Start position
