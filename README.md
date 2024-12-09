X4: Foundations - Sector Lister and Map Mover

Hello everyone, I wrote this Python tool to make it easier for modders to move sectors in X: Foundations.

Initial Thoughts:

First of all, thanks to MrBlair29 on Steam for giving me an initial idea: how, where, and what needs to be modified.

So I started with an experiment to scrape out from the galaxy.xml files of the base game and the DLCs using X-Tools.
After checking, I recognized the pattern:

Each Cluster (Sector) has its own:
- Name (Cluster Number, not a real name)
- Position Data in X,Y,Z (Y is not used and always at 0)
- Gate connections which have a specific pattern

Let us check the Base game’s galaxy.xml first:
```
<macro name="XU_EP2_universe_macro" class="galaxy">
```

This line indicates the "Main" folder of the map data. As long as you do not change it in your mod, everything is fine.

More important are these complexes:
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
As you can see, the Cluster which is identified as "connection name" always has the combination of "Cluster_[Number]_connection" and the respective x,y,z coordinates in meters!

First thing to know here, because it’s a hexagonal map pattern, it will always have a grid size of multiples of:

x = 15000000 and z = 8650000 
(x = left/right, z = up/down)

Let us go further and check the gate connections, because each Cluster should at least have one Gate to another Cluster to connect them both.
```
<connection name="ClusterGate001To004" ref="destination" path="../Cluster_01_connection/Cluster_01_Sector001_connection/Zone003_Cluster_01_Sector001_connection/connection_ClusterGate001To004">
        <macro connection="destination" path="../../../../../Cluster_04_connection/Cluster_04_Sector002_connection/Zone001_Cluster_04_Sector002_connection/connection_ClusterGate004To001" />
      </connection>
```
Here you can see the following pattern:

Inside we have:
```
<connection name="ClusterGate001To004">
```
Which indicates the Gate connects Cluster = 001 with 004 and vice versa, of course. In X4 we do not have a direction, so Origin and Destination are the same from the point of perspective you are looking from.

The Path:
```
<macro connection="destination" path="../../../../../Cluster_04_connection/Cluster_04_Sector002_connection/Zone001_Cluster_04_Sector002_connection/connection_ClusterGate004To001" />
```
Is also more important here. This path is a dynamic path which later points the connection between sectors, showing how the engine identifies which Gate is connected with which Gate of the respective Clusters.

Let us now dive into the first tool, the:

