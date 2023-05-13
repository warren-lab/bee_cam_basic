# Running some peripherals using fuel_gage current load



* found that charging rate is increasing but it is still negative....
*
-----
12/6/2023

* It looks like using the .reset() command once for the MAX17048 fuel gauge helped in resetting the calibration.
* Also seems like when there is higher load we will see more changes in the charging rate which is good so it will be negative which is assumed

* When load on battery is .02A or more then behavior seems to be more normal. However, when the system is idle there is a bit more inaccuracy it seems. There is a clear decrease in the battery voltage and charging rate when it is subjected to a higher load of the system during imaging. which entails .022A

- - - - 

Now when testing the charging capabilities after doing the reset it was tested that the battery ahd a voltage of 3.87v, and a state of 55%, after originally being around 3.9v and a state of 67%. With the low load it does seem to get confused when idle on whether or not it is charging sothe attery state might not be as accurate...


Okay so to test charging we had the above charactersitcs of the batter. We then added the power directly instead of trying to power down and then do the process over... 
* So after plugging in the wall power what we found is that there was a large increase in positive charge rate and the battery voltage also increased a lot to be in 4.xx range from 3.87. This is really inteeresting to see. 



-----
12/7/2023

* did another test by running the fuel gauge script on the original fuel gauge that has been reset on 12/6/2023 for 10 min.
    - After doing this we say that it had a stable votlage of 3.9v, and battery state of roughly 64.4 with it only decreasing slightly
* So after that we then ran the control script to increase the load on the battery for 10 minutes.
    - After doing this the voltage was 3.82 and battery state was 61.1

* We then let the pi idle for 10 min and recorded the stable voltage and battery state
    - After this time it was found that the voltage was 3.88 and battery state was 61.1

* Then we plugged in the wall power to the solar charger in order to charge the battery this was left for ~30 min
    - After this time the voltage and battery state were recorded as 4.14 and 80.7% respectively

* Finally we let the pi idel again for 30 min and recorded the stable volt and battery state after
    - Voltage and battery state were 3.9 and 75.5 respectively

So from this experiment the battery started at voltage of X and battery percentage of X, and then when subjected to the 10 min imaging experiment dropped the battery percentage to X and voltage to X, which was verified by running the fuel gauge script for when the pi was on idle for 10 min which say a voltage of X and battery state of X

Then we attempted tpo charge the battey up from this current state by pliugging in the wall power supply. This led to a ___ in the battery state/percentage to X and the voltage was X. This was verfied by running the fuel gauge script on idle and after 10 min the voltage and battery states were X and X which shows....

NEED TO DO ANTOHER FULL TEST TO SEE HOW MUCH THE BATTERY GETS CHARGED!!!