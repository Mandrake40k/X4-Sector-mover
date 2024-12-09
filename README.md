X4: Foundations - Sector Lister and Map Mover


Hello everyone, I wrote this Python tools to make it easier for modders to move sectors in X: Foudantions

Inital Thoughts:

First of all thanks to MrBlair29 on Steam to give me an inital idea: how, where and waht needs to be modified.

So I started with an experiemnt to scrape out from the galaxy.xml files of the base game and the DLC´S using X-Tools.
After checking I recognized the pattern


Each CLuster (Sector) have an own:
- name (Cluster Number, no real name)
- Postion Data in X,Y,Z ( Y is not used and always at 0)
- Gate connections which have a specific pattern


Let us check the Base game´s glaaxy.xml first

```
<macro name="XU_EP2_universe_macro" class="galaxy">

```

This Line indicates the "Main" Folder of the map data, as long you not chaning it it in your Mod, everything is fine.


More important are this complexes:

```
<connections>
      <connection name="Cluster_01_connection" ref="clusters">
        <macro ref="Cluster_01_macro" connection="galaxy" />
      </connection>
      <connection name="Cluster_02_connection" ref="clusters">
        <offset>
          <position x="15000000" y="0" z="25980000" />
        </offset>
        <macro ref="Cluster_02_macro" connection="galaxy" />
      </connection>

```

As you can see the Cluster which is identified as "connection name" have always the combination of "Cluster_```[Number]```_connection
and the respective x,y,z coordinates in meter!

First thing to know here, because its an hexagonal mappattern it will always have a grid size of multiples of:

x = 15000000 and z = 8650000 
(x = left/right , z = up/down)


Let us go further and checking thegate connections, ebcause each Cluster should at least have one Gate to anotehr Cluster to necte them both.

```
<connection name="ClusterGate001To004" ref="destination" path="../Cluster_01_connection/Cluster_01_Sector001_connection/Zone003_Cluster_01_Sector001_connection/connection_ClusterGate001To004">
        <macro connection="destination" path="../../../../../Cluster_04_connection/Cluster_04_Sector002_connection/Zone001_Cluster_04_Sector002_connection/connection_ClusterGate004To001" />
      </connection>
```


Here yo ucan see following pattern:

Inside we have:
```
<connection name="ClusterGate001To004"
```

Which indicates the Gate connects Cluster = 001 with 004 and vice versa of course. In X4 we do not have a directions, so Origin and Destianation are the same from the point of perspeccive you looking from.


The Path:
```
<macro connection="destination" path="../../../../../Cluster_04_connection/Cluster_04_Sector002_connection/Zone001_Cluster_04_Sector002_connection/connection_ClusterGate004To001" /
```

Is also here more important, this path is a dnyamic path which later points the connection betweeen sectors, how the engine identifies which Gate is connected whith which gate of the respective Clusters




Let us now dive in to the first tool, the:

