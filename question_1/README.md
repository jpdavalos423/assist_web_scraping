# **Question 1:** Which UC appears to add the most required courses when added to any pairing, and how consistent is this across different community college districts?

To answer this question we have divided it up into two sections and have two different visualizations. 

First we will be explaining the concept of the 3-UC combination sequences

## 3-UC Combination Sequences
We analyzed 3-UC combination in order-dependent sequences (e.g., [UCSD, UCLA, UCSD]). In each 3-UC sequence, the first UC covers as many requirements as possible, the second only contributes courses not already fulfilled, and the third adds anything that is still unmet. This reveals how much each UC contributes when added to an existing pair.​

## Folders and what's inside:

**data_txts**
This is where the data we developed that is in txt form is stored.

**graphs**
This is where all the graphs/visualizations we developed is stored.

**order_csvs**
This is where all the csvs of each order is stored.

**scripts_for_data**
This is where the scripts to create the data_txts and order_csvs is stored.

**scripts_for_graphs**
This is where all the scripts to create the graphs is stored.

## What's inside each folder and what they do:

### data_txts
#### average_combination_order.txt
For each of the 3-UC combination sequences, this txt file stores the average number of courses for each Community College District (CCD) in California for each of the UCs. At the end it has the total average for all the CCDs along with the total average only considering CCDs that are transferrable (meaning all requirements can be met through courses at that CCD).

#### total_combination_order.txt
Similarly to the average_combination_order.txt this is the same except it just the raw total instead of the averages. At the end There is the total number of courses and the average found by the total divided by the number of CCDs.

#### untransferrable_ccs.txt
Shows the which UCs for each of the CCDs that are impossible to transfer to.

### graphs
#### heat_maps_per_order
This is a folder filled with heat maps for each of the orders of the 3-UC combination sequences. Each one showcases the number of average courses per CCD to transfer to each UC. The darker the color the more courses it takes to fufill the requirements. The boxes that are red are the ones where it is impossible to transfer to that UC from that CC due to unfullfilled requirements.

#### grouped_bar_transferable_averages_by_uc.png
This graph visually shows the averges for each of the UCs when they are 1st, 2nd, and 3rd in the 3-UC combination sequences. This showcases which UC contributes to the most and least additional courses.

#### untransferrable_districts.png
This graph shows the number of CCDs are impossible to tranfer to a particular UC.

### order_csvs
This folder contains 3 csvs (1 per order) of each of the CCDs (as the rows) and the UCs (as the columns) both articulated and unarticulated. At the bottom is the average both everything together and after filtering out the CCDs that are impossible to transfer from.

### scripts_for_data
#### per_cc.py
This script would output a txt file of all the singular combinations for a singular CCD after the path to file is updated.

#### total_combination_order.py
This script outputs a bunch of the data such as the 3 order csv files, average_combination_order.txt, total_combination_order.txt, and untransferrable_ccs.txt.

### scripts for graphs
#### grouped_bar_graph.py
This script creates the graph titled grouped_bar_transferable_averages_by_uc.png.

#### heat_map_transferrable_ccs.py
This script creates all 3 heat maps for each order.

#### untransferrable_ccs.py
This script creates untransferrable_districts.png.
