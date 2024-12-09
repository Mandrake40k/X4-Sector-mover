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