Cluster and gate Mover
![Cluster adn Gate Mover](https://github.com/user-attachments/assets/906a4d3c-38a6-4908-bf44-bb8244e29db4)

1. Shows the Cluster , the Cluster name as Number, the respective coordiantes, and as check the "Connection Type" which is normally "galaxy". Let us now laod the base games galaxy.xml by using "3. Load XML Files
2. Cou can here Seelct multiple xml files of each dlc and mod too by jsut selecting them.
3. Let us try to laod the base game first only.

![Cluster and Gate Mover_2](https://github.com/user-attachments/assets/38b95859-8da2-4a89-87ba-0f10f7fbecc8)


As you can see the Base Games galaxy.xml is now dispalyed in the respective tables.

1. here you can directly modifiy the  X,Y,Z coordiantes if directly know where you wanna move a Cluster.
2. The second table shows us the Origin and destiantion betwewen the Clusters ---> here are still some minor problems by using the correct regex patter, to get the real "Link" between them as yo ucan see here:
3. ![Cluster and Gate Mover_3](https://github.com/user-attachments/assets/cb9f9c4b-7940-4ced-ba55-9aea4deeb027)


Most importannt here is it can cover ca 98% of the basegame/DLC connections. and also that we identify correctly the coordiantes of each cluster.

4. Load Overwrite FIle I will explain Later at the end. One few words here: A Mod which replace the specific sectors needs to move one by giving them new coordiantes. this overwrite file will check here the Conenction Name and apply new x,y,z coordinates when you amde changes.


Let us continue with "Save to JSON"
This Button will save all of the loaded xml files as a json style (it is more human readable from my point of view).

After Saving it looks like this:

![json save_1](https://github.com/user-attachments/assets/bd4061f2-7dd9-48a2-a286-059d67233da0)

![json save_2](https://github.com/user-attachments/assets/13053404-4fec-44d2-b80f-f00d88315706)



let us Continue with the next Tool:

The Map Drawer
![mapdrawer_1](https://github.com/user-attachments/assets/ed161e36-04b1-47bf-972a-6572e7e7a84f)

The Tool starts with a blank white screen and 3 Buttons:

Toggle Coordiantes:
- After laoding the json file which we created before we can hide or displaythe coordiantes for a better overview

  
Load JSON from File:
- Loading your created json filefrom before

Save JSON to FIle
- Saves the File back also into a JSON when we modfiy here Clusters


let us continue by uploading the JSON File

I tlooks liek this first of all:

![mapdrawer_2](https://github.com/user-attachments/assets/fd2ed163-1d2b-4444-91d3-f90d7946c8c9)


Controls for the Map Drawer:

- Scroll Wheel for zoom
- Middle Mouse Button hold for dragging the camera

Let us Zoom in:

![mapdrawer_3](https://github.com/user-attachments/assets/669cce7a-d439-4c44-9ef1-f90d42785a42)

As you can see the Clusters are now displayed with the Numbers and conenctions using the green lines between them, corresponding to this you see also the coordiantes which you can toggle on or off using the button.

Now we wanna move a sector here for people like me who need a graphically overview instead of modifiying endless numbers in XML files directly.


The Little ofsetted Box above the "Toggle Coordiantes" is a textbox. (Dont know why it is ofsettet currently... )

Here you can enter the "EXACT" CLuster Number and confirm afterwards with "Enter" todrag and drop thecluster to a new postion.
To Drop a cluster, use the right mousebutton on the new postion.

The coorinates getting updated directly. But keep in mind that you need to stay in the "originally grod" pattern. Otehrwise your new Cluster will be dispalyed in game with an offset.


Let us Move Cluster 28 (Most left cluster on the screen) .... far ... far... away more to the left.

![mapdrawer_4](https://github.com/user-attachments/assets/c5e787c7-4fa4-4499-9e06-1c69bf736bb6)

As youcan see, we moved sucessfully the cluster to a new position and the coordiantes are updated directly.

Currently Bug: The Textbox sometimes makes the inserted text invisible when you enter a new Cluster Number.... technically its still working... its jsut a visually glitch somewhere in thepygame-library renderer... .


Let us now save the new galaxy as jsonfile Using the corresponding button.

The new json file looks exactly thes ame like which you loaded, but the difference is obvious: The Moved CLusters have now new postions.



Last tool the json to XML converter


This is a super simple nearly 100 lines tool where you basically load your modified json file in it and save it back as a specific overwrite galaxy.xml which you can use for your mod
![xml creater](https://github.com/user-attachments/assets/19cdee91-dcf4-487e-bd68-b01c6d9979a9)


After savingthe json back to an xml it looks like this:

![xml replacer](https://github.com/user-attachments/assets/b2fa6cc8-a33b-405c-b004-babdb8134751)

As yo ucan see creator creates a xml file using a "replace sel" to point to thecorrect Cluster name and offset the postions. It shows every loaded CLuster, even when you never touched them in themap drawer.
Thsi decision i made ebcause otehrwise anaddional check up if the loaded coordinates differs from the modified. Thegame itself does ntocare about it if he same coordinates are used for replacement even when they are thesame... the basically "move... but do not move" ... you knwo what I mean.




Afterwards you can go back in the First tool.

To uplaoded the overwrite xml which basically uses your modificated positions.



And thats it. The rest is simple for modders:

Create a content.xml file use your new repalcement "galaxy.xml" for it. and move free ley any cluster.





Addional Notes WHich are very importannt


Currently "Supported" Mods which can be laoded using the galaxy.xml files:

- X Universe +/ as of 7.0  --> nearly 99% suported --> I think I catched all the connectiongates because they are well strucurized J.L made a very good mod becuase he started something around with 4xx as cluster numbers... there is enough "space" between original and modded"
- Add More Sectors 80% Supported... same issue here... More complex... because the mooder used always different prefixes...and capital... lower letters... which makes the identifation of all this "Non-Conform structure"... nearly impossible to get all the gae connections. (Hoenstly dude. I like you mod but...why????)
- Sector: The Deep --> As far As I see its jsut normally loaded
- Farnhams Legend. sadly same situation... the prefix is a UUID Number.... and honestly jsut for this one I do not write an own logic... just for dispalxing the gate... .


For all modders:

I will more or less not add any exception logic.

Which means... If you name your CLuster like "Mysupercrazypower_cLuster09"

like from Add more sectors:

![sectos dont](https://github.com/user-attachments/assets/280ec4d8-52de-4a63-9e41-0a0ef11239e0)

I will not make extra logics only do recongize your "custom prefx" I did this for Add more sectors but only becuase this mod and the mod X Universe + add a lot of nice clusters to thegame, where 6 of them overlapped and they also created a "spagehtti-verse"



Thats it, and to prove that my  galaxy is looking totally different now from yours here an example how my galaxy is currently looking:


![galaxy prove1](https://github.com/user-attachments/assets/db0b8495-2168-4de7-81a1-08fd3bd254e5)
![galaxy prove2](https://github.com/user-attachments/assets/6f7660e9-066e-4042-8a87-e17f83890562)

















