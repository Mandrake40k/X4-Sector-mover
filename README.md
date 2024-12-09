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