Cluster and Gate Mover
![Cluster and Gate Mover](https://github.com/user-attachments/assets/906a4d3c-38a6-4908-bf44-bb8244e29db4)

1. Shows the Cluster, the Cluster name as Number, the respective coordinates, and as a check the "Connection Type," which is normally "galaxy."
2. Load the base game's galaxy.xml by using "3. Load XML Files."
3. You can here select multiple XML files of each DLC and mod too by just selecting them.
4. Let us try to load the base game first only.

![Cluster and Gate Mover_2](https://github.com/user-attachments/assets/38b95859-8da2-4a89-87ba-0f10f7fbecc8)

As you can see, the Base Game's galaxy.xml is now displayed in the respective tables.

1. Here you can directly modify the X,Y,Z coordinates if you directly know where you want to move a Cluster.
2. The second table shows us the Origin and Destination between the Clusters. ---> Here are still some minor problems by using the correct regex pattern to get the real "Link" between them as you can see here:
3. ![Cluster and Gate Mover_3](https://github.com/user-attachments/assets/cb9f9c4b-7940-4ced-ba55-9aea4deeb027)

Most important here is it can cover ca 98% of the base game/DLC connections and also identify correctly the coordinates of each Cluster.

4. Load Overwrite File I will explain later at the end. A few words here: A mod which replaces the specific sectors needs to move one by giving them new coordinates. This overwrite file will check here the Connection Name and apply new x,y,z coordinates when you make changes.

Let us continue with "Save to JSON."
This Button will save all of the loaded XML files as a JSON style (it is more human-readable from my point of view).

After saving, it looks like this:

![json save_1](https://github.com/user-attachments/assets/bd4061f2-7dd9-48a2-a286-059d67233da0)

![json save_2](https://github.com/user-attachments/assets/13053404-4fec-44d2-b80f-f00d88315706)

Let us continue with the next tool:

The Map Drawer
![mapdrawer_1](https://github.com/user-attachments/assets/ed161e36-04b1-47bf-972a-6572e7e7a84f)

The tool starts with a blank white screen and 3 Buttons:

Toggle Coordinates:
- After loading the JSON file created before, we can hide or display the coordinates for better overview.

Load JSON from File:
- Loading your created JSON file from before.

Save JSON to File:
- Saves the file back as a JSON when we modify clusters.

Let us continue by uploading the JSON File.

It looks like this first of all:

![mapdrawer_2](https://github.com/user-attachments/assets/fd2ed163-1d2b-4444-91d3-f90d7946c8c9)

Controls for the Map Drawer:

- Scroll Wheel for zoom.
- Middle Mouse Button hold for dragging the camera.

Let us zoom in:

![mapdrawer_3](https://github.com/user-attachments/assets/669cce7a-d439-4c44-9ef1-f90d42785a42)

As you can see, the clusters are now displayed with the numbers and connections using the green lines between them. Correspondingly, you see also the coordinates, which you can toggle on or off using the button.

Now we want to move a sector here, for people like me who need a graphical overview instead of modifying endless numbers in XML files directly.

The little offset box above the "Toggle Coordinates" is a textbox. (Don’t know why it is offset currently…)

Here you can enter the "EXACT" Cluster Number and confirm afterwards with "Enter" to drag and drop the cluster to a new position.  
To drop a cluster, use the right mouse button on the new position.

The coordinates get updated directly. But keep in mind that you need to stay in the "original grid" pattern. Otherwise, your new Cluster will be displayed in-game with an offset.

Let us move Cluster 28 (most left cluster on the screen) ... far ... far ... away more to the left.

![mapdrawer_4](https://github.com/user-attachments/assets/c5e787c7-4fa4-4499-9e06-1c69bf736bb6)

As you can see, we moved the cluster successfully to a new position and the coordinates are updated directly.

Currently, Bug: The textbox sometimes makes the inserted text invisible when you enter a new Cluster Number. Technically, it’s still working, it’s just a visual glitch somewhere in the pygame-library renderer.

Let us now save the new galaxy as a JSON file using the corresponding button.

The new JSON file looks exactly the same as the one you loaded, but the difference is obvious: the moved Clusters now have new positions.

Last tool: the JSON to XML converter.

This is a super simple, nearly 100-line tool where you basically load your modified JSON file into it and save it back as a specific overwrite galaxy.xml which you can use for your mod.

![xml creator](https://github.com/user-attachments/assets/19cdee91-dcf4-487e-bd68-b01c6d9979a9)

After saving the JSON back to XML, it looks like this:

![xml replacer](https://github.com/user-attachments/assets/b2fa6cc8-a33b-405c-b004-babdb8134751)

As you can see, the creator creates an XML file using a "replace sel" to point to the correct Cluster name and offset the positions. It shows every loaded Cluster, even when you never touched them in the Map Drawer.  
This decision was made because otherwise an additional check would be needed if the loaded coordinates differ from the modified. The game itself doesn’t care if the same coordinates are used for replacement, even when they are the same... they basically "move... but do not move"... you know what I mean.

Afterwards, you can go back to the first tool to upload the overwrite XML, which basically uses your modified positions.

And that’s it. The rest is simple for modders:  

Create a content.xml file, use your new replacement "galaxy.xml" for it, and move freely any cluster.

---

Additional Notes Which Are Very Important:

Currently "Supported" Mods which can be loaded using the galaxy.xml files:

- X Universe + (as of 7.0) --> nearly 99% supported --> I think I caught all the connection gates because they are well-structured. J.L made a very good mod because he started something around with 4xx as cluster numbers... there is enough "space" between original and modded.
- Add More Sectors: 80% Supported... same issue here... more complex because the modder used always different prefixes... and capital... lower letters... which makes the identification of all this "Non-Conform structure" nearly impossible to get all the gate connections. (Honestly dude, I like your mod but... why????)
- Sector: The Deep --> As far as I see, it’s just normally loaded.
- Farnham’s Legend: Sadly same situation... the prefix is a UUID Number.... and honestly, just for this one, I do not write custom logic... just for displaying the gate.

For all modders:

I will more or less not add any exception logic.  
Which means... If you name your Cluster like "Mysupercrazypower_cLuster09,"  
like from Add More Sectors:

![sectors don't](https://github.com/user-attachments/assets/280ec4d8-52de-4a63-9e41-0a0ef11239e0)

I will not make extra logic only to recognize your "custom prefix." I did this for Add More Sectors but only because this mod and the mod X Universe + add a lot of nice clusters to the game, where 6 of them overlapped and they also created a "spaghetti-verse."

---

That’s it, and to prove that my galaxy is looking totally different now from yours, here is an example of how my galaxy is currently looking:

![galaxy proof 1](https://github.com/user-attachments/assets/db0b8495-2168-4de7-81a1-08fd3bd254e5)
![galaxy proof 2](https://github.com/user-attachments/assets/6f7660e9-066e-4042-8a87-e17f83890562)


